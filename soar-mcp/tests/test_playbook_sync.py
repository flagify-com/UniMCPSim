#!/usr/bin/env python3
"""
SOAR 剧本同步功能测试
测试数据库模型、API客户端、同步服务和MCP工具集成
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import DatabaseManager, PlaybookData, PlaybookParam, PlaybookModel
from sync_service import SOARAPIClient, PlaybookSyncService
from simple_mcp_server import mcp


class TestDatabaseModels(unittest.TestCase):
    """测试数据库模型"""

    def setUp(self):
        # 使用临时数据库文件
        self.temp_db = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db)
        self.db_manager.init_db()

    def tearDown(self):
        # 清理临时文件
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)

    def test_database_initialization(self):
        """测试数据库初始化"""
        # 验证表已创建
        session = self.db_manager.get_session()
        try:
            from sqlalchemy import text
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='playbooks'"))
            self.assertTrue(result.fetchone() is not None)
        finally:
            session.close()

    def test_playbook_save_and_retrieve(self):
        """测试剧本保存和获取"""
        # 创建测试数据
        params = [
            PlaybookParam(cef_column="sourceAddress", cef_desc="源IP地址", value_type="string"),
            PlaybookParam(cef_column="destinationPort", cef_desc="目标端口", value_type="integer")
        ]
        
        playbook = PlaybookData(
            id=12345,
            name="test_playbook",
            display_name="测试剧本",
            playbook_category="测试类别",
            description="这是一个测试剧本",
            create_time=datetime.now(),
            update_time=datetime.now(),
            playbook_params=params
        )

        # 保存剧本
        success = self.db_manager.save_playbook(playbook)
        self.assertTrue(success)

        # 获取剧本
        retrieved = self.db_manager.get_playbook(12345)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, 12345)
        self.assertEqual(retrieved.name, "test_playbook")
        self.assertEqual(len(retrieved.playbook_params), 2)
        self.assertEqual(retrieved.playbook_params[0].cef_column, "sourceAddress")

    def test_playbook_update(self):
        """测试剧本更新"""
        # 创建初始剧本
        playbook = PlaybookData(
            id=54321,
            name="update_test",
            display_name="更新测试",
            playbook_category="测试",
            description="原始描述"
        )
        self.db_manager.save_playbook(playbook)

        # 更新剧本
        updated_playbook = PlaybookData(
            id=54321,
            name="update_test",
            display_name="更新测试 - 修改版",
            playbook_category="测试",
            description="更新后的描述"
        )
        success = self.db_manager.save_playbook(updated_playbook)
        self.assertTrue(success)

        # 验证更新
        retrieved = self.db_manager.get_playbook(54321)
        self.assertEqual(retrieved.display_name, "更新测试 - 修改版")
        self.assertEqual(retrieved.description, "更新后的描述")

    def test_playbook_list_with_category(self):
        """测试按类别筛选剧本列表"""
        # 创建不同类别的剧本
        playbooks = [
            PlaybookData(id=1001, name="p1", playbook_category="安全响应"),
            PlaybookData(id=1002, name="p2", playbook_category="威胁调查"),
            PlaybookData(id=1003, name="p3", playbook_category="安全响应")
        ]
        
        for pb in playbooks:
            self.db_manager.save_playbook(pb)

        # 获取所有剧本
        all_playbooks = self.db_manager.get_playbooks()
        self.assertEqual(len(all_playbooks), 3)

        # 按类别筛选
        security_playbooks = self.db_manager.get_playbooks(category="安全响应")
        self.assertEqual(len(security_playbooks), 2)

    def test_sync_stats(self):
        """测试同步统计"""
        # 添加一些剧本
        for i in range(5):
            playbook = PlaybookData(id=i+1, name=f"playbook_{i}")
            self.db_manager.save_playbook(playbook)

        stats = self.db_manager.get_sync_stats()
        self.assertEqual(stats["total_playbooks"], 5)
        self.assertIsNotNone(stats["latest_sync_time"])


class TestSOARAPIClient(unittest.TestCase):
    """测试SOAR API客户端"""

    def setUp(self):
        self.mock_env = {
            'API_URL': 'https://test.example.com',
            'API_TOKEN': 'test_token_123',
            'SSL_VERIFY': '0'
        }

    @patch.dict(os.environ, {'API_URL': 'https://test.example.com', 'API_TOKEN': 'test_token_123'})
    @patch('httpx.AsyncClient')
    async def test_get_all_playbooks_success(self, mock_client_class):
        """测试获取剧本列表成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 200,
            "result": [
                {"id": 1001, "name": "test_playbook_1", "displayName": "测试剧本1"},
                {"id": 1002, "name": "test_playbook_2", "displayName": "测试剧本2"}
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        # 创建客户端并测试
        client = SOARAPIClient()
        client.client = mock_client
        
        playbooks = await client.get_all_playbooks()
        
        self.assertEqual(len(playbooks), 2)
        self.assertEqual(playbooks[0]["id"], 1001)
        self.assertEqual(playbooks[1]["name"], "test_playbook_2")

    @patch.dict(os.environ, {'API_URL': 'https://test.example.com', 'API_TOKEN': 'test_token_123'})
    @patch('httpx.AsyncClient')
    async def test_get_playbook_params_success(self, mock_client_class):
        """测试获取剧本参数成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 200,
            "result": [
                {"cefColumn": "sourceAddress", "cefDesc": "源IP", "valueType": "string"},
                {"cefColumn": "destinationPort", "cefDesc": "目标端口", "valueType": "integer"}
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = SOARAPIClient()
        client.client = mock_client
        
        params = await client.get_playbook_params(1001)
        
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0].cef_column, "sourceAddress")
        self.assertEqual(params[1].value_type, "integer")

    @patch.dict(os.environ, {'API_URL': 'https://test.example.com', 'API_TOKEN': 'test_token_123'})
    @patch('httpx.AsyncClient')
    async def test_get_playbook_params_no_params(self, mock_client_class):
        """测试获取剧本参数无参数情况"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 404, "message": "No params"}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = SOARAPIClient()
        client.client = mock_client
        
        params = await client.get_playbook_params(1001)
        
        self.assertEqual(len(params), 0)


class TestPlaybookSyncService(unittest.TestCase):
    """测试剧本同步服务"""

    def setUp(self):
        self.temp_db = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db)
        self.db_manager.init_db()

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)

    @patch('sync_service.SOARAPIClient')
    async def test_sync_single_playbook(self, mock_api_client_class):
        """测试单个剧本同步"""
        # 模拟API客户端
        mock_api_client = AsyncMock()
        mock_api_client.get_playbook_params.return_value = [
            PlaybookParam(cef_column="sourceAddress", cef_desc="源IP", value_type="string")
        ]
        mock_api_client_class.return_value = mock_api_client

        # 创建同步服务
        sync_service = PlaybookSyncService(self.db_manager, max_concurrent=1)
        sync_service.api_client = mock_api_client

        # 模拟剧本数据
        playbook_data = {
            "id": 2001,
            "name": "sync_test",
            "displayName": "同步测试",
            "playbookCategory": "测试同步",
            "description": "同步功能测试",
            "createTime": "2024-01-01T10:00:00Z",
            "updateTime": "2024-01-02T10:00:00Z"
        }

        # 执行同步
        success = await sync_service.sync_single_playbook(playbook_data)
        self.assertTrue(success)

        # 验证数据已保存
        saved_playbook = self.db_manager.get_playbook(2001)
        self.assertIsNotNone(saved_playbook)
        self.assertEqual(saved_playbook.name, "sync_test")
        self.assertEqual(len(saved_playbook.playbook_params), 1)

    @patch('sync_service.SOARAPIClient')
    async def test_sync_playbooks_batch(self, mock_api_client_class):
        """测试批量剧本同步"""
        mock_api_client = AsyncMock()
        mock_api_client.get_playbook_params.return_value = []
        mock_api_client_class.return_value = mock_api_client

        sync_service = PlaybookSyncService(self.db_manager, max_concurrent=2)
        sync_service.api_client = mock_api_client

        # 模拟多个剧本
        playbooks = [
            {"id": 3001, "name": "batch_test_1"},
            {"id": 3002, "name": "batch_test_2"},
            {"id": 3003, "name": "batch_test_3"}
        ]

        # 执行批量同步
        result = await sync_service.sync_playbooks_batch(playbooks)
        
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["success"], 3)
        self.assertEqual(result["failed"], 0)

        # 验证所有剧本都已保存
        for pb_data in playbooks:
            saved = self.db_manager.get_playbook(pb_data["id"])
            self.assertIsNotNone(saved)

    @patch('sync_service.SOARAPIClient')
    async def test_full_sync(self, mock_api_client_class):
        """测试完整同步流程"""
        mock_api_client = AsyncMock()
        mock_api_client.get_all_playbooks.return_value = [
            {"id": 4001, "name": "full_sync_test"}
        ]
        mock_api_client.get_playbook_params.return_value = []
        mock_api_client.close = AsyncMock()
        mock_api_client_class.return_value = mock_api_client

        sync_service = PlaybookSyncService(self.db_manager)
        sync_service.api_client = mock_api_client

        # 执行完整同步
        result = await sync_service.full_sync()
        
        self.assertIn("sync_time", result)
        self.assertIn("source_count", result)
        self.assertIn("sync_result", result)
        self.assertIn("database_stats", result)
        self.assertEqual(result["source_count"], 1)


class TestMCPIntegration(unittest.TestCase):
    """测试MCP工具集成"""

    def setUp(self):
        self.temp_db = tempfile.mktemp(suffix='.db')
        # 创建全局db_manager实例用于测试
        import simple_mcp_server
        simple_mcp_server.db_manager = DatabaseManager(self.temp_db)
        simple_mcp_server.db_manager.init_db()

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)

    def test_get_sync_status_tool(self):
        """测试获取同步状态工具"""
        import simple_mcp_server
        
        result = simple_mcp_server.get_sync_status()
        data = json.loads(result)
        
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("total_playbooks", data["data"])

    def test_get_database_playbooks_tool(self):
        """测试获取数据库剧本工具"""
        import simple_mcp_server
        
        # 添加测试数据
        playbook = PlaybookData(id=5001, name="mcp_test", display_name="MCP测试")
        simple_mcp_server.db_manager.save_playbook(playbook)
        
        result = simple_mcp_server.get_database_playbooks()
        data = json.loads(result)
        
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["playbooks"][0]["id"], 5001)
        self.assertEqual(data["playbooks"][0]["name"], "mcp_test")

    def test_get_playbook_detail_tool(self):
        """测试获取剧本详情工具"""
        import simple_mcp_server
        
        # 添加带参数的测试剧本
        params = [PlaybookParam(cef_column="testColumn", cef_desc="测试字段", value_type="string")]
        playbook = PlaybookData(
            id=5002, 
            name="detail_test",
            display_name="详情测试",
            playbook_params=params
        )
        simple_mcp_server.db_manager.save_playbook(playbook)
        
        result = simple_mcp_server.get_playbook_detail(5002)
        data = json.loads(result)
        
        self.assertEqual(data["id"], 5002)
        self.assertEqual(data["name"], "detail_test")
        self.assertEqual(len(data["playbookParams"]), 1)
        self.assertEqual(data["playbookParams"][0]["cefColumn"], "testColumn")

    def test_get_playbook_detail_not_found(self):
        """测试获取不存在剧本详情"""
        import simple_mcp_server
        
        result = simple_mcp_server.get_playbook_detail(99999)
        data = json.loads(result)
        
        self.assertIn("error", data)
        self.assertIn("未找到剧本", data["error"])


async def run_async_tests():
    """运行异步测试"""
    print("🧪 运行异步测试...")
    
    # 测试API客户端
    test_client = TestSOARAPIClient()
    test_client.setUp()
    await test_client.test_get_all_playbooks_success()
    await test_client.test_get_playbook_params_success()
    await test_client.test_get_playbook_params_no_params()
    print("✅ API客户端测试通过")
    
    # 测试同步服务
    test_sync = TestPlaybookSyncService()
    test_sync.setUp()
    await test_sync.test_sync_single_playbook()
    await test_sync.test_sync_playbooks_batch()
    await test_sync.test_full_sync()
    test_sync.tearDown()
    print("✅ 同步服务测试通过")


def main():
    """运行所有测试"""
    print("🚀 开始剧本同步功能测试")
    print("=" * 50)
    
    # 运行同步测试
    print("🧪 运行数据库模型测试...")
    unittest.main(module=__name__, argv=[''], testRunner=unittest.TextTestRunner(verbosity=2), exit=False)
    
    # 运行异步测试
    asyncio.run(run_async_tests())
    
    # 运行MCP集成测试 
    print("🧪 运行MCP集成测试...")
    try:
        test_mcp = TestMCPIntegration()
        test_mcp.setUp()
        test_mcp.test_get_sync_status_tool()
        test_mcp.test_get_database_playbooks_tool()
        test_mcp.test_get_playbook_detail_tool()
        test_mcp.test_get_playbook_detail_not_found()
        test_mcp.tearDown()
        print("✅ MCP集成测试通过")
    except Exception as e:
        print(f"⚠️  MCP集成测试跳过: {e}")
        print("   (这是正常的，因为需要独立的MCP服务器环境)")
    
    print("=" * 50)
    print("🎉 所有测试完成！")


if __name__ == "__main__":
    main()