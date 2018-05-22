#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import re
import os
import numpy as np
import MeCab
import random
import chardet
import sys
import argparse
from sklearn import metrics
import tensorflow as tf
import pandas

tf.logging.set_verbosity(tf.logging.INFO)
learn = tf.contrib.learn

FLAGS = None

MAX_DOCUMENT_LENGTH = 100

MIN_WORD_FREQUENCY = 1

EMBEDDING_SIZE = 20

N_FILTERS = 10

WINDOWS_SIZE = 20

FILTER_SHAPE1 = [WINDOWS_SIZE, EMBEDDING_SIZE]
FILTER_SHAPE2 = [WINDOWS_SIZE,N_FILTERS]

POOLING_WINDOW = 4
POOLING_STRIDE = 2
n_words = 0

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

def MakeWordsSet(words_file):
    words_set = set()                                            #创建set集合
    with open(words_file, 'r') as f:        #打开文件
        for line in f.readlines():                                #一行一行读取
            word = line.strip()                                    #去回车
            if len(word) > 0:                                    #有文本，则添加到words_set中
                words_set.add(word)
    return words_set

def TextProcessing(folder_path):
    global n_words
    folder_list = os.listdir(folder_path)                        #查看folder_path下的文件
    sentence = []                                                #训练集
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
                    if len(word_cut) > 1:
                        sentence.append((word_cut, folder))

    for line in sentence:
        print('one folder overall---------------------------')
        print(line)

    x, y = zip(*sentence)
    train_data, test_data, train_target, test_target = train_test_split(x, y, test_size = 0.2, random_state= 0 )

    vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH, min_frequency=MIN_WORD_FREQUENCY)
    x_train = np.array(list(vocab_processor.fit_transform(train_data)))
    x_test = np.array(list(vocab_processor.transform(test_data)))
    n_words = len(vocab_processor.vocabulary_)
    print('total words: %d' % n_words)

    cate_dic = {'culture':1, 'politics':2, 'social':3, 'sports':4, 'weather':5}
    train_target = map(lambda x:cate_dic[x], train_target)
    test_target = map(lambda x:cate_dic[x], test_target)
    y_train = pandas.Series(train_target)
    y_test = pandas.Series(test_target)

    return x_train, x_test, y_train, y_test

def cnn_model(features, target):
    #2层卷积神经网络
    #[n_words, EMBEDDING_SIZE]映射矩阵
    target = tf.one_hot(target, 15, 1, 0)
    word_vectors = tf.contrib.layers.embed_sequence(
        features, vocab_size=n_words, embed_dim=EMBEDDING_SIZE, scope='word')
    word_vectors = tf.expand_dims(word_vectors, 3)
    with tf.variable_scope('CNN_Layer1'):
        #添加卷积滤波
        conv1 = tf.contrib.layers.convolution2d(
            word_vectors, N_FILTERS, FILTER_SHAPE1, padding = 'VALID')
        #添加RELU非线性
        conv1 = tf.nn.relu(conv1)
        #最大池化
        pool1 = tf.nn.max_pool(
            conv1,
            ksize = [1, POOLING_WINDOW, 1, 1],
            strides = [1, POOLING_STRIDE, 1, 1],
            padding = 'SAME')
        #对矩阵进行转置
        pool1 = tf.transpose(pool1, [0, 1, 3, 2])
    with tf.variable_scope('CNN_Layer2'):
        #第二个卷积层
        conv2 = tf.contrib.layers.convolution2d(
            pool1, N_FILTERS, FILTER_SHAPE2, padding='VALID')
        #抽取特征
        pool2 = tf.squeeze(tf.reduce_max(conv2, 1), squeeze_dims = [1])

    #全连接层
    logits = tf.contrib.layers.fully_connected(pool2, 15, activation_fn = None)
    loss = tf.losses.softmax_cross_entropy(target, logits)

    train_op = tf.contrib.layers.optimize_loss(
        loss,
        tf.contrib.framework.get_global_step(),
        optimizer = 'Adam',
        learning_rate = 0.007,
    )

    return({
        'class' : tf.argmax(logits, 1),
        'prob' : tf.nn.softmax(logits)
    }), loss, train_op

if __name__ == '__main__':
    # 文本预处理
    folder_path = './nhk_news'  # 训练集存放地址
    #stopwords_file = './stopwords'
    #stopwords_set = MakeWordsSet(stopwords_file)
    x_train, x_test, y_train, y_test = TextProcessing(folder_path)
    classifier = learn.SKCompat(learn.Estimator(model_fn = cnn_model))
    #训练并预测
    classifier.fit(x_train, y_train, steps = 600)
    y_predicted = classifier.predict(x_test)['class']
    score = metrics.accuracy_score(y_test, y_predicted)
    print('Accuracy: {0:f}'.format(score))