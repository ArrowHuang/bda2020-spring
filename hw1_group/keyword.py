# coding=utf-8
import pandas as pd
import numpy as np
import argparse
from classification import article_classification
from LDA.lda import LDA_preprocess
from TextRank.textrank import TextRankAlgo
from Word2Vec.w2v import word2vec


parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('-input','-i',type=path,default=None,help="Please enter the path of input file")
parser.add_argument('-output','-o',type=path,default=None,help="Please enter the path of output file")
parser.add_argument('-stop','-s',type=path,default=None,help="Please enter the path of stopword file")
parser.add_argument('-type','-t',type=str,default='all',help="Please choose the keyword extraction method (LDA, W2V, TR or TFIDF)")
args = parser.parse_args()


# 利用LDA模型提取關鍵詞
def LDA_keywords(filepath,outputpath,stopwordspath):
    LDA_preprocess(filepath,outputpath,stopwordspath)


# 利用TextRank提取關鍵詞
def TextRank_keywords(filepath,outputpath)
    TextRankAlgo(filepath,outputpath)


# 利用Word2Vec提取關鍵詞
def Word2Vec_keywords(filepath,outputpath,stopwordspath)
    word2vec(filepath,outputpath,stopwordspath)


if __name__ == "__main__":
     if(args.type == 'LDA'):
        article_classification(args.input) 
        LDA_keywords('Topics.xlsx',args.output,args.stop)   

    elif(args.type == 'W2V'):
        article_classification(args.input) 
        Word2Vec_keywords('Topics.xlsx',args.output,args.stop)   

    elif(args.type == 'TR'):
        article_classification(args.input) 
        TextRank_keywords('Topics.xlsx',args.output) 

    elif(args.type == 'TFIDF'):
        article_classification(args.input) 
        TFIDF_keywords(args.path,args.key)   
   