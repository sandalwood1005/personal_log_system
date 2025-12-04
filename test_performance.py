import pymysql
pymysql.install_as_MySQLdb()

from app import app, db, Post, User, Comment
import time

def test_performance():
    with app.app_context():
        print("🔍 开始性能测试...")
        
        # 测试1：文章列表查询（模拟首页）
        start_time = time.time()
        posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
        query1_time = (time.time() - start_time) * 1000
        
        # 测试2：带用户信息的文章查询
        start_time = time.time()
        posts_with_author = db.session.query(Post, User).join(User).order_by(Post.created_at.desc()).limit(20).all()
        query2_time = (time.time() - start_time) * 1000
        
        # 测试3：分类统计查询
        start_time = time.time()
        from sqlalchemy import func
        category_stats = db.session.query(Post.category_id, func.count(Post.id)).group_by(Post.category_id).all()
        query3_time = (time.time() - start_time) * 1000
        
        print("\n📊 性能测试结果（优化前）:")
        print("======================================")
        print(f"📄 文章列表查询: {query1_time:.2f}ms")
        print(f"👥 带作者文章查询: {query2_time:.2f}ms") 
        print(f"📂 分类统计查询: {query3_time:.2f}ms")
        print("======================================")
        print("💡 这些查询现在应该比较慢了，接下来我们优化它们！")

if __name__ == '__main__':
    test_performance()
