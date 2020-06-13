import re,jieba,random,pickle,os
import numpy as np 
import pandas as pd 
from sklearn.model_selection import train_test_split,GridSearchCV,cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer #提取詞的特徵
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import precision_score,accuracy_score,recall_score,f1_score
import seaborn as sns
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

#創建output檔案路徑
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

#讀取停用詞語
def read_stopword(stopword_path):
    stopword_list = []
    with open(stopword_path,encoding='utf-8') as f:
        for line in f.readlines():
            stopword_list.append(line.strip())
    f.close()
    return stopword_list

def text_feature_(text, feature_words):
    text_words = set(text)
    features = [1 if word in text_words else 0 for word in feature_words]
    return features

#詞袋模型提取特徵
def get_feature():
    vec = CountVectorizer(
        analyzer='word', # 特徵由單詞構成
        ngram_range=(1,4), # ngram取1gram到4gram
        max_features=8000 # 選最常出現400個單詞構成詞袋
    )

    # TFIDF模型提取特徵
    tfidf_vect = TfidfVectorizer(
        analyzer='word', # 特徵由單詞構成
        ngram_range=(1,4), # ngram取1gram到4gram
        max_features=8000 # 選最常出現400個單詞構成詞袋
    )

#篩選出頻率最高
def get_frequency(all_words_list,x_train):
    all_words_dict = {}
    for word_str in x_train:
        for word in word_str:
            if all_words_dict.get(word) != None:
                all_words_dict[word] += 1
            else:
                all_words_dict[word] = 1
    return all_words_dict

#讀取資料
def get_data(N_path,P_path):
    N_news = pd.read_csv(N_path,encoding='utf-8')
    N_news = N_news.dropna()
    P_news = pd.read_csv(P_path,encoding='utf-8')
    P_news = P_news.dropna()
    return N_news,P_news

#前處理
def preprocess(data,all_data,category,stop_list):
    for line in data:
        line = re.sub(r'[^\w]','',line)
        line = re.sub(r'[A-Za-z0-9]','',line)
        line = re.sub(u'[\uFF01-\uFF5A]','',line)
        segment_list = jieba.lcut(line)
        segment_list = filter(lambda x: len(x)>1,segment_list)
        segment_list = filter(lambda x: x not in stop_list,segment_list)
        all_data.append( (' '.join(segment_list),category) )
    return all_data

#Randomforest模型
def RandomForest_model(model_path,label_path,stopword_path):
    mkdir(model_path) #創建模型輸出文件夾
    stopword_list = read_stopword(stopword_path) #讀取停用詞

    #讀取分類好文件
    fname_list = []
    files = os.listdir(label_path)
    for fname in files:
        if('.csv' in fname):
            fname_list.append(fname.split('_')[0])
    fname_list = list(set(fname_list))

    #處理每一類股票的漲跌文件
    for fname in fname_list:
        path = model_path+fname+'/'
        mkdir(path)
        N_news,P_news = get_data(label_path+fname+'_N.csv',label_path+fname+'_P.csv')
        
        #前處理文本
        all_data = []
        all_data = preprocess(N_news.content.values.tolist(),all_data,'Negative_news',stopword_list)
        all_data = preprocess(P_news.content.values.tolist(),all_data,'Positive_news',stopword_list)

        random.shuffle(all_data) #將所有資料打亂順序
        x,y = zip(*all_data)
        x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.3,random_state = 50)

        
        all_words_dict = {}
        all_words_dict = get_frequency(all_words_dict,x_train)
        all_words_tuple_list = sorted(all_words_dict.items(), key=lambda f: f[1], reverse=True)     # 按值降序排序 
        all_words_list = list(list(zip(*all_words_tuple_list))[0])      # all_words_list[word_one, word_two, ...]  
        all_words_list = all_words_list[:500]

        train_feature_list = [text_feature_(text, all_words_list) for text in x_train]
        test_feature_list = [text_feature_(text, all_words_list) for text in x_test]
       
        #載入模型
        with open(path+'randomforest_model.pickle', 'rb') as f:
            rfc = pickle.load(f)
        
        score = cross_val_score(rfc,train_feature_list, y_train,cv=10).mean()

        rfc = rfc.fit(train_feature_list,y_train)
        rfc.score(train_feature_list,y_train)
        rfc.apply(test_feature_list)
        predictions = rfc.predict(test_feature_list)

        precision = metrics.precision_score(predictions,y_test,average='weighted') #
        accuracy = accuracy_score(predictions,y_test)
        recall = recall_score(predictions,y_test,average='weighted')
        F_Measure = f1_score(predictions,y_test,average='weighted')

        print('Model score is: %.2f%%' % (100 * score))  #评估模型准确率
        print('precision ratio: %.2f%%' % (100 * precision)) #准确率
        print('Accuracy ratio: %.2f%%' % (100 * accuracy))
        print('Recall ratio: %.2f%%' % (100 * recall))
        print('F-Measure ratio: %.2f%%' % (100 * F_Measure))
        print()

        # C2 = confusion_matrix(y_test,predictionstest4)
        # f,ax = plt.subplots(figsize = (6,4))
        # sns.heatmap(C2,annot = True,fmt='g',cmap='Purples',xticklabels=['-1','1'],yticklabels=['-1','1'])
        # ax.set_title('Confusion matrix for tjd')
        # ax.set_xlabel('Predict')
        # ax.set_ylabel('Fact')








        