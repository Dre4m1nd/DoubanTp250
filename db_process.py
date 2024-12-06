import sqlite3
import logging
from typing import List, Dict, Tuple, Optional

DB_NAME = 'douban_movies.db'  # 数据库文件名

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接，返回连接对象或None"""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except Exception as e:
        logging.error(f"数据库连接失败: {str(e)}")
        return None

def init_database() -> None:
    """初始化数据库"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chinese_name TEXT NOT NULL,
                english_name TEXT,
                movie_url TEXT,
                director TEXT,
                actors TEXT,
                release_year TEXT,
                country TEXT,
                genre TEXT,
                rating FLOAT,
                rating_count INTEGER,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            logging.info("数据库初始化成功")
        except Exception as e:
            logging.error(f"数据库初始化失败: {str(e)}")
        finally:
            conn.close()

def insert_data_to_database(movie_list: List[Dict]) -> bool:
    """将电影数据插入数据库"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        for movie in movie_list:
            cursor.execute('''
            INSERT INTO movies (
                chinese_name, english_name, movie_url, director, 
                actors, release_year, country, genre, 
                rating, rating_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie['电影中文名'],
                movie['电影英文名'],
                movie['电影详情页链接'],
                movie['导演'],
                movie['主演'],
                movie['上映年份'],
                movie['国籍'],
                movie['类型'],
                float(movie['评分']),
                int(movie['评分人数'].replace('人评价', ''))
            ))
        conn.commit()
        logging.info(f"成功插入 {len(movie_list)} 条电影数据")
        return True
    except Exception as e:
        logging.error(f"数据插入失败: {str(e)}")
        return False
    finally:
        conn.close()

def get_nationality_stats() -> Optional[List[Tuple]]:
    """获取国籍统计数据（拆分复合国籍并分别统计）"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        # 使用WITH子句创建临时表，将复合国籍拆分并统计
        cursor.execute('''
        WITH RECURSIVE split_countries AS (
            SELECT 
                TRIM(value) as country,
                COUNT(*) as count
            FROM movies
            CROSS JOIN json_each('["' || REPLACE(country, ' ', '","') || '"]')
            GROUP BY TRIM(value)
            ORDER BY count DESC
        )
        SELECT country, count
        FROM split_countries
        WHERE country != ''
        ORDER BY count DESC, country
        ''')
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"获取国籍统计数据失败: {str(e)}")
        return None
    finally:
        conn.close()

def get_genre_stats() -> Optional[List[Tuple]]:
    """获取电影类型统计数据（只取第一个类型）"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT 
            SUBSTR(genre, 1, INSTR(genre || ' ', ' ') - 1) as main_genre,
            COUNT(*) as count 
        FROM movies 
        GROUP BY main_genre 
        ORDER BY count DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"获取类型统计数��失败: {str(e)}")
        return None
    finally:
        conn.close()

def get_director_stats() -> Optional[List[Tuple]]:
    """获取导演作品数量统计数据"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT director, COUNT(*) as count 
        FROM movies 
        GROUP BY director 
        ORDER BY count DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"获取导演统计数据失败: {str(e)}")
        return None
    finally:
        conn.close()

def check_data_exists() -> bool:
    """检查数据库中是否已有数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM movies')
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        logging.error(f"检查数据失败: {str(e)}")
        return False
    finally:
        conn.close()