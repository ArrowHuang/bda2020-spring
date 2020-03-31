# coding=utf-8
import pandas as pd
import numpy as np
from LDA.lda import LDA_preprocess
from TextRank.textrank import TextRankAlgo

def get_keyword():
    LDA_preprocess('sum_end.xlsx','LDA_output.xlsx','stopWord.txt')



if __name__ == "__main__":
    get_keyword()