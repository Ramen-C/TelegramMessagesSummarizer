import tkinter as tk
from tkinter import  ttk, messagebox
import chat_selector, exporter, summarizer, forwarder
from filter import filter_messages
from PIL import Image, ImageTk
from visualizer import generate_wordcloud

def main():
    root = tk.Tk()
    root.title("Telegram 群聊助手")
    root.geometry("800x600")

    # 左侧：载入群聊、导出设置、开始总结按钮
    left_frame = ttk.Frame(root, padding=10)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)


    # 载入群聊按钮事件
    def load_chats():
        try:
            chats = chat_selector.list_chats()
            # 清空表格
            for item in tree.get_children():
                tree.delete(item)
            # 插入群聊列表
            for chat in chats:
                tree.insert("", tk.END, values=(
                    chat['id'],  # 群聊ID
                    chat['type'],  # 群聊类型
                    chat['visible_name'],  # 显示名称
                    chat.get('username', '-'),  # 用户名（可能不存在）
                ))
        except Exception as e:
            messagebox.showinfo("成功", f"已载入 {len(chats)} 个群聊")

    load_button = ttk.Button(left_frame, text="载入群聊", command=load_chats)
    load_button.pack(fill=tk.X, pady=5)

    # 导出设置：单选按钮和数字输入框
    export_frame = ttk.LabelFrame(left_frame, text="导出设置", padding=10)
    export_frame.pack(fill=tk.X, pady=5)
    mode_var = tk.StringVar()
    rb_msgs = ttk.Radiobutton(export_frame, text="最近 N 条", variable=mode_var, value="msgs")
    rb_hours = ttk.Radiobutton(export_frame, text="最近 N 小时", variable=mode_var, value="hours")
    rb_msgs.pack(anchor=tk.W)
    rb_hours.pack(anchor=tk.W)
    input_frame = ttk.Frame(export_frame)
    input_frame.pack(fill=tk.X, pady=2)
    ttk.Label(input_frame, text="N = ").pack(side=tk.LEFT)
    number_var = tk.IntVar()
    entry = ttk.Entry(input_frame, textvariable=number_var, state="disabled", width=10)
    entry.pack(side=tk.LEFT, padx=5)
    def on_mode_change():
        entry.config(state="normal")
    rb_msgs.config(command=on_mode_change)
    rb_hours.config(command=on_mode_change)

    # 收藏夹设置，待补充
    '''
    to_fav_var = tk.BooleanVar()
    to_fav_check = ttk.Checkbutton(export_frame, text="导出到收藏夹", variable=to_fav_var)
    to_fav_check.pack(anchor=tk.W)
    '''
    

    # N 下方显示当前选中群组的 VisibleName
    group_name_label = ttk.Label(export_frame, text="未选择群聊")
    group_name_label.pack(fill=tk.X, pady=(2, 5))

    # 合并导出目标设置
    custom_target_var = tk.BooleanVar(value=False)
    def on_custom_target():
        if custom_target_var.get():
            chat_target_entry.config(state="normal")
        else:
            chat_target_entry.config(state="disabled")
    custom_target_check = ttk.Checkbutton(
        export_frame, text="自选导出目标", variable=custom_target_var, command=on_custom_target
    )
    custom_target_check.pack(anchor=tk.W, pady=(10, 0))

    chat_target_var = tk.StringVar()
    chat_target_entry = ttk.Entry(export_frame, textvariable=chat_target_var, width=30, state="disabled")
    chat_target_entry.pack(anchor=tk.W)

    # 设置 placeholder 功能
    def set_placeholder():
        if not chat_target_var.get():
            chat_target_entry.config(state="normal")
            chat_target_entry.delete(0, tk.END)
            chat_target_entry.insert(0, "默认导出到收藏夹")
            chat_target_entry.config(foreground="gray")
            chat_target_entry.config(state="disabled")

    def clear_placeholder(event=None):
       if chat_target_entry.get() == "默认导出到收藏夹":
            chat_target_entry.config(state="normal")
            chat_target_entry.delete(0, tk.END)
            chat_target_entry.config(foreground="black")

    def on_custom_target():
        if custom_target_var.get():
            chat_target_entry.config(state="normal")
            clear_placeholder()
        else:
            set_placeholder()

   # 绑定 Entry 获取焦点时清除 placeholder
    chat_target_entry.bind("<FocusIn>", clear_placeholder)
    chat_target_entry.bind("<FocusOut>", lambda e: set_placeholder() if not chat_target_var.get() and custom_target_var.get() else None)

    # 初始化 placeholder
    set_placeholder()

    # 右侧区域增加词云展示
    wordcloud_label = ttk.Label(right_frame, text="摘要词云：")
    wordcloud_label.pack(anchor=tk.W, pady=(8, 0))
    wordcloud_canvas = tk.Label(right_frame)
    wordcloud_canvas.pack(fill=tk.X, pady=(0, 8))

    def show_wordcloud(img_path="wordcloud.png"):
        img = Image.open(img_path)
        img = img.resize((300, 150))
        img_tk = ImageTk.PhotoImage(img)
        wordcloud_canvas.config(image=img_tk)
        wordcloud_canvas.image = img_tk  # 防止被垃圾回收


    # 开始总结按钮事件
    def start_summary():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("未选择群聊", "请先选择一个群聊")
            return
        if mode_var.get() == "":
            messagebox.showwarning("未选择导出方式", "请选择导出方式")
            return
        chat_id = tree.item(selected[0])['values'][0]
        try:
            n = number_var.get()
            if n <= 0:
                raise ValueError("N 必须为正整数")
            if mode_var.get() == "msgs":
                exporter.export_chat(chat_id, last_n=n)
            else:
                exporter.export_chat(chat_id, last_n_hours=n)
            filter_messages()
            summary_text = summarizer.summarize_chat()
            show_wordcloud("wordcloud.png")
            # 判断导出目标
            if custom_target_var.get():
                target = chat_target_var.get().strip()
                if not target:
                    raise ValueError("请填写导出目标 CHAT")
            else:
                target = "FAVORITES"  # 你可以根据业务实际调整
            forwarder.forward_summary(target, summary_text)
            messagebox.showinfo("成功", "摘要已发送到群聊")
            messagebox.showinfo("成功", "摘要生成并展示词云！")
        except Exception as e:
            messagebox.showerror("错误", f"总结失败: {e}")

    summary_button = ttk.Button(left_frame, text="开始总结", command=start_summary)
    summary_button.pack(fill=tk.X, pady=5)

    # 右侧：群聊列表表格和选中群聊信息
    right_frame = ttk.Frame(root, padding=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    columns = ("ID", "Type", "VisibleName", "Username")
    tree = ttk.Treeview(right_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.W)
    # 绑定选中事件，更新 group_name_label
    def on_chat_select(event):
        sel = tree.selection()
        if sel:
            item = tree.item(sel[0])
            vals = item['values']
            cid, cname = vals[0], vals[2]
            selected_label.config(text=f"选中群聊: ID={cid}, 名称={cname}")
            group_name_label.config(text=f"当前群组: {cname}")
    tree.bind("<<TreeviewSelect>>", on_chat_select)
    scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    selected_label = ttk.Label(right_frame, text="未选择群聊")
    selected_label.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    root.mainloop()

if __name__ == "__main__":
    main()