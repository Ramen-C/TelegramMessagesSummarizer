## Telegram AI 群聊助手 (TG-Summarizer)
本项目是一个基于 tdl 和 AI 大语言模型的 Telegram 群聊摘要工具。它提供了一个简单的图形化界面（GUI），能够授权登录您的 Telegram 账户，导出指定群聊的聊天记录，利用 AI 进行分析和总结，并将结构化的摘要报告发送回指定的聊天中，帮助用户快速了解群聊的核心内容。

### 项目原理
本工具的核心逻辑串联了四个主要步骤，构成了一个自动化的信息处理流水线：

- 导出 (Export)：用户在图形界面中选择一个群聊和导出范围（如“最近1000条”或“最近24小时”）。程序会调用 tdl 命令行工具，将指定范围内的聊天记录导出为 tdl-export.json 文件。
- 过滤 (Filter)：导出的原始 JSON 文件包含了所有类型的消息。filter.py 模块会读取这个文件，并过滤掉非文本内容（如贴纸、动图等），仅保留有效的文本消息，生成一个精简后的 tdl-export-filtered.json 文件。
- 总结 (Summarize)：summarizer.py 模块读取过滤后的文本内容，将其整合后发送给 AI 大模型（当前默认使用 DeepSeek API）。AI 会根据预设的提示词（Prompt）对内容进行结构化分析，提取主要议题、链接、关键发言和关键词，并生成一份 Markdown 格式的摘要。
- 转发 (Forward)：forwarder.py 模块会将 AI 生成的摘要内容保存为一个 summary.txt 文件，并再次调用 tdl 工具，将这个文件上传到用户指定的目标群聊中，完成整个流程。

### 功能特性
- 图形化界面：使用 Tkinter 构建。
- 灵活的聊天记录导出：支持按“最新消息数量”或“最近时间段（小时）”两种模式导出。
- 智能摘要：利用 DeepSeek 大模型对聊天内容进行高质量的结构化总结，自动提取议题、链接和金句。
- 自动化流程：一键完成从导出到转发的全过程。
- 代理支持：支持通过 config.json 文件配置 HTTP 代理。

### 核心引擎
Telegram 交互核心：iyear/tdl。
AI 总结引擎：DeepSeek、OpenAI、Gemini。
图形界面库：Tkinter。

### 安装与配置
在开始之前，请确保您的系统环境已准备就绪。

步骤 1：安装 tdl
tdl 是本项目的核心依赖，必须先在您的系统中安装。请根据您的操作系统选择合适的安装方式。

macOS / Linux：
打开终端，运行以下一键安装脚本。
```bash
curl -sSL https://docs.iyear.me/tdl/install.sh | sudo bash
```

Windows:
```bash
iwr -useb https://docs.iyear.me/tdl/install.ps1 | iex
```

步骤 2：克隆本项目并安装依赖
```bash
git clone <你的项目仓库地址>
cd <项目目录>
```
步骤 3：配置
项目根目录下有两个关键的配置文件：
```json
config.json:
{
  "tdl_path": "tdl",
  "proxy": "http://localhost:7890"
}
```
tdl_path: tdl 可执行文件的路径。如果已将其添加到系统环境变量，则保持默认的 "tdl" 即可。否则，请填写其完整路径（例如 D:\\apps\\tdl.exe）。
proxy: 如果您需要通过代理访问 Telegram，请在此处填写您的代理地址。如果不需要，请设置为空字符串 ""。

summarizer.py (API Key 配置):
目前，AI 的 API Key 硬编码在 summarizer.py 文件中。请打开该文件，找到以下行并替换为您自己的 DeepSeek API Key：
```python
client = OpenAI(
    api_key='', # <-- 在这里替换成你的 KEY
    base_url="https://api.deepseek.com"
)
```
步骤 4：首次登录 Telegram
在运行主程序之前，您必须先通过 tdl 登录您的 Telegram 账户。

打开终端（或 Windows 的 PowerShell/CMD），运行以下命令：

```bash
tdl login
```

展望未来 (Future Work)
本项目未来计划加入以下功能以提升用户体验和扩展性：

多 AI 模型支持：允许用户在配置中自由选择和切换不同的 AI 服务商，如 OpenAI(ChatGPT)、Anthropic(Claude)、Google(Gemini) 等。
多平台支持：探索接入更多聊天平台（如 Discord, Slack 等），可能通过集成 NoneBot 或 Koishi 等框架实现。
实时进度显示：在主界面的特定区域实时回显 tdl 等命令行工具的输出，让用户清晰地了解当前任务的执行进度。
界面内摘要预览：总结完成后，除了将结果转发到 Telegram，同时也在主界面中直接显示摘要内容，方便用户即时查看。

