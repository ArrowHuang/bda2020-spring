# coding: utf-8
import pandas as pd
import re
from collections import Counter
import xlrd


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


def get_stopword(stopwordpath):
    stopword = []
    with open(stopwordpath,"r",encoding = "utf8") as file:
        for data in file.readlines():
            data = data.strip()
            stopword.append(data)
    file.close()
    return stopword


def getdf_tf_list(collections):
    _RTS = {}
    dfngram_list = []
    tfngram_list = []

    for n_gram in range(2,7):
        df_dic = {}
        tf_dic = {}
        for index,row in collections.iterrows():
            _RTS[index] = preprocess(row["標題"]+row["內容"],n_gram,stopword)
        for key in _RTS.keys():
            for w in _RTS[key]:
                df = sum([w in _RTS[k] for k in _RTS.keys()])
                df_dic[w] = int(df)
#                 print(df)
                if w in tf_dic:
                    tf_dic[w] += 1
                else:
                    tf_dic[w] = 1
        tf_dic = {k:v for k,v in tf_dic.items() if v>10}
        df_dic = {k:v for k,v in df_dic.items() if v>5}
        tfngram_list.append(tf_dic)  
        dfngram_list.append(df_dic)  
    return dfngram_list,tfngram_list


def combinegram(df_list):            
    for bigram,bi_df in list(df_list[0].items()):
        for trigram,tri_df in list(df_list[1].items()):
            if bigram in trigram and bi_df == tri_df:
                df_list[0].pop(bigram,bi_df)
                break
            for fourgram,four_df in list(df_list[2].items()):
                if trigram in fourgram and four_df == tri_df:
                    df_list[1].pop(trigram,tri_df)
                    break
                for fivegram,five_df in list(df_list[3].items()):
                    if fourgram in fivegram and four_df == five_df:
                        df_list[2].pop(fourgram,four_df)
                        break
                    for sixgram,six_df in list(df_list[4].items()):
                        if fivegram in sixgram and six_df == five_df:
                            df_list[3].pop(fivegram,five_df)
                            break
    return df_list


#后面是新加的代码，要跑gramlist的
def sort(df_list,tf_list):
    ngram = []
    for i in range(0,5):
        df_i_list = df_listdic[i]
        tf_i_list = tf_listdic[i]
        gram_i = pd.DataFrame([df_i_list,tf_i_list],index=["DF","TF"])
        gram_i = pd.DataFrame(gram_i.values.T,index=gram_i.columns,columns=gram_i.index)
        gram_i = gram_i[:1000]
        gram_i = gram_i.dropna(axis=0,how="any")
        ngram.append(gram_i)
    ngramresult = pd.concat(ngram)
    ngramresult.sort_values(by=["DF","TF"],ascending=[False,False],inplace=True)
    ngramresult = ngramresult[:1000]
    gramlist = ngramresult.index.tolist()
    return ngramresult,gramlist


def getall_df_tf_list(alllist):
    df_dic = {}
    tf_dic = {}
    collections = pd.read_excel("bda2020_hw1/sum_6end1.xlsx",index_col = 0,coding='utf-8')
    for index,row in collections.iloc[0:].iterrows():
        for w in alllist: 
            newsstr = ''
            newsstr = row["標題"]+row["內容"]
            print(newsstr+"\n")
            if w in newsstr:
                if w in df_dic.keys():
                    df_dic[w]+=1
                else:
                    df_dic[w]=1
                if w in tf_dic.keys():
                    sumtf = tf_dic[w]
                    tf = newsstr.count(w)
                    sumtf = sumtf + tf
                    tf_dic[w] = sumtf
                else:
                    tf = newsstr.count(w)
                    tf_dic[w] = tf
    
    return df_dic,tf_dic


def generate_ngram(filepath,stopwordpath): #filepath=Topic
    m = ['銀行','信用卡' ,'匯率', '台積電', '台灣', '日本']
    stopword = get_stopword(stopwordpath)
    workbook = pd.ExcelWriter("TFDF/ngram_0.xlsx")
    allgramlist = []
    for i in range(len(m)):
        collections = pd.read_excel(filepath,i,index_col = 0,coding='utf-8')
        df_listdic,tf_listdic =  getdf_tf_list(collections)
        comdf_list = combinegram(df_listdic)
        ngramresult,gramlist = sort(comdf_list,tf_listdic)
        ngramresult.to_excel(workbook,sheet_name = m[i])
        allgramlist.append(gramlist)
    workbook.save()
    alllist = allgramlist[0]+allgramlist[1]+allgramlist[2]+allgramlist[3]+allgramlist[4]+allgramlist[5] 


    df_list,tf_list = getall_df_tf_list(alllist) 
    gramlist = pd.DataFrame([df_list,tf_list],index=["DF","TF"])
    gramlist = pd.DataFrame(gramlist.values.T,index=gramlist.columns,columns=gramlist.index)
    gramlist.sort_values(by=["DF","TF"],ascending=[False,False],inplace=True)
    workbook = pd.ExcelWriter("TFDF/allgramlist.xlsx")
    ngramresult.to_excel(workbook,sheet_name ="gramlist")
    workbook.save()
