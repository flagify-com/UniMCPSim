#!/usr/bin/env python3
"""测试管理API功能"""

from models import DatabaseManager
import traceback

def test_get_playbooks_admin():
    """测试获取剧本管理列表"""
    print("🔍 测试获取剧本管理列表...")
    
    try:
        db = DatabaseManager()
        
        # 测试获取所有剧本
        playbooks = db.get_playbooks_admin()
        print(f"📊 总共返回 {len(playbooks)} 个剧本")
        
        if playbooks:
            print("📋 前几个剧本信息:")
            for i, playbook in enumerate(playbooks[:3]):
                print(f"  {i+1}. ID: {playbook.get('id')}, Name: {playbook.get('name')}, Enabled: {playbook.get('enabled')}")
        else:
            print("❌ 没有返回任何剧本数据")
            
            # 尝试直接查询数据库
            print("🔍 直接查询数据库...")
            session = db.get_session()
            try:
                from models import PlaybookModel
                count = session.query(PlaybookModel).count()
                print(f"📊 数据库中总共有 {count} 个剧本记录")
                
                if count > 0:
                    first_playbook = session.query(PlaybookModel).first()
                    print(f"📝 第一个剧本: ID={first_playbook.id}, Name={first_playbook.name}, Enabled={first_playbook.enabled}")
            except Exception as e:
                print(f"❌ 直接查询数据库失败: {e}")
                traceback.print_exc()
            finally:
                session.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_get_playbooks_admin()