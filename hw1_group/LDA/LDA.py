# coding=utf-8
import re,time
import numpy as np
import pandas as pd
from gensim import corpora, models
from pandas.core.frame import DataFrame


# 讀取停用詞
def get_stopwords(swpath):
    stopword_list = []
    with open(swpath,'r',encoding='utf-8') as f:
        for line in f.readlines():
            stopword_list.append(line.strip())
    return stopword_list
 

# 正規表達去掉英文數字和符號等非unicode 
def text_filter(sentence,ngram_l,ngram_u,stopword_list):
    sentence = re.sub(r'[^\w]','',sentence)
    sentence = re.sub(r'[A-Za-z0-9]','',sentence)
    sentence = re.sub(u'[\uFF01-\uFF5A]','',sentence)
    
    w_all = []
    for i in range(int(ngram_l),int(ngram_u)+1):
        w = zip(sentence[j:j+i] for j in range(len(sentence)-int(i)+1))
        w = list(map( list,zip(*w) ))
        if(w not in stopword_list):
            w_all = w_all + w[0]
    # print(w_all)
    return w_all


# 輸出Excel前處理 
def output_keywords(wordlist):
    wordlist = list(map( list,wordlist ))
    data = DataFrame(wordlist)
    data.columns = ['關鍵詞','分數']
    data['分數'] = data['分數'] * 10000
    data.sort_values("分數",inplace=True,ascending=False)
    data = data.round({'分數':2})
    return data


# 文本前處理 輸入參數 
def LDA_preprocess(filepath,outputpath,swpath):
    ngram_l = 2
    ngram_u = 6

    stopword_list = get_stopwords(swpath)
    writer = pd.ExcelWriter(outputpath)
    dic = []
    type_list = ['銀行','信用卡','匯率','台積電','台灣','日本' ] 
    xls = pd.ExcelFile(filepath)
    start = time.time()

    for i in range(len(type_list)):
        data = pd.read_excel(xls,type_list[i],coding='utf-8')

        for index,row in data.iterrows():
            dic.append(text_filter(row["標題"]+row["內容"],ngram_l,ngram_u,stopword_list))
        
        # 主題模型
        lda_model = LDA_model(dic)
 
        # 儲存該主題的詞及其詞的權重
        words_list = lda_model.show_topic(0, 101)

        # 輸出的dataframe
        output_keywords(words_list).to_excel(writer,sheet_name=type_list[i])

    writer.save()
    print(time.time()-start)

 
# 生成LDA模型
def LDA_model(words_list):
    # 建構辭典
    dictionary = corpora.Dictionary(words_list)
 
    # 将dictionary轉化成一個詞袋
    corpus = [dictionary.doc2bow(words) for words in words_list]
 
    # LDA主題模型參數
    lda_model = models.ldamodel.LdaModel(corpus=corpus, num_topics=1, id2word=dictionary, passes=20)
    
    return lda_model
 

# if __name__ == "__main__":
#     LDA_preprocess('sum_6end.xlsx','LDA_output_100.xlsx','stopWord.txt')
   