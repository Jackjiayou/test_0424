import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=300,    # 保持连接超时时间
        limit_concurrency=10,      # 限制并发连接数
        backlog=128,              # 连接队列大小
        workers=1,                # 工作进程数（使用GPU时建议保持为1）
        log_level="info"          # 日志级别
    ) 