#!/usr/bin/env python3
"""
Celery配置 - 学习：进程管理、消息队列、后台任务
"""

from celery import Celery
import pymysql
pymysql.install_as_MySQLdb()

# 创建Celery应用
def make_celery():
    celery = Celery(
        'blog_tasks',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/1',
        include=['celery_tasks']
    )
    
    # 配置
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
    )
    
    return celery

celery = make_celery()

if __name__ == '__main__':
    print("✅ Celery配置加载成功")
    print(f"   Broker: {celery.conf.broker_url}")
    print(f"   Backend: {celery.conf.result_backend}")
