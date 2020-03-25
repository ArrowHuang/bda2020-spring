import pandas as pd
import numpy as np
import argparse
import warnings
warnings.filterwarnings('ignore')

# file_path='bda2020_hw1/hw1_table.xlsx'
parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('-path','-p',type=str,default=None,help="Please enter the path of your excel path")
parser.add_argument('-key','-k',type=int,default=20,help="Please enter the number of keywords you want")
parser.add_argument('-type','-t',type=str,default='all',help="Please choose the news type you want, (all,industry or honghai)")
args = parser.parse_args()

def normalization(data,column_name,scale):
    min_n = data[column_name].min()
    max_n = data[column_name].max()
    data[column_name] = scale*(data[column_name]-min_n)/(max_n-min_n)

def get_keyword_all(file_path,num_key):
    
    file_all_2gram = pd.read_excel(file_path,"全部_2gram",encoding='utf-8',header=2)
    file_all_3gram = pd.read_excel(file_path,"全部_3gram",encoding='utf-8',header=2)

    file_all_2gram['TFIDF']=(1+np.log10(file_all_2gram['TF']))*np.log10(90507/file_all_2gram['DF'])
    file_all_2gram = file_all_2gram.round({'TFIDF':3})
    file_all_2gram.sort_values("TFIDF",inplace=True,ascending=False)
    file_all_2gram_part = file_all_2gram[['詞','DF','TFIDF']][:num_key]

    file_all_3gram['TFIDF']=(1+np.log10(file_all_3gram['TF']))*np.log10(90507/file_all_3gram['DF'])
    file_all_3gram = file_all_3gram.round({'TFIDF':3})
    file_all_3gram.sort_values("TFIDF",inplace=True,ascending=False)
    file_all_3gram_part = file_all_3gram[['詞','DF','TFIDF']][:num_key]

    for i in range(len(file_all_3gram_part)):
        text = file_all_3gram_part.values[i][0]
        tfidf_num = file_all_3gram_part.values[i][1]
        text_list = [text[:2],text[1:]]
        repeat_data = file_all_2gram_part[file_all_2gram_part['詞'].isin(text_list)]
        if(len(repeat_data)>0):
            repeat_index = repeat_data[ repeat_data['DF']== tfidf_num ].index.tolist()
            if(len(repeat_index)>0):
                for r in repeat_index:
                    file_all_2gram_part = file_all_2gram_part.drop(r,axis=0)

    file_all_grammixed = pd.concat([file_all_2gram_part, file_all_3gram_part], axis=0)
    file_all_grammixed.sort_values("TFIDF",inplace=True,ascending=False)
    print(file_all_grammixed[['詞','TFIDF']][:num_key])

def get_keyword_industry(file_path,num_key):
    
    file_c_2gram = pd.read_excel(file_path,"產業_2gram",encoding='utf-8',header=2)
    file_c_3gram = pd.read_excel(file_path,"產業_3gram",encoding='utf-8',header=2)

    file_c_2gram_part = file_c_2gram[['詞','DF','TF-IDF','TF卡方值(保留正負號)','DF卡方值(保留正負號)']]
    file_c_3gram_part = file_c_3gram[['詞','DF','TF-IDF','TF卡方值(保留正負號)','DF卡方值(保留正負號)']]
    
    normalization(file_c_2gram_part,'TF卡方值(保留正負號)',10)
    normalization(file_c_3gram_part,'TF卡方值(保留正負號)',10)
    normalization(file_c_2gram_part,'DF卡方值(保留正負號)',10)
    normalization(file_c_3gram_part,'DF卡方值(保留正負號)',10)
   
    file_c_2gram_part['Score'] =  (file_c_2gram_part['TF卡方值(保留正負號)'] * file_c_2gram_part['TF-IDF'] + file_c_2gram_part['DF卡方值(保留正負號)'] * file_c_2gram_part['TF-IDF'] )
    file_c_3gram_part['Score'] =  (file_c_3gram_part['TF卡方值(保留正負號)'] * file_c_3gram_part['TF-IDF'] + file_c_3gram_part['DF卡方值(保留正負號)'] * file_c_3gram_part['TF-IDF'] )
    file_c_2gram_part.sort_values("Score",inplace=True,ascending=False)
    file_c_3gram_part.sort_values("Score",inplace=True,ascending=False)

    file_c_2gram_part = file_c_2gram_part[['詞','DF','Score']][:num_key]
    file_c_3gram_part = file_c_3gram_part[['詞','DF','Score']][:num_key]

    for i in range(len(file_c_3gram_part)):
        text = file_c_3gram_part.values[i][0]
        tfidf_num = file_c_3gram_part.values[i][1]
        text_list = [text[:2],text[1:]]
        repeat_data = file_c_2gram_part[file_c_2gram_part['詞'].isin(text_list)]
        if(len(repeat_data)>0):
            repeat_index = repeat_data[ repeat_data['DF']== tfidf_num ].index.tolist()
            if(len(repeat_index)>0):
                for r in repeat_index:
                    file_c_2gram_part = file_c_2gram_part.drop(r,axis=0)

    file_all_grammixed = pd.concat([file_c_2gram_part, file_c_3gram_part], axis=0)
    file_all_grammixed.sort_values("Score",inplace=True,ascending=False)
    print(file_all_grammixed[['詞','Score']][:num_key])

def get_keyword_honhai(file_path,num_key):
    file_h_2gram = pd.read_excel(file_path,"鴻海_2gram",encoding='utf-8',header=2)
    file_h_3gram = pd.read_excel(file_path,"鴻海_3gram",encoding='utf-8',header=2)

    file_h_2gram_part = file_h_2gram[['詞','DF','TF-IDF','TF卡方值(保留正負號)','DF卡方值(保留正負號)','MI(用DF)','Lift(用DF)']][:num_key]
    file_h_3gram_part = file_h_3gram[['詞','DF','TF-IDF','TF卡方值(保留正負號)','DF卡方值(保留正負號)','MI(用DF)','Lift(用DF)']][:num_key]

    normalization(file_h_2gram_part,'TF卡方值(保留正負號)',10)
    normalization(file_h_3gram_part,'TF卡方值(保留正負號)',10)
    normalization(file_h_2gram_part,'DF卡方值(保留正負號)',10)
    normalization(file_h_3gram_part,'DF卡方值(保留正負號)',10)

    file_h_2gram_part['Score'] =  (file_h_2gram_part['TF卡方值(保留正負號)'] * file_h_2gram_part['TF-IDF'] + file_h_2gram_part['DF卡方值(保留正負號)'] * file_h_2gram_part['TF-IDF'] )
    file_h_3gram_part['Score'] =  (file_h_3gram_part['TF卡方值(保留正負號)'] * file_h_3gram_part['TF-IDF'] + file_h_3gram_part['DF卡方值(保留正負號)'] * file_h_3gram_part['TF-IDF'] )
    # file_h_2gram_part['Score'] = (file_h_2gram_part['TF卡方值(保留正負號)'] + file_h_2gram_part['DF卡方值(保留正負號)'])/2
    # file_h_3gram_part['Score'] = (file_h_3gram_part['TF卡方值(保留正負號)'] + file_h_3gram_part['DF卡方值(保留正負號)'])/2
    file_h_2gram_part.sort_values("Score",inplace=True,ascending=False)
    file_h_3gram_part.sort_values("Score",inplace=True,ascending=False)

    file_h_2gram_part = file_h_2gram_part[['詞','DF','Score']][:num_key]
    file_h_3gram_part = file_h_3gram_part[['詞','DF','Score']][:num_key]

    for i in range(len(file_h_3gram_part)):
        text = file_h_3gram_part.values[i][0]
        tfidf_num = file_h_3gram_part.values[i][1]
        text_list = [text[:2],text[1:]]
        repeat_data = file_h_2gram_part[file_h_2gram_part['詞'].isin(text_list)]
        if(len(repeat_data)>0):
            repeat_index = repeat_data[ repeat_data['DF']== tfidf_num ].index.tolist()
            if(len(repeat_index)>0):
                for r in repeat_index:
                    file_h_2gram_part = file_h_2gram_part.drop(r,axis=0)

    file_all_grammixed = pd.concat([file_h_2gram_part, file_h_3gram_part], axis=0)
    file_all_grammixed.sort_values("Score",inplace=True,ascending=False)
    print(file_all_grammixed[['詞','Score']][:num_key])    

if __name__ == "__main__":

    if(args.type == 'all'):
        get_keyword_all(args.path,args.key)         # 取得所有新聞中關鍵詞,可以自定義要取出的keywords個數
    elif(args.type == 'industry'):
        get_keyword_industry(args.path,args.key)    # 取得產業新聞中關鍵詞,可以自定義要取出的keywords個數
    elif(args.type == 'honghai'):
        get_keyword_honhai(args.path,args.key)        # 取得鴻海新聞中關鍵詞,可以自定義要取出的keywords個數