# coding=utf-8
import pandas as pd
import numpy as np
import argparse
from ngram import generate_ngram
from classification import article_classification
from LDA.lda import LDA_preprocess
from TextRank.textrank import TextRankAlgo
from Word2Vec.w2v import word2vec
from TFDF.tfidf import TFIDF_algo


parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('-input','-i',type=str,default='hw1_text.xlsx',help="Please enter the path of input file")
parser.add_argument('-output','-o',type=str,default=None,help="Please enter the path of output file")
parser.add_argument('-stop','-s',type=str,default='stopWord.txt',help="Please enter the path of stopword file")
parser.add_argument('-type','-t',type=str,default=None,help="Please choose the keyword extraction method (LDA, W2V, TR or TFIDF)")
parser.add_argument('-num','-n',type=int,default=0,help="Please choose the TF-IDF type (0:TF-IDF | 1:TF-IDF+MI | 2:TF-IDF+Chi )")
args = parser.parse_args()


# 利用LDA模型提取關鍵詞
def LDA_keywords(filepath,outputpath,stopwordspath):
    LDA_preprocess(filepath,outputpath,stopwordspath)


# 利用TextRank提取關鍵詞
def TextRank_keywords(filepath,outputpath):
    TextRankAlgo(filepath,outputpath)


# 利用Word2Vec提取關鍵詞
def Word2Vec_keywords(filepath,outputpath,stopwordspath):
    word2vec(filepath,outputpath,stopwordspath)


# 利用TF-IDF提取關鍵詞
def TFIDF_keywords(filepath,outputpath,num):
    TFIDF_algo(filepath,outputpath,num)


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
        # generate_ngram('Topics.xlsx',args.stop)
        TFIDF_keywords('ngram_all.xlsx',args.output,args.num)   
   