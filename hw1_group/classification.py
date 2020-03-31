# coding: utf-8
import pandas as pd
from pandas import Series, DataFrame #Excel切片
import numpy as np
import xlsxwriter,os


def keyword_judge(txt_data):
    dict_theme = {'銀行':['銀行','理財','金融','分行','放款','逾期','證券','台銀','玉山銀行','渣打','台新','資金','貸款','國泰','信託','中信','借貸','開戶','花旗','央行',],
            '信用卡':['信用卡','行動支付','交易','金融卡','消費','銀聯卡','繳費','支付','金管會','簽賬','金額','電子支付','開卡','手續費','一卡通','轉賬','付款','分期','還款','持卡人'],
            '匯率':['匯率','匯率','股市','台股','美股','收盤','市場','投資','股票','跌幅','漲幅','開盤','貶值','人民幣','新台幣','美元','外匯','成交量','日圓','韓元','成交金額'],
            '台積電':['台積電','張忠謀','台灣積體電路','TSMC','半導體','製造','弘塑','電子','濕製程設備','面板','晶圓','供應鏈','供應商','晶片','智能手機','王耀東','蘋果','代工廠','劉德音','處理器','產業'],
            '台灣':['媽祖','台北','總統府','柯文哲','朱立倫','蔡英文','宋楚瑜','共和黨','親民黨','馬英九','捷運','花蓮','台中','台南','新北','賴清德','高雄','宜蘭','新竹','墾丁','阿里山'],
            '日本':['日本','東京','安倍晉三','在野黨','日圓','首相','大分','蓮舫','大阪','動漫','日文','日遺','沖繩','北海道','上高地','帝國','藤原紀香','神社','本田','日產']}
    a=[]
    for i in dict_theme.keys():
        for val in dict_theme[i]:
            if val in txt_data:
                a.append(i)
    m = {'銀行','信用卡' ,'匯率' , '台積電', '台灣', '日本'}
    dic={}
    for s in m:
        zong = a.count(s)
        s=str(s)
        dic[s]=zong
    pp = max(dic.items(),key=lambda x:x[1])
    if int(pp[1])>2:
        pp=pp[0]
        # print(pp)
    else:
        pp=['無']
    return pp


def article_classification(filepath):
    collections = pd.read_excel(filepath,index_col = 0)
    workbook = xlsxwriter.Workbook('Topics.xlsx')#创建一个excel文件
    worksheet = workbook.add_worksheet(u'銀行')
    worksheet1 = workbook.add_worksheet(u'信用卡')
    worksheet2 = workbook.add_worksheet(u'匯率')
    worksheet3 = workbook.add_worksheet(u'台積電')
    worksheet4 = workbook.add_worksheet(u'台灣')
    worksheet5 = workbook.add_worksheet(u'日本')
    i=1
    x=0
    q1=q2=q3=q4=q5=q6=0
    for s in collections.iloc[:,3]: 
        res = keyword_judge(str(s))
        hang = collections.iloc[x,:]
        x+=1
        if res == '銀行':
            q1 +=1
            worksheet.write(q1,0,str(x))
            for z in range(len(hang)):
                zz=z
                z+=1
                worksheet.write(q1,z,str(hang[zz]))
        elif res == '信用卡':
            q2+=1
            worksheet1.write(q2,0,str(x))
            for z in range(len(hang)):
                zz=z
                z+=1
                worksheet1.write(q2,z,str(hang[zz])) 
        elif res == '匯率':
            q3+=1
            worksheet2.write(q3,0,str(x))
            for z in range(len(hang)):
                zz=z
                z+=1
                worksheet2.write(q3,z,str(hang[zz]))
        elif res == '台積電':
            q4+=1
            worksheet3.write(q4,0,str(x))
            for z in range(len(hang)):
                zz=z
                z+=1
                worksheet3.write(q4,z,str(hang[zz]))
            q5+=1
            worksheet4.write(q5,0,str(x))
            for z in range(len(hang)):
                zz=z
                z+=1
                worksheet4.write(q5,z,str(hang[zz]))
        elif res == '日本':
            q6+=1
            worksheet5.write(q6,0,str(x))
            for z in range(len(hang)):
                zz=z
                z+=1
                worksheet5.write(q6,z,str(hang[zz]))
        else:
            pass
    workbook.close()