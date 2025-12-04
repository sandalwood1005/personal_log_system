import pymysql
pymysql.install_as_MySQLdb()

from app import app, db, User, Post, Category, Comment
import random
from datetime import datetime, timedelta

def generate_performance_data():
    with app.app_context():
        print("🚀 开始生成性能测试数据...")
        
        # 创建测试用户
        users = []
        for i in range(50):
            user = User(
                username=f'user_{i}',
                email=f'user{i}@example.com',
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ 创建了 {len(users)} 个测试用户")
        
        # 创建分类
        categories = []
        category_names = ['Python编程', 'Linux系统', '数据库', 'Web开发', '前端技术', '后端架构', 'DevOps', '云计算']
        for name in category_names:
            category = Category(name=name)
            categories.append(category)
            db.session.add(category)
        
        db.session.commit()
        print(f"✅ 创建了 {len(categories)} 个分类")
        
        # 创建大量文章（制造性能压力）
        print("📝 开始创建大量文章（这需要几分钟）...")
        posts = []
        for i in range(10000):  # 创建10000篇文章
            post = Post(
                title=f'深入探讨{i}：{random.choice(["Python", "Linux", "MySQL", "性能优化", "高并发"])}的最佳实践',
                content=f'这是第{i}篇深度技术文章，详细讨论相关技术细节。' * 50,
                user_id=random.choice(users).id,
                category_id=random.choice(categories).id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            posts.append(post)
            db.session.add(post)
            
            # 每500条提交一次，显示进度
            if i % 500 == 0:
                db.session.commit()
                print(f'  已创建 {i} 篇文章...')
        
        db.session.commit()
        print(f"✅ 总共创建了 {len(posts)} 篇文章")
        
        # 创建评论数据
        print("💬 创建评论数据...")
        comments_count = 0
        for post in random.sample(posts, 2000):  # 随机选择2000篇文章添加评论
            for j in range(random.randint(3, 15)):
                comment = Comment(
                    content=f'这篇文章关于"{post.title}"写得很好，第{j}条评论表示支持！',
                    user_id=random.choice(users).id,
                    post_id=post.id,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 100))
                )
                db.session.add(comment)
                comments_count += 1
        
        db.session.commit()
        print(f"✅ 创建了 {comments_count} 条评论")
        
        # 统计最终数据量
        total_posts = db.session.query(Post).count()
        total_users = db.session.query(User).count()
        total_comments = db.session.query(Comment).count()
        
        print("\n🎉 性能测试数据生成完成！")
        print("======================================")
        print(f"📊 数据库统计:")
        print(f"   用户数量: {total_users}")
        print(f"   文章数量: {total_posts}")
        print(f"   评论数量: {total_comments}")
        print(f"   总数据量: {total_users + total_posts + total_comments} 条记录")
        print("======================================")
        print("现在可以开始性能优化测试了！")

if __name__ == '__main__':
    generate_performance_data()
