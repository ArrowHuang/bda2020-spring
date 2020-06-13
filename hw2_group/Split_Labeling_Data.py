import pandas as pd
import numpy as np
import os,time,math,warnings
warnings.filterwarnings("ignore")
from datetime import datetime

#計算n天之後漲跌多少
def compute_dis(array , n):
    list1 = []
    for index in range(len(array) - n ):
        list1.append( array[index+n] - array[index])
    return list1

#創建output檔案路徑
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

#結合外部爬蟲數據
def combin_external(stock_path,company_name):
    data_old = pd.read_csv(stock_path+company_name+'.csv',encoding='utf-8',usecols=['post_time','title','content'])
    if(os.path.exists('external_data/'+company_name+'.csv')==True):
        data_external = pd.read_csv('external_data/'+company_name+'.csv',encoding='utf-8',usecols=['發布日期時間','新聞標題','新聞內容'])
        data_external.columns = ['post_time','title','content']
        data = pd.concat([data_old, data_external] , axis= 0) 
        data = data.sort_values(by="post_time")
        data = data.reset_index(drop=True)
        return data
    else:
        return data_old

#篩選波動大的股票
def SplitAndLabel(stock_path,companies, out_path, data_16, data_17, data_18, date, rate):
    mkdir(out_path)
    company_list = list(set(data_18['證券代碼'].values.tolist()))
    
    for company in companies:
        if('csv' in company):
            company_name = company.split('.')[0]
            for cn in company_list:
                if(company_name==cn.split(' ')[1]):
                    company_name2 = cn
                    break

            df1 = data_18[data_18['證券代碼'] == company_name2]
            df2 = data_17[data_17['證券代碼'] == company_name2]
            df3 = data_16[data_16['證券代碼'] == company_name2]
            df = pd.concat([df1, df2, df3] , axis= 0) 
            df = df.sort_values(by="年月日")
            df = df.reset_index(drop=True)
            
            df_value = df['收盤價(元)']
            if(df_value.std()>15): #判斷波動性,選出台積電、鴻海、大立光
                df_value_l = df['收盤價(元)'].values.tolist()
                data_news = combin_external(stock_path,company_name) #將外部爬蟲數據合併進來
                bais = compute_dis( df_value_l , date) #計算n天之後股票收盤價漲跌
                
                #計算漲幅率或者跌幅率
                labels = np.zeros( ( len(df) ) )
                index = 0
                for (item1 , item2) in zip(bais , df_value_l[:len(df_value_l)-date]):
                    result = item1 / item2    
                    if(result >= rate):
                        labels[index] = 1
                    elif(result <= -rate):
                        labels[index] = -1
                    index = index + 1
                
                #若某一天出現+1/-1,則之後n天新聞也同樣+1/-1
                labels2 = np.zeros(( len(df) ) )
                for index in range(len(labels2)):
                    if labels[index] == 1: # 扩充到n天， 到这里每一天的label就标记好了
                        labels2[index:index+date] = 1
                    elif labels[index] == -1:
                        labels2[index:index+date] = -1
                df_slabel = pd.Series(labels2)
                df['label'] = df_slabel #將label放到股票上面

                #把新聞中的時間轉換回來
                time1 = []
                for items in data_news['post_time']:
                    timeArray = time.strptime(items, "%Y/%m/%d %H:%M:%S")
                    dt_new = time.strftime("%Y-%m-%d",timeArray)
                    time1.append(dt_new)

                times = pd.Series(time1)
                data_news['times'] = times                

                new_labels = np.zeros((data_news.shape[0]))
                for index in range(len(data_news['times'])):
                    temp = df[df['年月日'] == data_news['times'][index]]['label'].values
                    if len(temp) == 0:
                        new_labels[index] = 0
                    else:
                        if math.isnan(temp):
                            new_labels[index] = 0
                        else:
                            new_labels[index] = int(temp)
                
                new_labels = pd.Series(new_labels)
                data_news['label'] = new_labels

                # #輸出成csv檔案
                df_label_positive = data_news[data_news['label'] == 1].reset_index(drop=True)
                df_label_positive = df_label_positive[['post_time','title','content','label']]
                df_label_positive.to_csv(out_path+str(company_name)+'_P.csv')

                df_label_negative = data_news[data_news['label'] == -1].reset_index(drop=True)
                df_label_negative = df_label_negative[['post_time','title','content','label']]
                df_label_negative.to_csv(out_path+str(company_name)+'_N.csv')
                print(len(df_label_positive),len(df_label_negative))


                    
                

