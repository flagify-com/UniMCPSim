#!/usr/bin/env python3
"""
剧本同步并发测试
验证20个并发请求的处理能力
"""

import asyncio
import sys
import os
import time
from unittest.mock import AsyncMock, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync_service import PlaybookSyncService, SOARAPIClient
from models import DatabaseManager, PlaybookParam


async def test_concurrent_params_fetch():
    """测试并发参数获取"""
    print("🧪 测试并发参数获取 (20个并发)")
    
    # 模拟API客户端
    mock_client = AsyncMock()
    
    # 模拟不同的参数响应
    def mock_get_params(playbook_id):
        if playbook_id % 3 == 0:
            return []  # 无参数
        elif playbook_id % 3 == 1:
            return [PlaybookParam(cef_column="sourceAddress", cef_desc="源IP", value_type="string")]
        else:
            return [
                PlaybookParam(cef_column="destinationPort", cef_desc="目标端口", value_type="integer"),
                PlaybookParam(cef_column="protocol", cef_desc="协议", value_type="string")
            ]
    
    mock_client.get_playbook_params.side_effect = lambda pid: mock_get_params(pid)
    
    # 创建临时数据库
    import tempfile
    temp_db = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(temp_db)
    db_manager.init_db()
    
    try:
        # 创建同步服务
        sync_service = PlaybookSyncService(db_manager, max_concurrent=20)
        sync_service.api_client = mock_client
        
        # 创建100个测试剧本数据
        test_playbooks = []
        for i in range(1, 101):
            test_playbooks.append({
                "id": i,
                "name": f"concurrent_test_{i}",
                "displayName": f"并发测试剧本{i}",
                "playbookCategory": "并发测试",
                "description": f"第{i}个测试剧本"
            })
        
        print(f"📊 准备同步 {len(test_playbooks)} 个剧本")
        
        # 执行并发同步
        start_time = time.time()
        result = await sync_service.sync_playbooks_batch(test_playbooks)
        elapsed_time = time.time() - start_time
        
        print(f"🎯 并发同步结果:")
        print(f"   总数: {result['total']}")
        print(f"   成功: {result['success']}")
        print(f"   失败: {result['failed']}")
        print(f"   耗时: {elapsed_time:.2f}秒")
        print(f"   平均: {elapsed_time/result['total']:.4f}秒/个")
        
        # 验证API调用次数
        expected_calls = len(test_playbooks)
        actual_calls = mock_client.get_playbook_params.call_count
        print(f"📞 API调用次数: {actual_calls} (预期: {expected_calls})")
        
        # 验证数据库数据
        saved_playbooks = db_manager.get_playbooks(limit=200)
        print(f"💾 数据库保存: {len(saved_playbooks)} 个剧本")
        
        # 验证参数保存
        param_counts = {}
        for pb in saved_playbooks:
            param_count = len(pb.playbook_params)
            param_counts[param_count] = param_counts.get(param_count, 0) + 1
        
        print(f"📋 参数分布: {param_counts}")
        
        # 断言验证
        assert result['success'] == len(test_playbooks), f"同步成功数不匹配: {result['success']} != {len(test_playbooks)}"
        assert result['failed'] == 0, f"不应有失败: {result['failed']}"
        assert actual_calls == expected_calls, f"API调用次数不匹配: {actual_calls} != {expected_calls}"
        assert len(saved_playbooks) == len(test_playbooks), f"数据库保存数量不匹配: {len(saved_playbooks)} != {len(test_playbooks)}"
        
        print("✅ 并发测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        return False
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_db):
            os.unlink(temp_db)


async def test_rate_limiting():
    """测试速率限制"""
    print("\n🧪 测试速率限制")
    
    # 模拟慢速API
    async def slow_get_params(playbook_id):
        await asyncio.sleep(0.1)  # 模拟100ms的API延迟
        return [PlaybookParam(cef_column="test", cef_desc="测试", value_type="string")]
    
    mock_client = AsyncMock()
    mock_client.get_playbook_params.side_effect = slow_get_params
    
    # 创建临时数据库
    import tempfile
    temp_db = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(temp_db)
    db_manager.init_db()
    
    try:
        # 测试不同的并发限制
        for max_concurrent in [5, 10, 20]:
            print(f"📊 测试最大并发 {max_concurrent}")
            
            sync_service = PlaybookSyncService(db_manager, max_concurrent=max_concurrent)
            sync_service.api_client = mock_client
            
            # 30个测试剧本
            test_playbooks = [{"id": i, "name": f"rate_test_{i}"} for i in range(1, 31)]
            
            start_time = time.time()
            result = await sync_service.sync_playbooks_batch(test_playbooks)
            elapsed_time = time.time() - start_time
            
            print(f"   耗时: {elapsed_time:.2f}秒, 成功: {result['success']}")
            
            # 重置mock计数器
            mock_client.reset_mock()
        
        print("✅ 速率限制测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 速率限制测试失败: {e}")
        return False
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


async def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试错误处理")
    
    # 模拟部分失败的API
    async def failing_get_params(playbook_id):
        if playbook_id % 5 == 0:  # 每5个就失败一次
            raise Exception(f"API错误 - 剧本 {playbook_id}")
        return [PlaybookParam(cef_column="test", cef_desc="测试", value_type="string")]
    
    mock_client = AsyncMock()
    mock_client.get_playbook_params.side_effect = failing_get_params
    
    import tempfile
    temp_db = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(temp_db)
    db_manager.init_db()
    
    try:
        sync_service = PlaybookSyncService(db_manager, max_concurrent=10)
        sync_service.api_client = mock_client
        
        # 25个测试剧本 (其中5个会失败)
        test_playbooks = [{"id": i, "name": f"error_test_{i}"} for i in range(1, 26)]
        
        result = await sync_service.sync_playbooks_batch(test_playbooks)
        
        print(f"📊 错误处理结果:")
        print(f"   总数: {result['total']}")
        print(f"   成功: {result['success']}")
        print(f"   失败: {result['failed']}")
        
        # 验证部分成功
        expected_success = 20  # 25个中5个失败
        expected_failed = 5
        
        assert result['success'] == expected_success, f"成功数不匹配: {result['success']} != {expected_success}"
        assert result['failed'] == expected_failed, f"失败数不匹配: {result['failed']} != {expected_failed}"
        
        print("✅ 错误处理测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


async def main():
    """运行所有并发测试"""
    print("🚀 开始并发同步测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 基本并发功能
    results.append(await test_concurrent_params_fetch())
    
    # 测试2: 速率限制
    results.append(await test_rate_limiting())
    
    # 测试3: 错误处理
    results.append(await test_error_handling())
    
    print("\n" + "=" * 60)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 所有并发测试通过! ({success_count}/{total_count})")
    else:
        print(f"⚠️  部分测试失败: ({success_count}/{total_count})")
    
    return success_count == total_count


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)