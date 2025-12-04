#!/usr/bin/env python3
"""
真实的Celery任务 - 学习：进程通信、任务调度、错误处理
"""

from celery_config import celery
from app import app, db, User, Post, Comment
import smtplib
from email.mime.text import MIMEText
import time
import requests

@celery.task(bind=True, max_retries=3)
def send_email_notification(self, to_email, subject, content):
    """
    发送邮件通知 - 学习：I/O密集型任务异步化
    """
    try:
        print(f"📧 开始发送邮件到: {to_email}")
        
        # 模拟邮件发送（真实环境替换为SMTP调用）
        print(f"   主题: {subject}")
        print(f"   内容: {content[:50]}...")
        
        # 模拟网络延迟
        time.sleep(2)
        
        # 模拟可能的失败（10%概率）
        import random
        if random.random() < 0.1:
            raise Exception("模拟邮件发送失败")
        
        print(f"✅ 邮件发送成功: {to_email}")
        return {"status": "success", "email": to_email}
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        # 自动重试（Celery自动重试机制）
        raise self.retry(countdown=60, exc=e)  # 60秒后重试

@celery.task
def update_post_statistics(post_id):
    """
    更新文章统计信息 - 学习：CPU密集型任务异步化
    """
    with app.app_context():
        try:
            print(f"📊 开始更新文章统计: {post_id}")
            
            post = Post.query.get(post_id)
            if not post:
                return {"status": "error", "message": "文章不存在"}
            
            # 计算阅读量趋势（模拟复杂计算）
            time.sleep(1)
            
            # 更新评论数缓存
            comment_count = Comment.query.filter_by(post_id=post_id).count()
            
            # 模拟一些数据分析
            import random
            popularity_score = comment_count * random.uniform(0.8, 1.2)
            
            print(f"✅ 文章统计更新完成: {post_id}")
            print(f"   评论数: {comment_count}, 热度分: {popularity_score:.2f}")
            
            return {
                "status": "success", 
                "post_id": post_id,
                "comment_count": comment_count,
                "popularity_score": popularity_score
            }
            
        except Exception as e:
            print(f"❌ 统计更新失败: {e}")
            return {"status": "error", "message": str(e)}

@celery.task
def backup_database():
    """
    数据库备份任务 - 学习：定时任务、资源管理
    """
    try:
        print("💾 开始数据库备份...")
        
        # 模拟备份过程
        time.sleep(3)
        
        # 这里可以添加真实的备份逻辑
        # 1. 导出数据库
        # 2. 上传到云存储
        # 3. 清理旧备份
        
        print("✅ 数据库备份完成")
        return {"status": "success", "backup_time": time.strftime("%Y-%m-%d %H:%M:%S")}
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return {"status": "error", "message": str(e)}

@celery.task
def process_user_registration(user_id):
    """
    用户注册后续处理 - 学习：工作流、任务链
    """
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                return {"status": "error", "message": "用户不存在"}
            
            print(f"👤 处理用户注册后续: {user.username}")
            
            # 任务1：发送欢迎邮件
            email_task = send_email_notification.delay(
                user.email,
                "欢迎注册技术博客",
                f"尊敬的{user.username}，欢迎加入我们的技术社区！"
            )
            
            # 任务2：更新用户统计
            from sqlalchemy import func
            total_users = User.query.count()
            
            # 任务3：准备推荐内容
            recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
            
            print(f"✅ 用户注册处理完成: {user.username}")
            print(f"   总用户数: {total_users}")
            print(f"   推荐文章: {len(recent_posts)}篇")
            
            return {
                "status": "success",
                "user_id": user_id,
                "email_task_id": email_task.id,
                "total_users": total_users
            }
            
        except Exception as e:
            print(f"❌ 用户注册处理失败: {e}")
            return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    print("✅ Celery任务模块加载成功")
    print("   可用的任务:")
    print("   - send_email_notification")
    print("   - update_post_statistics") 
    print("   - backup_database")
    print("   - process_user_registration")
