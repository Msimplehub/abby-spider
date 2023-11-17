import gensim
from gensim.summarization import summarize

def generate_summary(text, ratio=0.2):
    # 使用gensim.summarization模块中的summarize函数来生成摘要
    summary = summarize(text, ratio=ratio)
    return summary

if __name__ == "__main__":
    text = "['这是一个很长的文本，包含了很多句子。这是摘要生成的测试。', '这个文本包含了很多信息，可以帮助我们更好地理解这个主题。']"
    print(generate_summary(text))
