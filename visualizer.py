from wordcloud import WordCloud
#词云生成方法
def generate_wordcloud(text, output_path="wordclouds/wordcloud.png"):
    wc = WordCloud(
        font_path="msyh.ttc",  # 指定中文字体，若无可去掉此参数
        width=400, height=200,
        background_color="white",
        colormap="Blues"
    )
    wc.generate(text)
    wc.to_file(output_path)