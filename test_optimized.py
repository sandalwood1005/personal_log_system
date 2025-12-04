import pymysql
pymysql.install_as_MySQLdb()

from app import app, db, Post, User
from sqlalchemy import func
import time

def test_optimized_performance():
    with app.app_context():
        print("🚀 测试优化后性能...")
        
        # 测试1：文章列表查询
        start_time = time.time()
        posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
        query1_time = (time.time() - start_time) * 1000
        
        # 测试2：带用户信息的文章查询（优化目标）
        start_time = time.time()
        posts_with_author = db.session.query(Post, User).join(User).order_by(Post.created_at.desc()).limit(20).all()
        query2_time = (time.time() - start_time) * 1000
        
        # 测试3：使用 EXPLAIN 验证优化
        print("\n🔍 验证优化效果:")
        explain_result = db.session.execute(
            "EXPLAIN SELECT post.*, user.* FROM post JOIN user ON post.user_id = user.id ORDER BY post.created_at  LIMIT 20"
        )
        for row in explain_result:
            print(f"   - 执行计划: type={row[3]}, key={row[5]}, rows={row[6]},extra={row[9]}")
        
        print("\n📊 性能对比结果:")
        print("======================================")
        print(f"📄 文章列表查询: {query1_time:.2f}ms")
        print(f"👥 带作者文章查询: {query2_time:.2f}ms (优化前: 238.65ms)")
        print(f"📈 性能提升: {238.65/query2_time:.1f}x 倍")
        print("======================================")
        
        if query2_time < 50:
            print("🎉 优化成功！查询时间从 238ms 优化到", f"{query2_time:.2f}ms")
        else:
            print("💪 有改善，但还可以进一步优化")

if __name__ == '__main__':
    test_optimized_performance()
