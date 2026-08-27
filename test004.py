import asyncio
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from dotenv import load_dotenv
load_dotenv()


async def main():
    model = init_chat_model(
        'gemini-3.6-flash',
        model_provider="google-genai",
        temperature=0.5,
        timeout=600,
        max_tokens=25000,
        streaming=True,
    )

    DB_URI = "redis://localhost:6379"
    async with AsyncRedisSaver.from_conn_string(DB_URI) as checkpointer:
        # await checkpointer.asetup()

        async def call_model(state: MessagesState):
            response = await model.ainvoke(state["messages"])
            return {"messages": response}

        builder = StateGraph(MessagesState)
        builder.add_node(call_model)
        builder.add_edge(START, "call_model")

        graph = builder.compile(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": "1"
            }
        }

        print("--- First turn ---")
        async for event in graph.astream_events(
            {"messages": [{"role": "user", "content": "hi! I'm djs"}]},
            config,
            version="v3",
        ):
            # Filter for stream events from the chat model
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                print(chunk.content, end="", flush=True)
        print("\n")

        print("--- Second turn ---")
        async for event in graph.astream_events(
            {"messages": [{"role": "user", "content": "what's my name?"}]},
            config,
            version="v3",
        ):
            # Filter for stream events from the chat model
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                print(chunk.content, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
