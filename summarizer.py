import json
from openai import OpenAI
from visualizer import generate_wordcloud

def summarize_chat():
    """
    使用 DeepSeek API 对导出的聊天记录进行分析，并返回 Markdown 格式的摘要字符串。
    """
    # 读取 JSON 文件
    with open('tdl-export-filtered.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取消息文本（兼容没有 text 的消息）
    messages = [
        msg['text'] for msg in data.get('messages', [])
        if isinstance(msg.get('text'), str) and msg['text'].strip()
    ]
    chat_text = "\n".join(messages)

    if not chat_text.strip():
        raise ValueError("没有可用的文本消息用于摘要。")

    # 初始化 DeepSeek 客户端
    client = OpenAI(
        api_key='sk-80f4be0c573f49dfb31558c774ccf1f0',
        base_url="https://api.deepseek.com"
    )

    # 构造对话提示
    system_prompt = "你是一个擅长提取关键信息的聊天摘要专家。"
    user_prompt = f"""
    你是一名专业的 Telegram 群聊分析师，请根据以下对话内容生成简洁清晰的结构化摘要。你的任务包括：

    1. **识别 URL 链接**，并根据上下文描述链接可能指向的内容。
    2. **归纳对话中的主要议题**，包括：
       - 活动相关：请明确活动的时间、地点、内容（如有）。
       - 游戏讨论：标明游戏名称、核心观点、争议与共识。
       - 技术/学习讨论：指出讨论的工具、语言、框架、问题与解决方案。
    3. **提取关键词句或经典语录**（如有趣或值得引用的内容）。

    请将结果按以下结构输出，使用标准 Markdown：

    ---

    **📌 群聊摘要**

    **主要议题：**
    - …

    **📎 链接说明：**
    - `[链接文本](URL)`：推测内容为…

    **💬 精选发言：**
    - “…”

    **🧠 关键词：**
    - …

    ---

    请确保语言简洁、不重复，必要时可适度补全信息（例如未明确说明的链接内容）。以下为原始对话内容：

    {chat_text}
    """

    # 调用 API 获取摘要
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
    
    # 生成词云
    generate_wordcloud(summary)  # 用摘要文本生成词云
    return summary