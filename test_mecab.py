#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

import MeCab

def mecab_sentance(sentence):
    mecab = MeCab.Tagger("-Ochasen")
    corpus = []
    output = mecab.parse(sentence)
    list = output.split('\n')
    for line in list:
        if len(line) > 4:
            group = line.split('\t')
            if '名詞' in group[3]:
                corpus.append(group[0] + '\t')
    string = ' '.join(corpus)
    return string


 # corpus=["我 来到 北京 清华大学",#第一类文本切词后的结果，词之间以空格隔开
 #        "他 来到 了 网易 杭研 大厦",#第二类文本的切词结果
 #        "小明 硕士 毕业 与 中国 科学院",#第三类文本的切词结果
 #        "我 爱 北京 天安门"]#第四类文本的切词结果
 #    vectorizer=CountVectorizer()#该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
 #    transformer=TfidfTransformer()#该类会统计每个词语的tf-idf权值
 #    tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))#第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
 #    word=vectorizer.get_feature_names()#获取词袋模型中的所有词语
 #    weight=tfidf.toarray()#将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
 #    for i in range(len(weight)):#打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
 #        print u"-------这里输出第",i,u"类文本的词语tf-idf权重------"
 #        for j in range(len(word)):
 #            print word[j],weight[i][j]

def tfidf_keywords(corpus):
    # 00、读取文件,一行就是一个文档，将所有文档输出到一个list中

    # 01、构建词频矩阵，将文本中的词语转换成词频矩阵
    vectorizer = CountVectorizer()
    # a[i][j]:表示j词在第i个文本中的词频
    X = vectorizer.fit_transform(corpus)
    print X  # 词频矩阵

    # 02、构建TFIDF权值
    transformer = TfidfTransformer()
    # 计算tfidf值
    tfidf = transformer.fit_transform(X)

    # 03、获取词袋模型中的关键词
    word = vectorizer.get_feature_names()

    # tfidf矩阵
    weight = tfidf.toarray()

    # 打印权重
    for i in range(len(weight)):
        print u"-------这里输出第", i, u"类文本的词语tf-idf权重------"
        for j in range(len(word)):
            print word[j],weight[i][j]
            # print '\n'

if __name__ == '__main__':
    all_corpus = []
    sentence = ['陳特定教授は「詳しい因果関係はわからないが、睡眠時無呼吸症候群を治療することで、高血圧や糖尿病の改善につながる可能性がある。',
                '来月開幕するサッカーワールドカップロシア大会で、日本代表が１次リーグの第３戦で対戦するポーランドの代表候補選手３５人が発表され、エースのレバンドフスキ選手などが順当に選ばれました。'
                ]
    for line in sentence:
        string = mecab_sentance(line)
        all_corpus.append(string)

    tfidf_keywords(all_corpus)
