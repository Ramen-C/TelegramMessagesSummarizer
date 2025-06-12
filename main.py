# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.scrolledtext as scrolledtext
from PIL import Image, ImageTk

# 项目模块导入
import chat_selector, exporter, summarizer, forwarder
from filter import filter_and_format_messages
from visualizer import generate_wordcloud


def main():
    root = tk.Tk()
    root.title("Telegram AI 群聊助手")
    root.geometry("960x720")  # 适当增大了窗口尺寸

    # --- 界面布局调整 ---
    # 左侧控制面板
    left_frame = ttk.Frame(root, padding=10, width=280)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
    left_frame.pack_propagate(False)  # 防止 left_frame 自动缩放

    # 右侧主内容区
    right_frame = ttk.Frame(root, padding=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # --- 左侧面板 (控制区) ---

    # 载入群聊按钮事件
    def load_chats():
        try:
            # chat_selector.list_chats() 现在返回一个处理好的字典列表
            chats = chat_selector.list_chats()
            if not chats:
                messagebox.showwarning("未找到群聊", "未能从 tdl 获取到任何群聊信息。")
                return

            # 清空旧的列表
            for item in tree.get_children():
                tree.delete(item)

            # 插入新的群聊列表
            for chat in chats:
                # --- 核心改动：使用小写的字典键来获取数据 ---
                tree.insert("", tk.END, values=(
                    chat['id'],  # 使用 'id' 而不是 'ID'
                    chat['type'],  # 使用 'type' 而不是 'TYPE'
                    chat['visible_name'],  # 使用 'visible_name'
                    chat.get('username', '-')  # .get() 方法保持不变，很健壮
                ))
            messagebox.showinfo("成功", f"已载入 {len(chats)} 个群聊")
        except Exception as e:
            messagebox.showerror("错误", f"载入群聊失败: {e}")

    load_button = ttk.Button(left_frame, text="载入群聊", command=load_chats)
    load_button.pack(fill=tk.X, pady=5)

    # 导出设置
    export_frame = ttk.LabelFrame(left_frame, text="导出设置", padding=10)
    export_frame.pack(fill=tk.X, pady=5)
    mode_var = tk.StringVar(value="msgs")  # 默认选中"最近N条"
    entry = ttk.Entry(export_frame, state="normal", width=10)  # 默认可用

    def on_mode_change():  # 简单逻辑，保持 entry 可用即可
        entry.config(state="normal")

    rb_msgs = ttk.Radiobutton(export_frame, text="最近 N 条", variable=mode_var, value="msgs", command=on_mode_change)
    rb_hours = ttk.Radiobutton(export_frame, text="最近 N 小时", variable=mode_var, value="hours",
                               command=on_mode_change)
    rb_msgs.pack(anchor=tk.W)
    rb_hours.pack(anchor=tk.W)
    input_frame = ttk.Frame(export_frame)
    input_frame.pack(fill=tk.X, pady=2, anchor=tk.W)
    ttk.Label(input_frame, text="N = ").pack(side=tk.LEFT)
    number_var = tk.IntVar(value=100)  # 默认值100
    entry.config(textvariable=number_var)
    entry.pack(side=tk.LEFT, padx=5)

    group_name_label = ttk.Label(export_frame, text="未选择群聊", foreground="blue")
    group_name_label.pack(fill=tk.X, pady=(5, 5))

    # 转发目标设置
    forward_frame = ttk.LabelFrame(left_frame, text="转发设置", padding=10)
    forward_frame.pack(fill=tk.X, pady=5)
    custom_target_var = tk.BooleanVar(value=False)
    chat_target_var = tk.StringVar()
    chat_target_entry = ttk.Entry(forward_frame, textvariable=chat_target_var, width=28, state="disabled")

    def on_custom_target_toggle():
        if custom_target_var.get():
            chat_target_entry.config(state="normal")
            if chat_target_entry.get() == "默认转发到“收藏夹”":
                chat_target_entry.delete(0, tk.END)
                chat_target_entry.config(foreground="black")
        else:
            chat_target_entry.delete(0, tk.END)
            chat_target_entry.insert(0, "默认转发到“收藏夹”")
            chat_target_entry.config(foreground="gray", state="disabled")

    custom_target_check = ttk.Checkbutton(
        forward_frame, text="转发到指定目标 (填Chat ID)", variable=custom_target_var, command=on_custom_target_toggle
    )
    custom_target_check.pack(anchor=tk.W)
    chat_target_entry.pack(anchor=tk.W, pady=(5, 0))
    on_custom_target_toggle()  # 初始化placeholder

    # 开始总结按钮
    def start_summary():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("操作无效", "请先在右侧列表中选择一个群聊。")
            return

        chat_id = tree.item(selected[0])['values'][0]

        try:
            n = number_var.get()
            if n <= 0:
                raise ValueError("N 必须为正整数")

            # 清空上次的结果
            summary_text_widget.config(state="normal")
            summary_text_widget.delete('1.0', tk.END)
            summary_text_widget.config(state="disabled")
            wordcloud_canvas.config(image=None)
            wordcloud_canvas.image = None
            root.update_idletasks()  # 强制刷新界面

            messagebox.showinfo("处理中", "正在导出和分析消息，请稍候...", )

            # 步骤 1: 导出
            if mode_var.get() == "msgs":
                exporter.export_chat(chat_id, last_n=n)
            else:
                exporter.export_chat(chat_id, last_n_hours=n)

            # 步骤 2: 过滤和格式化
            formatted_messages = filter_and_format_messages()
            if not formatted_messages:
                raise ValueError("过滤后没有找到有效的文本消息，请检查导出范围或聊天记录。")

            # 步骤 3: 总结
            summary_text = summarizer.summarize_chat(formatted_messages)

            # --- 核心改动：在总结成功后更新UI ---
            # 3.1 更新文本框内容
            summary_text_widget.config(state="normal")
            summary_text_widget.insert('1.0', summary_text)
            summary_text_widget.config(state="disabled")

            # 3.2 生成并显示词云
            generate_wordcloud(summary_text, "wordcloud.png")
            img = Image.open("wordcloud.png")
            img_tk = ImageTk.PhotoImage(img)
            wordcloud_canvas.config(image=img_tk)
            wordcloud_canvas.image = img_tk  # 防止被垃圾回收

            # 步骤 4: 转发
            target = chat_target_var.get().strip() if custom_target_var.get() else ""  # "me" 通常是收藏夹
            if custom_target_var.get() and not target:
                raise ValueError("您勾选了自选目标，但未填写有效的 Chat ID。")

            forwarder.forward_summary(target, summary_text)
            messagebox.showinfo("成功", "摘要已在界面显示，并成功转发！")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {e}")

    summary_button = ttk.Button(left_frame, text="开始总结", command=start_summary, style="Accent.TButton")
    summary_button.pack(fill=tk.X, pady=20)
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))

    # --- 右侧面板 (内容展示区) ---

    # 上半部分：群聊列表
    tree_frame = ttk.LabelFrame(right_frame, text="群聊列表 (请点击选择)", padding=10)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
    columns = ("ID", "Type", "VisibleName", "Username")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor=tk.W)

    def on_chat_select(event):
        sel = tree.selection()
        if sel:
            cname = tree.item(sel[0])['values'][2]
            group_name_label.config(text=f"当前群组: {cname}")

    tree.bind("<<TreeviewSelect>>", on_chat_select)
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 下半部分：摘要和词云
    results_frame = ttk.LabelFrame(right_frame, text="摘要结果", padding=10)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    results_frame.grid_rowconfigure(0, weight=1)
    results_frame.grid_columnconfigure(0, weight=3)  # 文本区占更大空间
    results_frame.grid_columnconfigure(1, weight=2)

    # 摘要文本显示区
    summary_text_widget = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state="disabled",
                                                    font=("Helvetica", 10))
    summary_text_widget.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    # 词云显示区
    wordcloud_frame = ttk.Frame(results_frame)
    wordcloud_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    ttk.Label(wordcloud_frame, text="核心词云", font=("Helvetica", 11, "bold")).pack(pady=5)
    wordcloud_canvas = tk.Label(wordcloud_frame)
    wordcloud_canvas.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()