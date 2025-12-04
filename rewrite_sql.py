import pymysql
pymysql.install_as_MySQLdb()

from app import app, db, Post, User
from sqlalchemy import text
import time

def test_rewritten_queries():
    with app.app_context():
        print("🔄 测试SQL重写优化...")
        
        # 原始查询（慢）
        start_time = time.time()
        result1 = db.session.execute(text("""
            SELECT post.*, user.username, user.email 
            FROM post 
            JOIN user ON post.user_id = user.id 
            ORDER BY post.created_at DESC 
            LIMIT 20
        """)).fetchall()
        time1 = (time.time() - start_time) * 1000
        
        # 优化方案1：使用子查询减少JOIN数据量
        start_time = time.time()
        result2 = db.session.execute(text("""
            SELECT p.*, u.username, u.email 
            FROM (
                SELECT * FROM post 
                ORDER BY created_at DESC 
                LIMIT 20
            ) p
            JOIN user u ON p.user_id = u.id
        """)).fetchall()
        time2 = (time.time() - start_time) * 1000
        
        # 优化方案2：强制使用索引
        start_time = time.time()
        result3 = db.session.execute(text("""
            SELECT /*+ INDEX(post idx_post_created_at) */ 
                   post.*, user.username, user.email 
            FROM post 
            JOIN user ON post.user_id = user.id 
            ORDER BY post.created_at DESC 
            LIMIT 20
        """)).fetchall()
        time3 = (time.time() - start_time) * 1000
        
        print("\n📊 SQL重写优化对比:")
        print("======================================")
        print(f"原始查询: {time1:.2f}ms")
        print(f"子查询优化: {time2:.2f}ms")
        print(f"强制索引: {time3:.2f}ms")
        print("======================================")
        
        # 验证结果一致性
        print(f"结果一致性: {len(result1) == len(result2) == len(result3)}")

if __name__ == '__main__':
    test_rewritten_queries()
