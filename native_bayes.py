#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import matplotlib.pyplot as plt
import re
import os
import MeCab
import random
import chardet
import sys

NUMBER = 30

def mecab_sentance(sentence):
    mecab = MeCab.Tagger("-Ochasen")
    corpus = []
    output = mecab.parse(sentence)
    list = output.split('\n')
    for line in list:
        if len(line) > 4:
            group = line.split('\t')
            if '名詞' in group[3] and len(group[0])>2:
                corpus.append(group[0] + '\t')
    string = ' '.join(corpus)
    return string
#########################################################  for user use
def StringProcessing(string):
    word_cut = mecab_sentance(string)
    word_list = word_cut.split('\t')
    return word_list

def StringFeature(word_list,feature_words):
    def text_features(text, feature_words):                        #出现在特征集中，则置1
        text_words = set(text)
        features = [1 if word in text_words else 0 for word in feature_words]
        return features
    word_feature_list = [text_features(word_list, feature_words)]
    return word_feature_list

def StringClassify(train_feature_list, word_feature_list, train_class_list):
    classifier = MultinomialNB().fit(train_feature_list, train_class_list)
    tag = classifier.predict(word_feature_list)
    return tag

#########################################################   for research
def TextProcessing(folder_path, test_size = 0.2):
    folder_list = os.listdir(folder_path)                        #查看folder_path下的文件
    data_list = []                                                #训练集
    class_list = []
    #遍历每个子文件夹
    for folder in folder_list:
        if '.DS_Store' not in folder:
            new_folder_path = os.path.join(folder_path, folder)        #根据子文件夹，生成新的路径
            files = os.listdir(new_folder_path)                        #存放子文件夹下的txt文件的列表
            #遍历每个txt文件
            for file in files:
                if folder in file:
                    with open(os.path.join(new_folder_path, file), 'r') as f:
                        raw = f.read()
                    word_cut = mecab_sentance(raw)
                    word_list = word_cut.split('\t')
                    data_list.append(word_list)
                    class_list.append(folder)

    for line in data_list:
        print('one folder overall---------------------------')
        print(' '.join(line))
    print(class_list)

    data_class_list = list(zip(data_list, class_list))  # zip压缩合并，将数据与标签对应压缩
    random.shuffle(data_class_list)  # 将data_class_list乱序
    index = int(len(data_class_list) * test_size) + 1  # 训练集和测试集切分的索引值
    train_list = data_class_list[index:]  # 训练集
    test_list = data_class_list[:index]  # 测试集
    train_data_list, train_class_list = zip(*train_list)  # 训练集解压缩
    test_data_list, test_class_list = zip(*test_list)  # 测试集解压缩

    all_words_dict = {}                    #统计训练集词频
    for word_list in train_data_list:
        for word in word_list:
            if word in all_words_dict.keys():
                all_words_dict[word] += 1
            else:
                all_words_dict[word] = 1

    all_words_tuple_list = sorted(all_words_dict.items(), key=lambda f: f[1], reverse=True)
    all_words_list, all_words_nums = zip(*all_words_tuple_list)  # 解压缩
    all_words_list = list(all_words_list)  # 转换成列表
    return all_words_list, train_data_list, test_data_list, train_class_list, test_class_list

def MakeWordsSet(words_file):
    words_set = set()                       #创建set集合
    with open(words_file, 'r') as f:        #打开文件
        for line in f.readlines():
            word = line.strip()             #去回车
            if len(word) > 0:               #有文本，则添加到words_set中
                words_set.add(word)
    return words_set                        #返回处理结果

def words_dict(all_words_list, deleteN, stopwords_set = set()):
    feature_words = []                            #特征列表
    n = 1
    for t in range(deleteN, len(all_words_list), 1):
        if n > 1000:                            #feature_words的维度为1000
            break
        if  all_words_list[t] not in stopwords_set and 1 < len(all_words_list[t]):
            feature_words.append(all_words_list[t])
        n += 1
    return feature_words

def TextClassifier(train_feature_list, test_feature_list, train_class_list, test_class_list):
    classifier = MultinomialNB().fit(train_feature_list, train_class_list)
    test_accuracy = classifier.score(test_feature_list, test_class_list)
    return test_accuracy

def TextFeatures(train_data_list, test_data_list, feature_words):
    def text_features(text, feature_words):                        #出现在特征集中，则置1
        text_words = set(text)
        features = [1 if word in text_words else 0 for word in feature_words]
        return features
    train_feature_list = [text_features(text, feature_words) for text in train_data_list]
    test_feature_list = [text_features(text, feature_words) for text in test_data_list]
    return train_feature_list, test_feature_list                    #返回结果

if __name__ == '__main__':
    #文本预处理
    folder_path = './nhk_news'                #训练集存放地址
    all_words_list, train_data_list, test_data_list, train_class_list, test_class_list = TextProcessing(folder_path, test_size=0.2)
    print('下面是词典-----------------------')
    print('\t'.join(all_words_list))

    stopwords_file = './stopwords'
    stopwords_set = MakeWordsSet(stopwords_file)

    #feature_words = words_dict(all_words_list, 100, stopwords_set)
    #print('下面是文本的特征------------------')
    #print('\t'.join(feature_words))

    test_accuracy_list = []
    deleteNs = range(1, 1000, 3)
    for deleteN in deleteNs:
        feature_words = words_dict(all_words_list, deleteN, stopwords_set)
        train_feature_list, test_feature_list = TextFeatures(train_data_list, test_data_list, feature_words)
        print('下面是文本的特征------------------')
        print('\t'.join(feature_words))
        test_accuracy = TextClassifier(train_feature_list, test_feature_list, train_class_list, test_class_list)
        print ('accuracy:',test_accuracy)
        test_accuracy_list.append(test_accuracy)

    print('------------系统成功初始化，已寻找到最优文本特征-------------')
    feature_words = words_dict(all_words_list, NUMBER, stopwords_set)
    train_feature_list, test_feature_list = TextFeatures(train_data_list, test_data_list, feature_words)
    string = raw_input('请输入想要预测的日文文本：')
    word_list = StringProcessing(string)
    word_feature_list = StringFeature(word_list, feature_words)
    result = StringClassify(train_feature_list, word_feature_list, train_class_list)
    print(result)

    plt.figure()
    plt.plot(deleteNs, test_accuracy_list)
    plt.title('Relationship of deleteNs and test_accuracy')
    plt.xlabel('deleteNs')
    plt.ylabel('test_accuracy')
    plt.show()
