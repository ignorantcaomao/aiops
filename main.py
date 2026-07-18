from fastapi import FastAPI, Request, Header, HTTPException, status
import logging

# 初始化 FastAPI 应用
app = FastAPI(title="GitHub Webhook Listener")

# 配置日志输出，方便在控制台查看事件
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/webhook/github-events")
async def handle_github_events(
    request: Request,
    x_github_event: str = Header(..., description="GitHub 事件类型")
):
    """
    获取并处理来自 GitHub 的所有 Webhook 事件
    """
    try:
        # 1. 解析来自 GitHub 的 JSON 数据体
        payload = await request.json()
        print(f"收到 payload: {payload}")
    except Exception as e:
        logger.error(f"解析 JSON 失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid JSON payload"
        )

    # 2. 根据不同的事件类型进行逻辑分发 (例如 push, pull_request)
    logger.info(f"收到 GitHub 事件类型: {x_github_event}")

    if x_github_event == "push":
        ref = payload.get("ref", "")
        repo_name = payload.get("repository", {}).get("full_name", "")
        committer = payload.get("head_commit", {}).get("author", {}).get("name", "")
        logger.info(f"【Push 事件】项目 {repo_name} 的 {ref} 分支被 {committer} 提交了代码。")
        # 这里可以加入你的代码检查、CI/CD 触发等逻辑

    elif x_github_event == "pull_request":
        action = payload.get("action", "")
        pr_number = payload.get("number", "")
        title = payload.get("pull_request", {}).get("title", "")
        logger.info(f"【PR 事件】动作: {action} | 编号: #{pr_number} | 标题: {title}")
        # 这里可以加入你的 AI Code Review 逻辑

    elif x_github_event == "ping":
        logger.info("【Ping 事件】成功接收到 GitHub 的连通性测试！")

    else:
        logger.info(f"【其他事件】未专门处理的事件数据: {payload}")

    # 3. 及时给 GitHub 响应 200 OK，避免超时重试
    return {"status": "success", "event_received": x_github_event}


@app.get("/")
async def root():
    """
    根路径，返回服务状态
    """
    return {"message": "GitHub Webhook Listener is running."}

if __name__ == "__main__":
    import uvicorn
    # 启动服务，运行在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)