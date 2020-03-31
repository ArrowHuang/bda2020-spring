# coding: utf-8
# from ckiptagger import data_utils,WS
# ws = WS("./data")
import pandas as pd
import numpy as np
import re
import openpyxl
from gensim.models.word2vec import Word2Vec

topic_dic = {'銀行':'bank','信用卡':'credit','匯率':'rate','台積電':'tmx','台灣':'tw','日本':'jp'}

def get_stopwords(swpath):
    stopword_list = []
    with open(swpath,'r') as f:
        for line in f.readlines():
            stopword_list.append(line.strip())
    return stopword_list


def text_filter(sentence,stopWords):
    candi = ''
    sentence = re.sub(r'[^\w]','',sentence)
    sentence = re.sub(r'[A-Za-z0-9]','',sentence)
    sentence = re.sub(u'[\uFF01-\uFF5A]','',sentence)
    for i in sentence[:len(sentence)]:
        if i not in stopWords or i != '\n':
            candi +=i
    candi.strip()
    return candi


# def processing(collection,stopWords,n):
#     processed_data = {}
#     for idx, val in collection.iloc[:n].iterrows():
#         line =  val['標題']+val['內容']
#         pre_sent = text_filter(line,stopWords)
#         processed_data[idx] = ws([pre_sent])
#     processed_data = pd.DataFrame.from_dict(processed_data, orient='index')
#     return processed_data


def most_similar(modelPath,words,modelname,topn=50):
    model = Word2Vec.load(modelPath + modelname + '.model')
    similar_df = pd.DataFrame()
    for word in words:
        if word in model:
            similar_words = pd.DataFrame(model.most_similar(words, topn=topn), columns=['關鍵詞', 'Cos similarity'])
            similar_df = pd.concat([similar_df, similar_words], axis=1)
            similar_df.index = np.arange(1, len(similar_df)+1)
        else:
            print(word, "not found in Word2Vec model!")
    return similar_df


def word2vec(filepath,resultpath,stopwordpath):
    stopWords = get_stopwords(stopwordpath)
    xls = pd.ExcelFile(filepath)
    result_path = resultpath
    modelPath = 'models/'
    
    write = pd.ExcelWriter(result_path)
    for topic in xls.sheet_names:
        data = pd.read_excel(xls,topic, names = ['編號','類別','時間','標題','內容'])
        # train = processing(data,stopWords,len(data))
        
        # for i in range(len(train)):
        #     train[0][i] = [w for w in train[0][i] if len(w) > 1]
        
        # model = Word2Vec(train[0], sg=0, size=128,  window=5,  min_count=1)
        # model.save(modelPath + topic + '.model')
        
        modelname = topic_dic[topic]
        df = most_similar(modelPath,[topic],modelname,topn=100)
        df.to_excel(write,sheet_name=topic,index=True)
    write.save()

# word2vec('sum_end.xlsx','result.xlsx','stopWord.txt')