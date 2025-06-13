import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.scrolledtext as scrolledtext
from PIL import Image, ImageTk
import json
from pathlib import Path

# 项目模块导入
import chat_selector, exporter, summarizer, forwarder
from filter import filter_and_format_messages
from visualizer import generate_wordcloud

CONFIG_FILE = Path("config.json")


def load_config():
    """加载配置文件，如果文件不存在，则创建默认文件。"""
    default_config = {
        "tdl_path": "tdl",
        "proxy": "",
        "api": "sk-..."
    }
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("配置错误", "config.json 文件损坏，将使用默认配置。")
            return default_config


def save_config(config_data):
    """保存配置到文件。"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)


def open_settings_window(parent):
    """打开最终简化的设置窗口。"""
    settings_win = tk.Toplevel(parent)
    settings_win.title("设置")
    settings_win.geometry("480x200")  # 窗口高度减小
    settings_win.resizable(False, False)
    settings_win.transient(parent)
    settings_win.grab_set()

    config = load_config()

    tdl_path_var = tk.StringVar(value=config.get("tdl_path", "tdl"))
    proxy_var = tk.StringVar(value=config.get("proxy", ""))
    api_key_var = tk.StringVar(value=config.get("api", ""))

    main_frame = ttk.Frame(settings_win, padding=15)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="TDL 路径:").grid(row=0, column=0, sticky=tk.W, pady=4)
    ttk.Entry(main_frame, textvariable=tdl_path_var, width=40).grid(row=0, column=1, sticky=tk.EW)

    ttk.Label(main_frame, text="代理地址:").grid(row=1, column=0, sticky=tk.W, pady=4)
    ttk.Entry(main_frame, textvariable=proxy_var, width=40).grid(row=1, column=1, sticky=tk.EW)

    ttk.Label(main_frame, text="DeepSeek API Key:").grid(row=2, column=0, sticky=tk.W, pady=4)
    ttk.Entry(main_frame, textvariable=api_key_var, width=40, show="*").grid(row=2, column=1, sticky=tk.EW)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky=tk.E)

    def save_and_close():
        new_config = {
            "tdl_path": tdl_path_var.get(),
            "proxy": proxy_var.get(),
            "api": api_key_var.get()
        }
        save_config(new_config)
        messagebox.showinfo("成功", "设置已保存！", parent=settings_win)
        settings_win.destroy()

    ttk.Button(button_frame, text="保存", command=save_and_close, style="Accent.TButton").pack(side=tk.RIGHT)
    ttk.Button(button_frame, text="取消", command=settings_win.destroy).pack(side=tk.RIGHT, padx=10)


def main():
    root = tk.Tk()
    root.title("Telegram AI 群聊助手 (Deepseek Reasoner 专用版)")
    root.geometry("960x720")

    left_frame = ttk.Frame(root, padding=10, width=280)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
    left_frame.pack_propagate(False)

    right_frame = ttk.Frame(root, padding=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def load_chats():
        try:
            chats = chat_selector.list_chats()
            for item in tree.get_children(): tree.delete(item)
            for chat in chats: tree.insert("", tk.END, values=(
            chat['id'], chat['type'], chat['visible_name'], chat.get('username', '-')))
            messagebox.showinfo("成功", f"已载入 {len(chats)} 个群聊")
        except Exception as e:
            messagebox.showerror("错误", f"载入群聊失败: {e}")

    load_button = ttk.Button(left_frame, text="载入群聊", command=load_chats)
    load_button.pack(fill=tk.X, pady=5)

    export_frame = ttk.LabelFrame(left_frame, text="导出设置", padding=10)
    export_frame.pack(fill=tk.X, pady=5)
    mode_var = tk.StringVar(value="msgs")
    number_var = tk.IntVar(value=100)
    ttk.Radiobutton(export_frame, text="最近 N 条", variable=mode_var, value="msgs").pack(anchor=tk.W)
    ttk.Radiobutton(export_frame, text="最近 N 小时", variable=mode_var, value="hours").pack(anchor=tk.W)
    input_frame = ttk.Frame(export_frame)
    input_frame.pack(fill=tk.X, pady=2, anchor=tk.W)
    ttk.Label(input_frame, text="N = ").pack(side=tk.LEFT)
    ttk.Entry(input_frame, textvariable=number_var, width=10).pack(side=tk.LEFT, padx=5)
    group_name_label = ttk.Label(export_frame, text="未选择群聊", foreground="blue")
    group_name_label.pack(fill=tk.X, pady=(5, 5))

    forward_frame = ttk.LabelFrame(left_frame, text="转发设置", padding=10)
    forward_frame.pack(fill=tk.X, pady=5)
    custom_target_var = tk.BooleanVar(value=False)
    chat_target_var = tk.StringVar()
    chat_target_entry = ttk.Entry(forward_frame, textvariable=chat_target_var, width=28, state="disabled")

    def on_custom_target_toggle():
        if custom_target_var.get():
            chat_target_entry.config(state="normal")
            if chat_target_entry.get() == "默认转发到“收藏夹”": chat_target_entry.delete(0, tk.END)
        else:
            chat_target_entry.delete(0, tk.END)
            chat_target_entry.insert(0, "默认转发到“收藏夹”")
            chat_target_entry.config(state="disabled")

    ttk.Checkbutton(forward_frame, text="转发到指定目标 (填Chat ID)", variable=custom_target_var,
                    command=on_custom_target_toggle).pack(anchor=tk.W)
    chat_target_entry.pack(anchor=tk.W, pady=(5, 0))
    on_custom_target_toggle()

    def start_summary():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("操作无效", "请先在右侧列表中选择一个群聊。")
            return

        chat_id = tree.item(selected[0])['values'][0]

        try:
            n = number_var.get()
            if n <= 0: raise ValueError("N 必须为正整数")

            summary_text_widget.config(state="normal");
            summary_text_widget.delete('1.0', tk.END);
            summary_text_widget.config(state="disabled")
            wordcloud_canvas.config(image=None);
            wordcloud_canvas.image = None
            root.update_idletasks()

            messagebox.showinfo("处理中", "正在导出和分析消息，请稍候...", )

            if mode_var.get() == "msgs":
                exporter.export_chat(chat_id, last_n=n)
            else:
                exporter.export_chat(chat_id, last_n_hours=n)

            formatted_messages = filter_and_format_messages()
            if not formatted_messages: raise ValueError("过滤后没有找到有效的文本消息。")

            summary_text = summarizer.summarize_chat(formatted_messages)

            summary_text_widget.config(state="normal");
            summary_text_widget.insert('1.0', summary_text);
            summary_text_widget.config(state="disabled")

            generate_wordcloud(summary_text, "wordcloud.png")
            img = Image.open("wordcloud.png");
            img_tk = ImageTk.PhotoImage(img)
            wordcloud_canvas.config(image=img_tk);
            wordcloud_canvas.image = img_tk

            # --- 核心改动：转发逻辑彻底简化 ---
            if custom_target_var.get():
                target_id = chat_target_var.get().strip()
                if not target_id:
                    raise ValueError("您已勾选自选目标，请填写有效的 Chat ID。")
            else:
                # 默认收藏夹
                target_id = ""

            forwarder.forward_summary(target_id, summary_text)
            messagebox.showinfo("成功", "摘要已在界面显示，并成功转发！")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {e}")

    summary_button = ttk.Button(left_frame, text="开始总结", command=start_summary, style="Accent.TButton")
    summary_button.pack(fill=tk.X, pady=20)
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))

    settings_button = ttk.Button(left_frame, text="⚙️ 设置", command=lambda: open_settings_window(root))
    settings_button.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    tree_frame = ttk.LabelFrame(right_frame, text="群聊列表 (请点击选择)", padding=10)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
    columns = ("ID", "Type", "VisibleName", "Username")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns: tree.heading(col, text=col); tree.column(col, width=150, anchor=tk.W)

    def on_chat_select(event):
        sel = tree.selection()
        if sel: group_name_label.config(text=f"当前群组: {tree.item(sel[0])['values'][2]}")

    tree.bind("<<TreeviewSelect>>", on_chat_select)
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    results_frame = ttk.LabelFrame(right_frame, text="摘要结果", padding=10)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    results_frame.grid_rowconfigure(0, weight=1);
    results_frame.grid_columnconfigure(0, weight=3);
    results_frame.grid_columnconfigure(1, weight=2)
    summary_text_widget = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state="disabled",
                                                    font=("Helvetica", 10))
    summary_text_widget.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    wordcloud_frame = ttk.Frame(results_frame)
    wordcloud_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    ttk.Label(wordcloud_frame, text="核心词云", font=("Helvetica", 11, "bold")).pack(pady=5)
    wordcloud_canvas = tk.Label(wordcloud_frame)
    wordcloud_canvas.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()