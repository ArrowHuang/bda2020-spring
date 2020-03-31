from imp import reload
import sys
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import pandas as pd
import argparse
from pathlib import Path

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

def concat_all(df):
    # concat 标题和内容
    test_title, test_text= df['標題'], df['內容']
    text_list = []
    for i in range(df.shape[0]):
        text = '%s。%s' % (test_title[i], test_text[i])
        text_list.append(text)
    df['New_all'] = text_list
    str1 = ''
    for index in range(df.shape[0]):
        str1 += df['New_all'][index]
    
    return str1


def compute_texttank(df , filepath):
    writer = pd.ExcelWriter(filepath)
    for names in df:
        
        all_re =[]
        test_df = df[names]
        text_all = concat_all(df= test_df)
        tr4w = TextRank4Keyword()
        tr4w.analyze(text=text_all, lower=True, window=6)
        for item in tr4w.get_keywords(num=100, word_min_len=2):
            all_re.append([item.word, item.weight])

        df_result = pd.DataFrame(all_re)
        df_result.columns = ['關鍵詞' , 'Textrank分數']
        df_result.to_excel(writer , sheet_name= names)

    writer.save()


def TextRankAlgo(filepath,oputputpath):
    df = pd.read_excel(filepath, sheet_name= None)
    compute_texttank(df , oputputpath)


# def _parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('data_path' , type = Path)
#     parser.add_argument('output_path', type = Path)
#     args = parser.parse_args()
#     return args

# if __name__ == '__main__':
#     args = _parse_args()
#     main(args)



