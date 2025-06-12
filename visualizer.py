# visualizer.py

from wordcloud import WordCloud
import os


def generate_wordcloud(text: str, output_path="wordcloud.png"):
    """
    根据输入的文本生成词云图片。

    Args:
        text (str): 用于生成词云的文本。
        output_path (str): 生成的图片保存路径。
    """
    # 字体路径，msyh.ttc (微软雅黑) 是Windows自带的，其他系统可能需要自行下载
    font_path = "msyh.ttc"
    # 检查字体文件是否存在，如果不存在则不使用指定字体，避免报错
    if not os.path.exists(font_path):
        font_path = '/System/Library/Fonts/STHeiti Light.ttc'
        print(f"警告: 找不到字体文件 {font_path}。词云可能无法正确显示中文。")
        font_path = None  # WordCloud会使用默认字体

    wc = WordCloud(
        font_path=font_path,
        width=400,
        height=200,
        background_color="white",
        colormap="Blues",  # 使用蓝色系，更具科技感
        max_words=50,  # 最多显示50个词
        prefer_horizontal=0.9  # 词语更倾向于水平排列
    )

    # 使用传入的文本生成词云
    wc.generate(text)

    # 保存到文件
    wc.to_file(output_path)
    print(f"词云已生成并保存至 {output_path}")