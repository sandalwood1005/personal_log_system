#!/usr/bin/env python3
"""
Redis缓存工具类
学习：缓存机制、内存管理、缓存策略
"""

import redis
import json
import pickle
from functools import wraps
from app import app

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def get(self, key):
        """获取缓存"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value.encode('latin1'))
            return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None
    
    def set(self, key, value, expire=3600):
        """设置缓存"""
        try:
            self.redis_client.setex(
                key,
                expire,
                pickle.dumps(value).decode('latin1')
            )
            return True
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    def delete(self, key):
        """删除缓存"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """按模式清除缓存"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return len(keys)
        except Exception as e:
            print(f"模式清除失败: {e}")
            return 0

# 创建全局缓存实例
cache = RedisCache()

def cache_view(timeout=300):
    """视图缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键
            cache_key = f"view:{f.__name__}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"✅ 缓存命中: {cache_key}")
                return cached_result
            
            # 执行原函数
            print(f"❌ 缓存未命中: {cache_key}")
            result = f(*args, **kwargs)
            
            # 缓存结果
            cache.set(cache_key, result, timeout)
            return result
        return decorated_function
    return decorator

def cache_invalidate(pattern):
    """缓存失效装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 先执行函数
            result = f(*args, **kwargs)
            
            # 然后清除相关缓存
            deleted_count = cache.clear_pattern(pattern)
            print(f"🗑️  清除缓存: {pattern} ({deleted_count}个)")
            
            return result
        return decorated_function
    return decorator

if __name__ == '__main__':
    # 测试缓存功能
    with app.app_context():
        # 测试基本缓存
        cache.set('test_key', {'name': 'test', 'value': 123})
        result = cache.get('test_key')
        print(f"缓存测试: {result}")
