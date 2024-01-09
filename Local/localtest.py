import os
import platform
import configparser
from pathlib import Path
import requests
from datetime import datetime

# 配置文件路径 保存至当前目录
config_file = Path.cwd() / "ddns_config.ini"

# 初始化配置解析器
config = configparser.ConfigParser()

def show_menu():
    print("\n主菜单")
    print("1. 设置用户信息")
    print("2. 查看当前配置")
    print("3. 查看当前地址")
    print("4. 设置刷新间隔")
    print("0. 退出")
    choice = input("请输入您的选择: ")
    return choice

def load_config():
    """ 加载配置文件 """
    if config_file.exists():
        config.read(config_file)
    else:
        # 如果配置文件不存在，则创建空的配置节
        config['USER'] = {}
        config['SETTINGS'] = {}

def save_config():
    """ 保存配置到文件 """
    with open(config_file, 'w') as file:
        config.write(file)

def configure_account():
    """ 设置用户信息 """
    username = input("请输入用户名: ")
    server = input("请输入服务器URL: ")
    config['USER']['username'] = username
    # config['USER']['server'] = server
    save_config()
    print("账户配置成功。\n")

def wait_for_keypress():
    # 检测操作系统类型
    if platform.system() == "Windows":
        # Windows系统: 使用os.system调用pause命令
        os.system("pause")
    else:
        # 非Windows系统 (如Linux或macOS): 使用input()
        input("\n按回车键继续...\n")

def check_configuration():
    """ 查看当前用户配置 """
    if 'USER' in config and 'username' in config['USER']:
        print(f"\n当前配置:")
        print(f"用户名: {config['USER']['username']}")
        # print(f"服务器URL: {config['USER']['server']}")
        print(f"刷新间隔: {config['SETTINGS'].get('refresh_interval', '未设置')}")
    else:
        print("\n未找到配置。")
    wait_for_keypress()

def get_public_ip():
    """ 查询当前的公网IP地址 """
    try:
        response = requests.get("http://api.ipify.org", timeout=10)  # 设置10秒超时
        response.raise_for_status()  # 检查响应状态码
        return response.text
    except requests.Timeout:
        return "Error: 请求超时，请检查您的网络连接。"
    except requests.RequestException as e:
        return f"Error: 发生错误 - {e}"


def save_ip_to_file(ip_address):
    """ 保存IP地址到文件 """
    with open("ip_history.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp}: {ip_address}\n")

def show_current_ip():
    """ 显示当前IP并保存结果 """
    ip_address = get_public_ip()
    print(f"\n当前IP地址: {ip_address}")
    save_ip_to_file(ip_address)
    wait_for_keypress()

def configure_refresh_interval():
    """ 设置刷新间隔 """
    while True:
        try:
            interval = int(input("请输入刷新间隔（10 - 65535分钟）: "))
            if 10 <= interval <= 65535:
                config['SETTINGS']['refresh_interval'] = str(interval)
                save_config()
                print("刷新间隔设置成功。\n")
                wait_for_keypress()
                break
            else:
                print("输入的间隔不在允许的范围内，请重新输入。")
                wait_for_keypress()
                break
        except ValueError:
            print("请输入一个有效的数字。")

def main():
    load_config()
    while True:
        choice = show_menu()
        if choice == "1":
            configure_account()
        elif choice == "2":
            check_configuration()
        elif choice == "3":
            show_current_ip()
        elif choice == "4":
            configure_refresh_interval()
        elif choice == "0":
            print("退出程序。")
            break
        else:
            print("无效选择，请重试。")

if __name__ == "__main__":
    main()
