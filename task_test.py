#!/usr/bin/env python3
"""
任务测试接口 - 学习：进程间通信、任务调度
"""

import pymysql
pymysql.install_as_MySQLdb()
from celery_tasks import send_email_notification, update_post_statistics, backup_database, process_user_registration
from app import app, User, Post
import time

def test_all_tasks():
    """测试所有类型的任务"""
    with app.app_context():
        print("🚀 开始测试Celery异步任务...")
        print("=" * 60)
        
        # 测试1：邮件发送任务
        print("1. 测试邮件发送任务:")
        start_time = time.time()
        email_task = send_email_notification.delay(
            "test@example.com", 
            "测试邮件主题", 
            "这是一封测试邮件内容"
        )
        email_trigger_time = time.time() - start_time
        print(f"   ✅ 任务提交成功! ID: {email_task.id}")
        print(f"   触发时间: {email_trigger_time:.3f}秒 (立即返回!)")
        
        # 测试2：统计更新任务
        print("\n2. 测试统计更新任务:")
        post = Post.query.first()
        if post:
            stat_task = update_post_statistics.delay(post.id)
            print(f"   ✅ 统计任务提交! ID: {stat_task.id}")
        
        # 测试3：备份任务
        print("\n3. 测试数据库备份:")
        backup_task = backup_database.delay()
        print(f"   ✅ 备份任务提交! ID: {backup_task.id}")
        
        # 测试4：用户注册流程
        print("\n4. 测试用户注册流程:")
        user = User.query.first()
        if user:
            reg_task = process_user_registration.delay(user.id)
            print(f"   ✅ 注册流程提交! ID: {reg_task.id}")
        
        print("\n" + "=" * 60)
        print("🎉 所有任务已提交到后台!")
        print("💡 主程序立即继续，不被阻塞!")
        print("📊 查看 celery.log 文件观察任务执行情况")
        
        return {
            "email_task": email_task.id,
            "stat_task": stat_task.id if post else None,
            "backup_task": backup_task.id,
            "reg_task": reg_task.id if user else None
        }

def check_task_results(task_ids):
    """检查任务结果"""
    print("\n🔍 检查任务状态:")
    from celery_tasks import send_email_notification
    
    for name, task_id in task_ids.items():
        if task_id:
            task_result = send_email_notification.AsyncResult(task_id)
            print(f"   {name}: {task_result.state}")

if __name__ == '__main__':
    tasks = test_all_tasks()
    
    # 等待一会儿后检查状态
    print("\n⏳ 等待5秒后检查任务状态...")
    time.sleep(5)
    check_task_results(tasks)
