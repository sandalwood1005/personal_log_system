#!/usr/bin/env python3

# 绑定地址
bind = "127.0.0.1:5000"

# 🎯 关键优化：使用异步Worker（I/O多路复用）
worker_class = "gevent"
worker_connections = 1000

# 进程数配置（根据CPU核心数调整）
workers = 5  

# 线程数（如果使用同步Worker）
threads = 4

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 超时设置
timeout = 30
graceful_timeout = 30
keepalive = 2

# 日志配置
accesslog = "/var/www/myblog/logs/gunicorn_access.log"
errorlog = "/var/www/myblog/logs/gunicorn_error.log"
loglevel = "info"

# 进程名称（方便监控）
proc_name = "myblog_gunicorn"

# 启动设置
preload_app = True  # 预加载应用，减少内存使用

def when_ready(server):
    """服务器启动完成时调用"""
    print(f"🚀 Gunicorn服务器启动完成 - {workers}个Worker进程")

def on_exit(server):
    """服务器退出时调用"""
    print("🛑 Gunicorn服务器关闭")

if __name__ == '__main__':
    print("✅ Gunicorn配置检查:")
    print(f"   Worker类型: {worker_class}")
    print(f"   Worker数量: {workers}")
    print(f"   最大连接数: {worker_connections}")
    print(f"   监听地址: {bind}")
