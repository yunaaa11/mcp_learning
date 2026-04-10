from mcp import StdioServerParameters,stdio_client,ClientSession
#它告诉客户端“怎么启动 Server”。在这个例子里，它会开启一个子进程来运行 python d:/study/mcp/mcp_server.py。
#ClientSession：这是建立连接后的会话。它负责发送指令（如 call_tool）并接收结果。
import mcp.types as types
server_params=StdioServerParameters(
    command=r"d:/study/lg_env/Scripts/python.exe",
    args=[r"d:/study/mcp/mcp_server.py"],
    env=None
)
async def handle_sampling_message(message:types.CreateMessageRequestParams)->types.CreateMessageResult:
    print(f"sampling message:{message}")
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello,world!from model"
        ),
        model="qwen-max",
        stopReason="endTurn"
    )
async def run():
    print("正在尝试启动 Server...") # 打印点 1
    async with stdio_client(server_params) as (read,write):
        print("Server 进程已启动，正在建立 Session...") # 打印点 2
        async with ClientSession(read,write,sampling_callback=handle_sampling_message) as session:
            await session.initialize()
            print("初始化完成！")
            prompts=await session.list_prompts()
            print(f"prompts:{prompts}")
            tools=await session.list_tools()
            print(f"tools:{tools}")
            result=await session.call_tool("weather",{"city":"北京"})
            print(f"result:{result}")
            resources = await session.list_resources()
            print(f"发现资源: {resources}")
            greeting_result = await session.read_resource("greeting://zhao1")
            print(f"资源运行结果: {greeting_result}")

if __name__=="__main__":
    import asyncio
    asyncio.run(run())
#生命周期
#启动进程 -> 初始化 (initialize) -> 获取列表 (list_tools) -> 远程调用 (call_tool) -> 关闭连接 的完整过程
