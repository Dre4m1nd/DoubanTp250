import crawl
import db_process
import data_process
import sys
import logging

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_menu(menu_type):
    """打印菜单，根据menu_type显示不同的菜单选项"""
    if menu_type == "main":
        print("""
        豆瓣Top250电影数据分析系统
        ========================
        1. 爬取数据
        2. 数据可视化
        3. 清空数据库
        0. 退出系统
        """)
    elif menu_type == "visualization":
        print("""
        数据可视化选项
        ============
        1. 国籍分布图
        2. 类型分布图
        3. 导演作品分布图
        0. 返回主菜单
        """)

def handle_visualization():
    """处理可视化菜单的用户选择"""
    # 检查数据库中是否有数据
    if not db_process.check_data_exists():
        print("数据库中没有数据，请先爬取数据！")
        return
        
    while True:
        print_menu("visualization")
        viz_choice = input("请输入您的选择: ").strip()
        
        if viz_choice == '0':
            break
        elif viz_choice == '1':
            data_process.plot_nationality_distribution()  # 生成国籍分布图
        elif viz_choice == '2':
            data_process.plot_genre_distribution()  # 生成类型分布图
        elif viz_choice == '3':
            data_process.plot_director_distribution()  # 生成导演作品分布图
        else:
            print("无效的选择，请重新输入")

def main():
    """主函数：程序入口点"""
    logging.info("程序启动")
    db_process.init_database()  # 初始化数据库
    
    while True:
        print_menu("main")
        choice = input("请输入您的选择: ").strip()
        
        if choice == '0':
            print("感谢使用，再见！")
            logging.info("程序正常退出")
            sys.exit(0)
            
        elif choice == '1':
            # 检查是否需要重新爬取数据
            if db_process.check_data_exists():
                confirm = input("数据库中已有数据，是否重新爬取？(y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            crawl.main()  # 启动爬虫
            
        elif choice == '2':
            handle_visualization()  # 处理可视化选项
            
        elif choice == '3':
            # 清空数据库操作需要确认
            confirm = input("确定要清空数据库吗？(y/n): ").strip().lower()
            if confirm == 'y':
                db_process.init_database()
                print("数据库已清空")
            
        else:
            print("无效的选择，请重新输入")

if __name__ == '__main__':
    main()