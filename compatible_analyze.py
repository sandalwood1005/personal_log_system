import pymysql
pymysql.install_as_MySQLdb()

from app import app, db
from sqlalchemy import text

def compatible_analyze():
    with app.app_context():
        print("🔍 兼容性分析查询性能...")
        
        # 方法1：传统EXPLAIN（兼容所有版本）
        print("\n1. 传统EXPLAIN分析:")
        explain_result = db.session.execute(text("""
            EXPLAIN 
            SELECT post.*, user.* 
            FROM post 
            JOIN user ON post.user_id = user.id 
            ORDER BY post.created_at DESC 
            LIMIT 20
        """))
        
        print("   " + "-" * 80)
        print("   | id | select_type | table | type  | possible_keys | key     | key_len | rows | Extra |")
        print("   " + "-" * 80)
        for row in explain_result:
            print(f"   | {row[0]} | {row[1]:11} | {row[2]:5} | {row[3]:5} | {row[4] or 'NULL':14} | {row[5] or 'NULL':8} | {row[6] or 'NULL':7} | {row[7]:4} | {row[8] or '':6} |")
        print("   " + "-" * 80)
        
        # 方法2：检查MySQL版本
        print("\n2. 数据库版本信息:")
        version_result = db.session.execute(text("SELECT VERSION()"))
        for row in version_result:
            print(f"   数据库版本: {row[0]}")
        
        # 方法3：分析索引使用情况
        print("\n3. 索引使用分析:")
        index_usage = db.session.execute(text("""
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                SEQ_IN_INDEX,
                COLUMN_NAME,
                CARDINALITY
            FROM information_schema.STATISTICS 
            WHERE TABLE_SCHEMA = 'myblog' 
            AND TABLE_NAME IN ('post', 'user')
            ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
        """))
        
        current_table = ""
        for idx in index_usage:
            if idx[0] != current_table:
                print(f"   {idx[0]}表索引:")
                current_table = idx[0]
            print(f"     - {idx[1]}: {idx[3]} (基数: {idx[4]})")
        
        # 方法4：表统计分析
        print("\n4. 表统计分析:")
        table_stats = db.session.execute(text("""
            SELECT 
                TABLE_NAME,
                TABLE_ROWS,
                round(DATA_LENGTH/1024/1024, 2) as data_mb,
                round(INDEX_LENGTH/1024/1024, 2) as index_mb,
                round(DATA_LENGTH/1024/1024, 2) + round(INDEX_LENGTH/1024/1024, 2) as total_mb
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'myblog'
            ORDER BY TABLE_ROWS DESC
        """))
        
        for table in table_stats:
            print(f"   {table[0]}: {table[1]:,}行, 数据:{table[2]}MB, 索引:{table[3]}MB, 总计:{table[4]}MB")

if __name__ == '__main__':
    compatible_analyze()
