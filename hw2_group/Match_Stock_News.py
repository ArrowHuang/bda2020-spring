import numpy as np
import pandas as pd 

#由於Excel讀取太慢，所以轉成CSV
def excel2csv(filepath,path_16,path_17,path_18):
    data_18 = pd.read_excel(filepath,'上市2018',encoding='utf-8')
    data_18.to_csv(path_18)
    data_17 = pd.read_excel(filepath,'上市2017',encoding='utf-8')
    data_17.to_csv(path_17)
    data_16 = pd.read_excel(filepath,'上市2016',encoding='utf-8')
    data_16.to_csv(path_16)

#選取前K個新聞(k=5)
def getTopK(data_dic_n):
    data_dic_n = sorted(data_dic_n.items(), key=lambda x:x[1],reverse=True)[:5]
    return data_dic_n

#讀取兩個文本檔案
def match_stock2news(stock_type,bbs_path,news_path,save_path):
    data_bbs = pd.read_csv(bbs_path,encoding='utf-8')
    data_bbs = data_bbs[["post_time","title","content"]]

    data_news = pd.read_csv(news_path,encoding='utf-8')
    data_news = data_news[["post_time","title","content"]]

    data_all = pd.concat([data_bbs,data_news],axis=0) #合併起來
    data_all = data_all.reset_index(drop=True) #重新設定索引值
    
    data_dic = {}
    data_dic_n = {}

    for stock in stock_type:
        stock = stock.split('-')[0]
        for index,row_data in data_all.iterrows():
            data_list = []
            if( stock in  str(row_data['title'])+str(row_data['content']) ):
                if(stock not in data_dic.keys()):
                    data_list.append(index)
                    data_dic[stock] = data_list
                    data_dic_n[stock] = 1
                else:
                    data_list = data_dic[stock]
                    data_list.append(index)
                    data_dic[stock] = data_list
                    data_dic_n[stock] = data_dic_n[stock] + 1
    
    data_dic_n = getTopK(data_dic_n) #排序取前K個

    #找到每一個stock對應出現的新聞
    for data in data_dic_n:
        data_tmp = data_all.iloc[data_dic[data[0]]]
        data_tmp = data_tmp.reset_index(drop=True) #重新設定索引值
        data_tmp.to_csv(save_path+str(data[0])+'.csv')         

#讀取三年股票檔案
def calStock(save_path,path_16,path_17,path_18,bbs_path,news_path):

    data_18 = pd.read_csv(path_18,encoding='utf-8')
    data_18 = data_18[['證券代碼','年月日','收盤價(元)']]

    data_17 = pd.read_csv(path_17,encoding='utf-8')
    data_17 = data_17[['證券代碼','年月日','收盤價(元)']]

    data_16 = pd.read_csv(path_16,encoding='utf-8')
    data_16 = data_16[['證券代碼','年月日','收盤價(元)']]

    stock_type = list(set(data_18['證券代碼'].values.tolist()))      #取得所有股票種類
    stock_type = list(filter(lambda x: '指數' not in x,stock_type)) #去掉所以指數類股票
    stock_type = [x.split(' ')[1] for x in stock_type]
    
    match_stock2news(stock_type,bbs_path,news_path,save_path)