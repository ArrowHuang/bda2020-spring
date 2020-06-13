#coding:utf-8
import os,re,itertools
import pandas as pd
import numpy as np
from datetime import timedelta

# 處理交易資料
def Preprocess(file_path):
    filename_data = file_path
    data_csv = pd.read_csv(filename_data,usecols=['TradesGroupCode','TradesDateTime','OuterProductSkuCode','Status','MemberID'])
    # data_csv['TradesDateTime'] = pd.to_datetime(data_csv['TradesDateTime'].astype(str).str[0:19],format="%Y-%m-%d %H:%M:%S") + timedelta(hours=8)
    trade = list(set(data_csv['TradesGroupCode'].values.tolist()))
    data_csv = data_csv[ data_csv['Status']!='Return' ]
    data_csv = data_csv[ data_csv['Status']!='Fail' ]
    data_csv = data_csv[ data_csv['Status']!='Cancel' ]

    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

    for t in trade:
        tmp_data = data_csv[ data_csv['TradesGroupCode']==t ]
        candidate = tmp_data['OuterProductSkuCode'].values.tolist()
        candidate = list(filter(lambda x: zh_pattern.search(str(x))==None,candidate))
        candidate = list(map(str,candidate))
        if(len(candidate)>1):
            with open('dataset/dataset.txt','a+') as f:
                f.write('{}\n'.format(' '.join(candidate)))
            f.close()

# 讀取檔案並且計算每一個商品次數，將垂直資料庫轉成水平資料庫
def Translate(file_path):
    line_count = 1
    single_item = {}
    item_db = {}

    with open(file_path, "r") as f:
        for line in f.readlines():
            for item in line.strip().split(' '):
                tmp_l = []
                if(item in single_item.keys()):
                    single_item[item] = single_item[item] + 1
                    tmp_l = item_db[item]
                    tmp_l.append(line_count)
                    item_db[item] = tmp_l
                else:
                    single_item[item] = 1
                    tmp_l.append(line_count)
                    item_db[item] = tmp_l
            line_count = line_count+1
    f.close()

    #產生兩兩一組
    candidate = []
    for item in single_item.keys():
        if(single_item[item]>1):
            candidate.append(item)
    candidate = list(itertools.permutations(candidate,2))
    
    #計算兩兩一組的confidence
    for c in candidate:
        item1 = c[0]
        item2 = c[1]
        inters = set(item_db[item1]).intersection(set(item_db[item2]))
        if( len(inters)>0 ):
            result = len(inters)/single_item[item1]
            if(result>0.3): #門檻值設定為0.3，由使用者設定
                with open('dataset/confidence.txt','a+') as f:
                    f.write('{}->{} #CONFIDENCE {}\n'.format(item1,item2,result))
                f.close()

# 將商品的confidence重新讀取，保留confidence最大的作為起始與終止
def Trans_format(file_path):
    all_candidate = {}
    all_result = {}
    with open(file_path, "r") as f:
        for line in f.readlines():
            segemnt = line.strip().split(' #CONFIDENCE ')
            seg_con = float(segemnt[1])
            seg_item = segemnt[0].split('->')
            tem_item = ' '.join(sorted(seg_item))
            real_item = ' '.join(seg_item)
            if(tem_item not in all_candidate):
                all_candidate[tem_item] = seg_con
                all_result[tem_item] = real_item
            else:
                if(seg_con>all_candidate[tem_item]):
                    all_candidate[tem_item] = seg_con
                    all_result[tem_item] = real_item
    f.close()

    with open('dataset/result.txt','a+') as f:
        for item in all_result.keys():
            f.write('{}\n'.format(all_result[item]))
    f.close()
