import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from config import Config
async def run_agent():
    # 1. 连接你的本地 MCP Server
    server_config = {
        "my_local_tools": {
        "command": r"d:/study/lg_env/Scripts/python.exe",
        "args": [r"d:/study/mcp/mcp_server.py"],
        "transport": "stdio"
        }
    # },
    # "amap_tools": { #接入高德 但是太慢了
    #     "command": "npx",
    #     "args": ["-y", "@mapit-ai/mcp-server-amap"],
    #     "env": {"AMAP_KEY": Config.AMAP_KEY},
    #     "transport": "stdio"
    # }
    }

    print("--- 正在连接 MCP Server 并加载工具 ---")
    client = MultiServerMCPClient(server_config)
    try:
        # 2. 核心：通过适配器自动获取并转换工具
        # 这步执行完，langchain_tools 列表里有就躺着你写的 add 和 weather 了
        langchain_tools = await client.get_tools()
        print(f"成功加载工具: {[t.name for t in langchain_tools]}")

        model = ChatOpenAI(
            model=Config.Model, 
            api_key=Config.API_KEY, 
            base_url=Config.Base_url
        )

        # 4. 创建智能体
        # create_agent 会自动处理：用户提问 -> 模型判断是否需要工具 -> 调用工具 -> 返回结果
        prompt = (
            "你是一个智能助手。请根据用户需求，"
            "灵活调用计算器(add)或天气查询(weather)工具来回答问题。"
        )
        
        agent = create_agent(
            model, 
            langchain_tools,
            system_prompt=prompt # 引导模型正确生成工具调用格式
        )

        # 5. 测试：给一个需要调用两个工具的复杂指令
        query = "北京天气好吗？顺便帮我算下 123 加上 456 等于多少。"
        print(f"--- 用户提问: {query} ---")
        
        inputs = {"messages": [("user", query)]}

        try:
            async for event in agent.astream(inputs, stream_mode="updates"):
                for node_name, content in event.items():
                    print(f"\n[执行节点: {node_name}]")
                    if "messages" in content:
                        last_msg = content["messages"][-1]
                        # 打印模型回复或工具结果
                        if hasattr(last_msg, "content") and last_msg.content:
                            print(f"内容: {last_msg.content}")
                        elif hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            print(f"正在准备调用工具: {last_msg.tool_calls[0]['name']}")
        except Exception as e:
            print(f"\n❌ Agent 运行过程中发生错误: {e}")
            print("提示：如果依然报 400 错误，请尝试在 mcp_server.py 中将 weather 的返回信息改为简单的英文。")   
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(run_agent())