import requests
from lxml import etree
import time
import random
import logging
from typing import List, Dict
import db_process

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_douban_movies() -> List[Dict]:
    """爬取豆瓣电影数据"""
    movie_list = []
    max_retries = 3  # 直接在函数中定义重试次数
    
    for page in range(1, 11):
        retry_count = 0
        while retry_count < max_retries:
            try:
                url = f'https://movie.douban.com/top250?start={(page - 1) * 25}&filter='
                response = requests.get(url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                
                tree = etree.HTML(response.text)
                divs = tree.xpath('//div[@class="info"]')
                
                for div in divs:
                    try:
                        movie = {}
                        # 电影中文标题
                        movie['电影中文名'] = ''.join(div.xpath('./div[@class="hd"]/a/span[@class="title"]/text()')).split('\xa0/\xa0')[0]
                        # 电影英文标题
                        movie['电影英文名'] = div.xpath('./div[@class="hd"]/a/span[2]/text()')[0].strip('\xa0/\xa0')
                        # 电影详情页链接
                        movie['电影详情页链接'] = div.xpath('./div[@class="hd"]/a/@href')[0]
                        
                        # 导演和主演
                        info_text = div.xpath('./div[@class="bd"]/p/text()')[0].strip()
                        movie['导演'] = info_text.split('导演: ')[1].split('主演: ')[0].strip()
                        try:
                            movie['主演'] = info_text.split('主演: ')[1].strip()
                        except IndexError:
                            movie['主演'] = '未知'
                        
                        # 详细信息
                        detail_text = div.xpath('./div[@class="bd"]/p/text()')[1].strip()
                        details = [item.strip() for item in detail_text.split('/')]
                        
                        movie['上映年份'] = details[0]
                        movie['国籍'] = details[1] if len(details[1][0].encode('utf-8')) > 1 else details[2]
                        movie['类型'] = details[2] if len(details[1][0].encode('utf-8')) > 1 else details[3]
                        
                        # 评分信息
                        movie['评分'] = div.xpath('./div[@class="bd"]/div/span[2]/text()')[0]
                        movie['评分人数'] = div.xpath('./div[@class="bd"]/div/span[4]/text()')[0]
                        
                        movie_list.append(movie)
                        
                    except Exception as e:
                        logging.error(f"解析电影数据时出错: {str(e)}")
                        continue
                
                logging.info(f'第{page}页爬取完成')
                # 添加随机延时
                time.sleep(2 + random.random() * 3)
                
                break
            except Exception as e:
                logging.error(f"爬取第{page}页时出错: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    logging.info(f"第{page}页爬取失败，重试第{retry_count}次")
                else:
                    logging.error(f"第{page}页爬取失败，重试次数已用完")
    
    return movie_list

def main():
    """主函数"""
    logging.info("开始爬取豆瓣Top250电影数据...")
    
    # 初始化数据库
    db_process.init_database()
    
    # 爬取数据
    movie_list = crawl_douban_movies()
    logging.info(f"共爬取 {len(movie_list)} 部电影信息")
    
    # 保存到数据库
    if db_process.insert_data_to_database(movie_list):
        logging.info("数据已成功保存到数据库")
    else:
        logging.error("数据保存失败")

if __name__ == '__main__':
    main()