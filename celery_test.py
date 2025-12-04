#!/usr/bin/env python3
"""
Celery异步任务测试
学习：进程vs线程、任务队列
"""

from celery import Celery
import time

# 配置Celery
app = Celery('blog_tasks', broker='redis://localhost:6379/0')

@app.task
def send_welcome_email(user_email):
    """模拟发送欢迎邮件（耗时操作）"""
    print(f"📧 开始发送邮件到: {user_email}")
    time.sleep(3)  # 模拟邮件发送耗时
    print(f"✅ 邮件发送完成: {user_email}")
    return f"Email sent to {user_email}"

@app.task  
def generate_thumbnail(image_path):
    """模拟生成缩略图（耗时操作）"""
    print(f"🖼️  开始处理图片: {image_path}")
    time.sleep(2)  # 模拟图片处理耗时
    print(f"✅ 图片处理完成: {image_path}")
    return f"Thumbnail generated for {image_path}"

def test_sync_vs_async():
    """对比同步vs异步性能"""
    print("🔄 同步执行测试:")
    sync_start = time.time()
    
    # 同步执行（模拟没有Celery的情况）
    send_welcome_email("user1@example.com")
    generate_thumbnail("/path/to/image1.jpg")
    
    sync_time = time.time() - sync_start
    print(f"   同步执行时间: {sync_time:.2f}秒")
    
    print("\n⚡ 异步执行测试:")
    async_start = time.time()
    
    # 异步执行（使用Celery）
    task1 = send_welcome_email.delay("user2@example.com")
    task2 = generate_thumbnail.delay("/path/to/image2.jpg")
    
    async_time = time.time() - async_start
    print(f"   异步触发时间: {async_time:.2f}秒")
    print(f"   任务已提交到后台执行!")
    print(f"   主程序立即继续，不被阻塞!")
    
    print(f"\n📊 性能对比:")
    print(f"   同步: {sync_time:.2f}秒 (用户需要等待)")
    print(f"   异步: {async_time:.2f}秒 (立即返回)")

if __name__ == '__main__':
    test_sync_vs_async()
