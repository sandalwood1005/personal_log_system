import pymysql
pymysql.install_as_MySQLdb()

from app import app, db
from sqlalchemy import text
import time

def final_test():
    with app.app_context():
        print("🎯 最终优化效果测试...")
        
        # 测试1：使用覆盖索引的优化查询
        start_time = time.time()
        result = db.session.execute(text("""
            SELECT 
                p.id, p.title, p.created_at, 
                p.category_id, u.username, u.email
            FROM post p 
            FORCE INDEX (idx_post_covering)
            JOIN user u ON p.user_id = u.id 
            ORDER BY p.created_at DESC 
            LIMIT 20
        """)).fetchall()
        optimized_time = (time.time() - start_time) * 1000
        
        # 测试2：检查执行计划
        print("\n🔍 优化后执行计划:")
        explain_result = db.session.execute(text("""
            EXPLAIN 
            SELECT p.id, p.title, p.created_at, u.username
            FROM post p FORCE INDEX (idx_post_covering)
            JOIN user u ON p.user_id = u.id 
            ORDER BY p.created_at DESC 
            LIMIT 20
        """))
        
        for row in explain_result:
            print(f"   表: {row[0]}, 类型: {row[3]}, 索引: {row[5]}")
        
        print("\n📊 最终性能对比:")
        print("======================================")
        print(f"优化前: 238.65ms")
        print(f"优化后: {optimized_time:.2f}ms")
        print(f"性能提升: {238.65/optimized_time:.1f}x 倍")
        print("======================================")
        
        if optimized_time < 50:
            print("🎉 优化成功！达到了生产环境标准")
        elif optimized_time < 100:
            print("✅ 良好优化！用户体验可接受")
        else:
            print("💪 继续努力，还有优化空间")

if __name__ == '__main__':
    final_test()
