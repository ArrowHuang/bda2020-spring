import os
import numpy as np
import pandas as pd
import re,random
import jieba
import pickle 
from sklearn import metrics 
from sklearn.model_selection import train_test_split 
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from xgboost import XGBClassifier
import seaborn as sn

#創建output檔案路徑
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

#讀取停用詞語
def read_stopword(stopword_path):
    stopword_list = []
    with open(stopword_path,encoding='utf-8') as f:
        for line in f.readlines():
            stopword_list.append(line.strip())
    f.close()
    return stopword_list

#迭代讀取文本並斷詞過濾
def read_text(data,data_list,stopword_list,category):
    for index,row in data.iterrows():
        line = str(row['title'])+str(row['content'])
        line = re.sub(r'[^\w]','',line)
        line = re.sub(r'[A-Za-z0-9]','',line)
        line = re.sub(u'[\uFF01-\uFF5A]','',line)
        segment_list = jieba.lcut(line)
        segment_list = filter(lambda x: len(x)>1, segment_list)
        segment_list = filter(lambda x: x not in stopword_list, segment_list)
        data_list.append( "__label__"+str(category)+' , '+' '.join(segment_list) )
    return data_list

#對文本進行處理
def preprocess(positive_path,negative_path,stopword_list):
    p_data = pd.read_csv(positive_path,encoding='utf-8')
    n_data = pd.read_csv(negative_path,encoding='utf-8')
    p_data_all = []
    n_data_all = []
    p_data_all = read_text(p_data,p_data_all,stopword_list,'P')
    n_data_all = read_text(n_data,n_data_all,stopword_list,'N')
    return p_data_all,n_data_all

#FastText模型
def Xgboost_model(model_path,label_path,stopword_path):
    mkdir(model_path) #創建模型輸出文件夾
    stopword_list = read_stopword(stopword_path) #讀取停用詞

    #讀取分類好文件
    fname_list = []
    files = os.listdir(label_path)
    for fname in files:
        if('.csv' in fname):
            fname_list.append(fname.split('_')[0])
    fname_list = list(set(fname_list))

    #處理每一類股票的漲跌文件
    for fname in fname_list:
        path = model_path+fname+'/'
        mkdir(path)

        data_p,data_n = preprocess(label_path+fname+'_P.csv',label_path+fname+'_N.csv',stopword_list)
        data_all = data_p+data_n
        
        random.shuffle(data_all)
        x,y = zip(*data_all)
        x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.3,random_state=666)

        #TFIDF詞帶模型
        tvec = TfidfVectorizer(
            analyzer='word',
            ngram_range=(2,6), 
            max_features=8000 
        )

        #載入模型
        with open(path+'xgboost_model.pickle', 'rb') as f:
            xgb = pickle.load(f)

        pred = xgb.predict(tvec.transform(x_test))
        print ('Optimal xgboost f1-score: %.4f' %metrics.f1_score(y_test,pred))
        print ('Optimal xgboost accuracy: %.4f' %metrics. accuracy_score(y_test,pred))
        
        #畫Confusion Matrix
        # con = metrics.confusion_matrix(y_test,pred)
        # f, ax = plt.subplots(figsize = (6, 4))
        # sn.heatmap(con,annot=True,fmt ='g',cmap='Purples',xticklabels =['-1','1'], yticklabels=['-1','1'])
        # ax.set_title('Confusion matrix for '+stockname)
        # ax.set_xlabel('Predict')
        # ax.set_ylabel('Fact')
        # f.savefig(path++ "XGboost.png")
