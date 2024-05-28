import os

def list_ssl_files():
    ssl_dir = os.path.abspath('/etc/ssl/')

    # 切换到指定目录
    os.chdir(ssl_dir)
    
    # 列出目录下的所有文件和子目录
    files = os.listdir(ssl_dir)
    for file in files:
        print(file)

if __name__ == '__main__':
    list_ssl_files()
