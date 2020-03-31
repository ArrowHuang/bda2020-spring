# coding=utf-8
import pandas as pd
import numpy as np
from LDA.lda import LDA_preprocess
from TextRank.textrank import TextRankAlgo
from Word2Vec.w2v import word2vec

def get_keyword():
    # LDA_preprocess('sum_end.xlsx','LDA_output.xlsx','stopWord.txt')
    word2vec('sum_end.xlsx','Word2Vec_output.xlsx','stopWord.txt')


if __name__ == "__main__":
    get_keyword()