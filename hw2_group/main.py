import os,time,math
import argparse
import numpy as np
import pandas as pd 
from Match_Stock_News import excel2csv,calStock
from Split_Labeling_Data import SplitAndLabel
from FastText import FastText_model

stock_data_path = 'dataset/stock_data.xlsx'
stopword_path = 'dataset/stopwords.txt'
data_2016_path = 'dataset/2016.csv'
data_2017_path = 'dataset/2017.csv'
data_2018_path = 'dataset/2018.csv'
bbs_data_path = 'dataset/bbs.csv'
news_data_path = 'dataset/news.csv'
stock_save_path = 'sw_result/'
label_save_path = 'label_result/'
model_save_path = 'model_result/'

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('-preprocess','-p',help="Choose to preprocess or not",action='store_true')
parser.add_argument('-label','-l',help="Choose to filter and label or not",action='store_true')
parser.add_argument('-type','-t',type=str,default='FT',help="Please choose the classification method (LDA, W2V, TR or TFIDF)")
args = parser.parse_args()

#前處理函數
def preprocess():

    #將stock_data.xlsx檔案中上市公司抽出來
    excel2csv(stock_data_path,data_2016_path,data_2017_path,data_2018_path) 

    #統計每個股票在新聞中出現次數選出前5筆
    calStock(stock_save_path,data_2016_path,data_2017_path,data_2018_path,bbs_data_path,news_data_path)

#篩選股票以及漲跌分類
def filterAndlabel():

    companies = os.listdir(stock_save_path)
    if(len(companies)>0):  
        data_18 = pd.read_csv(data_2018_path,encoding='utf-8',usecols=['證券代碼','年月日','收盤價(元)'])
        data_17 = pd.read_csv(data_2017_path,encoding='utf-8',usecols=['證券代碼','年月日','收盤價(元)'])
        data_16 = pd.read_csv(data_2016_path,encoding='utf-8',usecols=['證券代碼','年月日','收盤價(元)'])

        SplitAndLabel(stock_save_path,companies,label_save_path,data_16,data_17,data_18,3,0.01) #考慮漲跌的時候自己考慮天數預計門檻

#提取關鍵詞
def keyword_extraction():
    pass

#文本分類訓練模型
def classification(model_type):
    if(model_type=='FT'):
        FastText_model(model_save_path,label_save_path,stopword_path)

#移動回歸測試


if __name__ == '__main__':
    if(args.preprocess == True):
        preprocess()
    if(args.label == True):
        filterAndlabel()
    classification(args.type)
    
            
