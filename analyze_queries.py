import pymysql
pymysql.install_as_MySQLdb()

from app import app, db, Post, User
from sqlalchemy import text

def analyze_queries():
    with app.app_context():
        print("🔍 开始分析查询性能...")
        
        # 分析慢查询：带作者的文章查询
        print("\n1. 分析带作者的文章查询 (238ms):")
        explain_result = db.session.execute(text(
            "EXPLAIN SELECT post.*, user.* FROM post JOIN user ON post.user_id = user.id ORDER BY post.created_at DESC LIMIT 20"
        ))
        for row in explain_result:
            print(f"   - type: {row[3]}, key: {row[5]}, rows: {row[6]}, Extra: {row[9]}")
        
        # 分析文章表索引
        print("\n2. 分析文章表索引:")
        indexes = db.session.execute(text("SHOW INDEX FROM post"))
        has_created_at_index = False
        has_user_id_index = False
        
        for idx in indexes:
            print(f"   - 索引: {idx[2]}, 字段: {idx[4]}")
            if idx[4] == 'created_at':
                has_created_at_index = True
            if idx[4] == 'user_id':
                has_user_id_index = True
        
        print(f"\n3. 索引状态:")
        print(f"   - created_at 索引: {'✅ 存在' if has_created_at_index else '❌ 缺失'}")
        print(f"   - user_id 索引: {'✅ 存在' if has_user_id_index else '❌ 缺失'}")
        
        # 查看表数据量
        table_stats = db.session.execute(text("""
            SELECT 
                table_name,
                table_rows,
                round(data_length/1024/1024, 2) as data_mb,
                round(index_length/1024/1024, 2) as index_mb
            FROM information_schema.tables 
            WHERE table_schema = 'myblog' AND table_name IN ('post', 'user')
        """))
        
        print("\n4. 表统计信息:")
        for table in table_stats:
            print(f"   - {table[0]}: {table[1]} 行, 数据: {table[2]}MB, 索引: {table[3]}MB")

if __name__ == '__main__':
    analyze_queries()
