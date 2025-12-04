#!/usr/bin/env python3
"""
独立的缓存性能测试
不修改主应用，避免启动问题
"""

import pymysql
pymysql.install_as_MySQLdb()
import redis
import time
from app import app, Post, User

# Redis配置
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def test_cached_query():
    """测试带缓存的查询性能"""
    with app.app_context():
        cache_key = "test:homepage:posts"
        
        # 尝试从缓存获取
        start_time = time.time()
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            print("✅ 缓存命中 - 直接从Redis读取")
            query_time = (time.time() - start_time) * 1000
            print(f"   查询时间: {query_time:.2f}ms")
            return
        
        # 缓存未命中，查询数据库
        print("❌ 缓存未命中 - 查询数据库")
        db_start_time = time.time()
        posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
        db_time = (time.time() - db_start_time) * 1000
        
        # 存入缓存
        redis_client.setex(cache_key, 60, "cached_data")  # 缓存60秒
        cache_time = (time.time() - start_time) * 1000
        
        print(f"   数据库查询: {db_time:.2f}ms")
        print(f"   总时间 (含缓存): {cache_time:.2f}ms")
        print(f"   下次访问将从缓存读取!")

def benchmark_queries():
    """性能对比测试"""
    print("🚀 开始缓存性能对比测试...")
    print("=" * 50)
    
    # 第一次查询（会缓存）
    print("第一次查询 (建立缓存):")
    test_cached_query()
    print()
    
    # 第二次查询（从缓存）
    print("第二次查询 (使用缓存):")
    test_cached_query()
    print()
    
    # 直接数据库查询对比
    print("直接数据库查询对比:")
    start_time = time.time()
    with app.app_context():
        posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
    direct_time = (time.time() - start_time) * 1000
    print(f"   直接数据库查询: {direct_time:.2f}ms")

if __name__ == '__main__':
    benchmark_queries()
