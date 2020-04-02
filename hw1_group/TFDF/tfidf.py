# coding: utf-8
import pandas as pd
import re
import xlrd
import xlwt
import math


def set_up(collections): #預處理
    _RTS =[]
    for index,val in collections.iterrows():
        w = [val["word"],val["DF"],val["TF"]]
        _RTS.append(w)
    return _RTS


def tf_idf(word_list): # 算tf和idf
    num = len(word_list) # 文檔總數
    for a in word_list:
        df = a[1]
        idf = math.log(num/df)
        a[1] = idf
    return word_list


def get_tf_idf(tf,idf):
    tfidf = (1+math.log(tf))*idf
    return tfidf


def order_tf_idf(un_list): # 算tf-idf值并排序
    tfi_list = []
    for a in un_list:
        tfidf = get_tf_idf(a[2],a[1])
        tfi_list.append((a[0],tfidf))
        
    tfi_list = list(set(tfi_list))  # 去掉重複
    tfi_list = sorted(tfi_list,key = lambda x:x[1],reverse = True) # 按第二個由大到小排序
    return tfi_list


def get_mi(tf_cla,tf_all,cla_num): # 算MI
    mi = math.log(tf_cla/(tf_all*cla_num)) 
    return mi


def order_tmi(ti_list,ti_all_list): # 按tf-idf*MI排序
    cla_num =len(ti_list)
    tf_cla = 0
    tf_all = 0
    tfi = 0
    mi =0
    tmi = 0
    # 合併分類tf和全部tf
    sum_list = []
    checklist = [0]
    for a in ti_list:
        for b in ti_all_list:
            if a[0] == b[0] and a[0] not in checklist:
                sum_list.append([a[0],a[2],b[2],tfi,mi,tmi])
                checklist.append(a[0])

    # 算tf-idf
    for t in range(len(ti_list)):
        sum_list[t][3] = get_tf_idf(ti_list[t][2],ti_list[t][1])
    # 算MI
    for mm in sum_list:
        mm[4] = get_mi(mm[1],mm[2],cla_num)
    # 算t*mi
        mm[5] = mm[3]*mm[4]
    # 排序
    sum_list = sorted(sum_list,key = lambda x:x[5],reverse = True) # 按第6個由大到小排序

    return sum_list


def order_chi(ti_list,ti_all_list): # 按卡方值排序
    # 算變數
    o = 0 # 觀察值
    e = 0 # 期望值
    chi = 0 # 卡方值
    cla_num = len(ti_list)
    all_num = len(ti_all_list)
    chi_list = []  
    check_re = [0]
    for i in ti_list:
        for j in ti_all_list:
            if i[0] == j[0]:            
                o = i[2]
                e = j[2]*cla_num/all_num
                if o > e:
                    chi = math.pow((o-e),2)/e
                else:
                    chi = -1
                chi_list.append([i[0],chi])
    # 排序
    chi_list = sorted(chi_list,key = lambda x:x[1],reverse = True) # 按第2個由大到小排序                    
    return chi_list


def TFIDF_Cal(inputpath,outputpath,sheetname,method,writebook): # 最終結果 排序方法（0，1，2）tfidf排序=0,mi排序=1,chi排序=2
    # 設定輸出
    worksheet = writebook.add_sheet(sheetname)  #在打开的excel中添加一个sheet
    
    worksheet.write(0,0,"word")

    if sheetname == '銀行':
        collections = pd.read_excel(inputpath,'銀行')
        _RTS =set_up(collections)
    elif sheetname == '信用卡':
        collections2 = pd.read_excel(inputpath,'信用卡')
        _RTS =set_up(collections2)
    elif sheetname == '匯率':
        collections3 = pd.read_excel(inputpath,'匯率') 
        _RTS =set_up(collections3)
    elif sheetname == '台積電':
        collections4 = pd.read_excel(inputpath,'台積電')
        _RTS =set_up(collections4)
    elif sheetname == '台灣':
        collections5 = pd.read_excel(inputpath,'台灣')
        _RTS =set_up(collections5)
    elif sheetname == '日本':
        collections6 = pd.read_excel(inputpath,'日本')
        _RTS =set_up(collections6)
        
    un_list = tf_idf(_RTS)
    if method == 0:
        order_tfi = order_tf_idf(un_list)
        #輸出
        worksheet.write(0,1,"tf-idf")
        for num in range(100):  #取多少
            worksheet.write(num+1,0,order_tfi[num][0])
            worksheet.write(num+1,1,order_tfi[num][1])
    else:
        collections7 = pd.read_excel(inputpath,'all')
        _RTS_all =set_up(collections7) 
        noun_list_all = tf_idf(_RTS_all)
        # 刪all重複
        un_list_all = []
        check_nore = {'a':-1}
        for n in range(len(noun_list_all)):
            if noun_list_all[n][0] not in check_nore: #如果沒重複
                un_list_all.append(noun_list_all[n])    # copy
                check_nore[noun_list_all[n][0]] = n     # 寫進dict
            else: 
                renum = check_nore[noun_list_all[n][0]]       # 找到重複的行
                un_list_all.append([0,0,0])                  # 重複的填0
                un_list_all[renum][2] += noun_list_all[n][2]  # 原來的更新tf

        if([0,0,0] in un_list_all):
            un_list_all.remove([0,0,0])
                

        # 输出tmi排序结果到excel
        if method == 1:
            tmi_list = order_tmi(un_list,un_list_all)
            #輸出
            worksheet.write(0,1,"tf-idf*MI")
            for num in range(100):  #取多少
                worksheet.write(num+1,0,tmi_list[num][0])
                worksheet.write(num+1,1,tmi_list[num][1])
        # 输出chi排序结果到excel
        elif method ==2:
            chi_list = order_chi(un_list,un_list_all)
            #輸出
            worksheet.write(0,1,"chi")
            for num in range(100):
                worksheet.write(num+1,0,chi_list[num][0])
                worksheet.write(num+1,1,chi_list[num][1])
        
    writebook.save(outputpath)  # 保存
    return 


def TFIDF_algo(inputpath,outputpath,method):  # (排序方法)tfidf排序=0,mi排序=1,chi排序=2
    writebook = xlwt.Workbook(outputpath)  # 打开一个excel
    runlist = ['銀行','信用卡','匯率','台積電','台灣','日本']
    for runn in runlist:
        TFIDF_Cal(inputpath,outputpath,runn,method,writebook)
    return    


# TFIDF_algo('ngram_all.xlsx','TFDF.xlsx',1)
