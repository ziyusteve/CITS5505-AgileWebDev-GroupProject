from app import create_app

app = create_app()

if __name__ == '__main__':
    # 关闭自动重载，确保只启动一个进程加载最新代码
    app.run(debug=True, use_reloader=False)
