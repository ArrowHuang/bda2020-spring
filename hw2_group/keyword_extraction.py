# coding: utf-8
import pandas as pd
import re
from collections import Counter
import xlrd
import xlwt
import math

def preprocess(sent,n_gram,stopword):
    sent = re.sub(u'[\uFF01-\uFF5A]','',sent)
    sent = re.sub(r'[^\w]',' ',sent)
    sent = re.sub(r'[A-Za-z0-9]','',sent)

    return_list = [] 
    for i in range(len(sent) -n_gram+1):
        w = sent[i:i+n_gram]
        if w not in stopword:
            return_list.append(w)
            if " " in w:
                return_list.remove(w)
    return return_list

def getdf_tf_list(collections):
    # stopword
    stopword = []
    with open('stopWord.txt',"r",encoding = "utf8") as file:
        for data in file.readlines():
            data = data.strip()
            stopword.append(data)
    file.close()
    _RTS = {}
    dfngram_list = []
    tfngram_list = []
    for n_gram in range(2,5):
        df_dic = {}
        tf_dic = {}
        num = len(collections)
        for index,row in collections.iterrows():
            if type(row["title"]) == str and type(row["content"]) == str:
                _RTS[index] = preprocess(row["title"]+row["content"],n_gram,stopword)
        for i in _RTS.keys():
            for w in _RTS[i]:
                #df = sum([w in _RTS[k] for k in _RTS.keys()])
                #df_dic[w] = int(df)
                if w in tf_dic:
                    tf_dic[w] += 1
                else:
                    tf_dic[w] = 1

        tf_dic = {k:v for k,v in tf_dic.items() if v>40}
        for wor in tf_dic.keys():
            df = 0
            for ke in _RTS.keys():
                if wor in _RTS[ke]:
                    df += 1
            df_dic[wor] = df
        df_dic = {k:v for k,v in df_dic.items() if v>5}
        tfngram_list.append(tf_dic)  
        dfngram_list.append(df_dic)
    return dfngram_list,tfngram_list,num

def get_result(excel):
    # 設定輸出
    writebook = xlwt.Workbook('result.xlsx')  # 打开一个excel
    worksheet = writebook.add_sheet('1')
    # 打开文件
    collections = pd.read_excel(excel,index_col = 0,coding='utf-8')
    df_listdic,tf_listdic,num =  getdf_tf_list(collections)
    # 把list转换dict
    tf_dic = {}
    for i in tf_listdic:
        for k in i.keys():
            tf_dic[k] = i[k]
    df_dic = {}
    for i in df_listdic:
        for k in i.keys():
            df_dic[k] = i[k]
    # 已有tf和idf
    # 输出格式
    worksheet.write(0,0,"word")
    worksheet.write(0,1,"tf")
    worksheet.write(0,2,"idf")
    worksheet.write(0,3,"tf-idf")
    worksheet.write(0,4,"chi")
    round = 0
    for kword in tf_dic.keys():
        if kword in df_dic.keys():
            # 计算
            tf = tf_dic[kword]
            df = df_dic[kword]
            idf = math.log(num/df)
            tfidf = (1+math.log(tf))*idf
            #chi = math.pow((o-e),2)/e 
            # 输出
            if tfidf > 25:
                 round += 1
                 worksheet.write(round,0,kword) # word
                 worksheet.write(round,1,tf) # tf
                 worksheet.write(round,2,idf) # idf
                 worksheet.write(round,3,tfidf) # tfidf
                 #worksheet.write(round,4,) # chi

    writebook.save('result.xls')
    return 

get_result('tjdn.xlsx')
