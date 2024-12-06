import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 强制使用 Agg 后端
import matplotlib.pyplot as plt
import db_process
import logging
from matplotlib.font_manager import FontProperties
import os

# 创建图表保存目录
IMAGES_DIR = 'charts'
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# 尝试加载中文字体，依次尝试微软雅黑和黑体
try:
    font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")  # 微软雅黑
except:
    try:
        font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf")  # 黑体
    except:
        logging.error("未找到合适的中文字体，图表中文可能无法正常显示")
        font = None

def save_plot(filename):
    """保存图表"""
    filepath = os.path.join(IMAGES_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"图表已保存为 {filepath}")

def plot_nationality_distribution():
    """绘制不同国籍电影数量的条形图"""
    print("正在生成国籍分布图...")
    data = db_process.get_nationality_stats()  # 获取国籍统计数据
    if data:
        df = pd.DataFrame(data, columns=['Nationality', 'Count'])
        
        # 创建大尺寸图形以容纳所有数据
        plt.figure(figsize=(24, 10))
        
        # 绘制柱状图，设置较小的宽度以增加间距
        ax = df.plot(kind='bar', x='Nationality', y='Count', legend=False, width=0.3)
        
        # 设置图表标题和标签，使用中文字体
        plt.title('不同国家/地区电影数量分布', fontproperties=font, pad=20, fontsize=14)
        plt.xlabel('国家/地区', fontproperties=font, fontsize=12)
        plt.ylabel('电影数量', fontproperties=font, fontsize=12)
        
        # 调整x轴标签的旋转角度和字体
        plt.xticks(rotation=45, ha='right', fontproperties=font, fontsize=10)
        
        # 调整图表边距
        plt.subplots_adjust(bottom=0.25)
        plt.tight_layout()
        
        save_plot('nationality_distribution.png')
    else:
        print("获取数据失败，请检查数据库连接")

def plot_genre_distribution():
    """绘制不同类型电影数量的饼图"""
    print("正在生成类型分布图...")
    data = db_process.get_genre_stats()
    if data:
        df = pd.DataFrame(data, columns=['Genre', 'Count'])
        plt.figure(figsize=(10, 8))
        plt.pie(df['Count'], 
                labels=[str(x) for x in df['Genre']], 
                autopct='%1.1f%%')
        plt.title('电影类型分布', fontproperties=font)
        for text in plt.gca().texts:
            if text.get_text().strip('%').replace('.', '').isdigit():
                continue
            text.set_fontproperties(font)
        plt.axis('equal')
        plt.tight_layout()
        save_plot('genre_distribution.png')
    else:
        print("获取数据失败，请检查数据库连接")

def plot_director_distribution():
    """统计每位导演的作品数量分布（横向条形图）"""
    print("正在生成导演作品分布图...")
    data = db_process.get_director_stats()
    if data:
        df = pd.DataFrame(data, columns=['Director', 'Count'])
        # 只显示作品数量大于1的导演，并按数量降序排序
        df = df[df['Count'] > 1].sort_values('Count', ascending=True)
        
        # 创建更大的图形，增加高度
        plt.figure(figsize=(12, len(df) * 0.5))
        
        # 绘制横向条形图
        ax = plt.gca()
        bars = ax.barh(range(len(df)), df['Count'], height=0.6)  # 直接使用plt.barh而不是df.plot
        
        # 设置y轴刻度和标签
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels(df['Director'], fontproperties=font, fontsize=10)
        
        plt.title('导演作品数量分布（仅显示多部作品导演）', fontproperties=font, pad=20, fontsize=14)
        plt.xlabel('作品数量', fontproperties=font, fontsize=12)
        plt.ylabel('导演', fontproperties=font, fontsize=12)
        
        # 为每个条形添加数值标签
        for i, v in enumerate(df['Count']):
            ax.text(v, i, f' {v}', va='center', fontsize=10)
        
        # 调整边距
        plt.subplots_adjust(left=0.2, right=0.95, top=0.95, bottom=0.1)
        
        # 自动调整布局，但保持设置的边距
        plt.tight_layout()
        
        save_plot('director_distribution.png')
    else:
        print("获取数据失败，请检查数据库连接")

def main():
    """数据处理主函数"""
    print("数据处理模块已启动，请选择要生成的图表类型...")

