# main.py
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import json
import sqlite3

def main():
    conn = sqlite3.connect('settings.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    conn.commit()

    def get_setting(key):
        cur.execute('SELECT value FROM settings WHERE key=?', (key,))
        row = cur.fetchone()
        return row[0] if row else ''

    def set_setting(key, value):
        cur.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()

    def handle_login():
        messagebox.showinfo("登录提醒", "将打开命令行窗口，请按空格确认账号并输入 no。")
        os.system("tdl login")

    def handle_fetch_chats():
        output = subprocess.check_output([r'C:\tdl\tdl.exe', 'chat', 'ls', '--proxy', 'http://localhost:7890'], text=True, encoding='utf-8')
        chat_listbox.delete(0, tk.END)
        for line in output.splitlines()[1:]:  # 跳过表头
            chat_listbox.insert(tk.END, line)

    def select_chat():
        selection = chat_listbox.get(chat_listbox.curselection())
        chat_id.set(selection.split()[0])
        messagebox.showinfo("选择成功", f"当前群聊ID：{chat_id.get()}")

    def handle_summary():
        export_type = export_var.get()
        cid = chat_id.get()
        if not cid:
            messagebox.showerror("错误", "请先选择群聊")
            return

        if export_type == "last":
            n = entry_last.get()
            cmd = [r'C:\tdl\tdl.exe', 'chat', 'export', '-c', cid, '-T', 'last', '-i', n,
                   '--proxy', 'http://localhost:7890', '--with-content', '--all']
        else:
            h = float(entry_hour.get())
            now = int(time.time())
            since = now - int(h * 3600)
            cmd = [r'C:\tdl\tdl.exe', 'chat', 'export', '-c', cid, '-T', 'time', '-i', f"{since},{now}",
                   '--proxy', 'http://localhost:7890', '--with-content', '--all']
        subprocess.run(cmd)

        # summarize
        with open("tdl-export.json", "r", encoding="utf-8") as f:
            js = json.load(f)
        all_text = "\n".join(m.get("text", "") for m in js["messages"] if "text" in m)

        from openai import OpenAI
        client = OpenAI(api_key=api_key.get(), base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个擅长总结聊天记录的助手"},
                {"role": "user", "content": f"""请总结以下对话内容：
- 若包含链接，尝试猜测其内容
- 若讨论活动，请提取时间与地点
- 若讨论游戏，请列出名称与要点
- 请使用 __斜体__、**强调**、~~删除线~~、```等宽```、||剧透|| 格式

内容：
{all_text}
"""}],
            stream=False
        )
        result = resp.choices[0].message.content
        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write(result)
        messagebox.showinfo("总结完成", "摘要已生成，将发送到群聊")
        subprocess.run([
            r'C:\tdl\tdl.exe', 'up', '-c', cid, '-p', 'summary.txt', '--proxy', 'http://localhost:7890'
        ])

        set_setting("api_key", api_key.get())
        set_setting("chat_id", cid)

    # GUI 主体
    root = tk.Tk()
    root.title("Telegram 聊天摘要助手")

    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", "聊天摘要助手 v1.0"))
    file_menu.add_separator()
    file_menu.add_command(label="退出", command=root.quit)
    menu_bar.add_cascade(label="设置", menu=file_menu)
    root.config(menu=menu_bar)

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    tk.Button(frame, text="登录", command=handle_login).grid(row=0, column=0)
    tk.Button(frame, text="查看群聊", command=handle_fetch_chats).grid(row=0, column=1)

    chat_listbox = tk.Listbox(frame, width=100)
    chat_listbox.grid(row=1, column=0, columnspan=2)
    tk.Button(frame, text="选择群聊", command=select_chat).grid(row=2, column=0, columnspan=2)

    chat_id = tk.StringVar()
    export_var = tk.StringVar(value="last")
    tk.Label(frame, text="导出方式：").grid(row=3, column=0)
    tk.Radiobutton(frame, text="最新N条", variable=export_var, value="last").grid(row=4, column=0)
    entry_last = tk.Entry(frame)
    entry_last.grid(row=4, column=1)
    tk.Radiobutton(frame, text="最近N小时", variable=export_var, value="time").grid(row=5, column=0)
    entry_hour = tk.Entry(frame)
    entry_hour.grid(row=5, column=1)

    tk.Label(frame, text="DeepSeek API Key：").grid(row=6, column=0)
    api_key = tk.StringVar()
    tk.Entry(frame, textvariable=api_key, width=50).grid(row=6, column=1)

    tk.Button(frame, text="执行总结", command=handle_summary).grid(row=7, column=0, columnspan=2)

    api_key.set(get_setting("api_key"))
    chat_id.set(get_setting("chat_id"))

    root.mainloop()

if __name__ == '__main__':
    main()