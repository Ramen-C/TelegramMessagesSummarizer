# summarizer.py

import json
from openai import OpenAI
from pathlib import Path

# 读取配置
config_path = Path('../settings/config.json')
config = json.loads(config_path.read_text())
proxy = config.get("api_key")  # 可为空
# --- 核心改动 1: 函数签名改变，接收一个列表作为参数 ---
def summarize_chat(formatted_messages: list):
    """
    接收一个格式化后的消息列表，调用 DeepSeek API 进行分析，并返回摘要字符串。
    """
    if not formatted_messages:
        raise ValueError("没有可用的文本消息用于摘要。")

    # --- 核心改动 2: 直接用换行符连接列表内容，不再读取文件 ---
    chat_text = "\n".join(formatted_messages)

    # 初始化 DeepSeek 客户端 (请确保你的API Key在这里)
    client = OpenAI(
        api_key='sk-80f4be0c573f49dfb31558c774ccf1f0', # 您的 DeepSeek Key
        base_url="https://api.deepseek.com"
    )

    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
    # 检查语言设置
    language_value = config_data.get('language')

    # (这里的 Prompt 保持不变，它设计得很好，可以直接使用)
    if language_value == "zh":
        print("2")
        system_prompt = "你是一位精通信息提取和内容归纳的资深社群运营分析师。"
        user_prompt = f"""
        作为一名专业的 Telegram 群聊分析师，请根据下方用 '---' 分隔的、包含匿名化用户（如 User A, User B）的聊天记录，生成一份简洁、精准、结构化的摘要报告。
        聊天记录已按时间倒序排列（最新消息在前）。
    
        你的核心任务是：
    
        1.  **核心议题归纳 (Main Topics)**:
            - 识别并提炼出 2-4 个本次讨论的核心议题。
        2.  **关键信息与决策 (Key Information & Decisions)**:
            - 提取对话中所有明确的结论、决策或一致同意的观点。
            - 整理出具体的待办事项（Action Items）。如果无，则注明“无”。
        3.  **重要链接提取 (Important Links)**:
            - 识别所有分享的 URL 链接并简要说明其内容。
        4.  **金句或趣味发言 (Quotes & Highlights)**:
            - 挑选出 1-10 条最有趣或最具代表性的发言。
    
        以下是原始聊天记录：
    
        {chat_text}
        """

    else:
        system_prompt = "You are a senior community operations analyst proficient in information extraction and content summarization."
        user_prompt = f"""
        As a professional Telegram chat analyst, please generate a concise, accurate, and structured summary report based on the chat records below, separated by '---', which include anonymized users (e.g., User A, User B).
        The chat records are sorted in reverse chronological order (latest messages first).
    
        Your core tasks are:
    
        1.  **Main Topics**:
            - Identify and extract 2-4 main topics of this discussion.
        2.  **Key Information & Decisions**:
            - Extract all explicit conclusions, decisions, or agreed-upon points from the conversation.
            - List specific action items. If none, state "None".
        3.  **Important Links**:
            - Identify all shared URLs and briefly describe their content.
        4.  **Quotes & Highlights**:
            - Select 1-10 of the most interesting or representative statements.
    
        Here are the original chat records:
    
        {chat_text}
        """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    summary = response.choices[0].message.content.strip()
    print("=== 聊天摘要 ===")
    print(summary)
    return summary