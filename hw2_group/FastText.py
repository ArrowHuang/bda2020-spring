import re,jieba,random,os
import numpy as np 
import pandas as pd 
import fasttext
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, recall_score, precision_score 
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

#迭代讀取文本並斷詞過濾
def read_text(data,data_list,stopword_list,category):
    for index,row in data.iterrows():
        line = str(row['title'])+str(row['content'])
        line = re.sub(r'[^\w]','',line)
        line = re.sub(r'[A-Za-z0-9]','',line)
        line = re.sub(u'[\uFF01-\uFF5A]','',line)
        segment_list = jieba.lcut(line)
        segment_list = filter(lambda x: len(x)>1, segment_list)
        segment_list = filter(lambda x: x not in stopword_list, segment_list)
        data_list.append( "__label__"+str(category)+' , '+' '.join(segment_list) )
    return data_list

#將訓練與測試資料保存
def write_file(path,train_data,test_data):
    print("Writing data to fasttext format...")
    with open(path+'fasttext_train_data.txt', 'w',encoding='utf-8') as f:
        for data in train_data:
            f.write(data+"\n")
    f.close()

    with open(path+'fasttext_test_data.txt', 'w',encoding='utf-8') as f2:
        for data in test_data:
            f2.write(data+"\n")
    f2.close()
    print("done!")

#對文本進行處理
def preprocess(positive_path,negative_path,stopword_list):
    p_data = pd.read_csv(positive_path,encoding='utf-8')
    n_data = pd.read_csv(negative_path,encoding='utf-8')
    p_data_all = []
    n_data_all = []
    p_data_all = read_text(p_data,p_data_all,stopword_list,'P')
    n_data_all = read_text(n_data,n_data_all,stopword_list,'N')
    return p_data_all,n_data_all

#訓練找參數
def FastText_Training(data_all,path,fname):
    #將資料大亂並且分為訓練與測試資料 5次取平均
    F1_score_max = 0
    learn_rate_best = 0
    epoch_best = 0
    dim_best = 0
    dic = {'鴻海':0.49,'大立光':1.06,'台積電':0.4}
    for learn_r in range(1):
        # learn_r = float(learn_r/100)
        learn_r = dic[fname]
        F1_list_mean = []
        
        for dim_n in range(10,1000,10):
            for cout in range(10):
                random.shuffle(data_all)
                train_data = data_all[:int(len(data_all)*0.8)]
                test_data = data_all[int(len(data_all)*0.8):]
                    
                write_file(path,train_data,test_data)

                #訓練FastText模型並進行預測
                clf = fasttext.train_supervised(path+'fasttext_train_data.txt',lr=learn_r,dim=dim_n,epoch=50)
                result = clf.test(path+'fasttext_test_data.txt')

                P = result[1]
                R = result[2]
                F1_score = (2*P*R)/(P+R)
                F1_list_mean.append(F1_score)

            if(np.mean(F1_list_mean)>F1_score_max):
                F1_score_max = np.mean(F1_list_mean)
                clf.save_model(path+fname+"_LR_D_E50_NS_model.bin")
                # learn_rate_best = learn_r
                # epoch_best = epoch_n
                dim_best = dim_n

            with open(path+fname+'_LR_D_E50_NS.txt','a+') as f:
                f.write('{},{}\n'.format(dim_n,np.mean(F1_list_mean)))
            f.close()
    
    with open(path+fname+'_LR_D_E50_NS.txt','a+') as f:
        f.write('Best Dim:{}'.format(dim_n))
    f.close()
 
#FastText模型
def FastText_model(model_path,label_path,stopword_path):
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
        data_p,data_n = preprocess(label_path+fname+'_P.csv',label_path+fname+'_N.csv',stopword_list)
        data_all = data_p+data_n

        # FastText_Training(data_all,path,fname) #找到好的參數訓練模型

        random.shuffle(data_all)
        train_data = data_all[:int(len(data_all)*0.8)]
        test_data = data_all[int(len(data_all)*0.8):]            
        write_file(path,train_data,test_data)

        #訓練FastText模型並進行預測
        dic = {'鴻海':0.49,'大立光':1.06,'台積電':0.4}
        clf = fasttext.train_supervised(path+'fasttext_train_data.txt',lr=dic[fname],dim=100,epoch=50)
        clf.save_model(path+"fasttext_model.bin")

        #畫Confusion Matrix
        model = fasttext.load_model(path+"fasttext_model.bin")
        y_true = []
        y_pred = []
        with open(path+'fasttext_test_data.txt','r') as f:
            for line in f.readlines():
                if(',' in line):
                    label = 1 if line.strip().split(',')[0].strip()=='__label__P' else -1
                    data = line.strip().split(',')[1].strip()
                    data = 1 if model.predict(data.strip(),k=1)[0][0]=='__label__P' else -1
                    y_true.append(label)
                    y_pred.append(data)
       
        sns.set()
        f,ax = plt.subplots(figsize=(8,4))
        C = confusion_matrix(y_true,y_pred,labels=[-1,1])
        Cp = sns.heatmap(C,annot = True,fmt='g',cmap='Purples',xticklabels=['-1','1'],yticklabels=['-1','1'])

        ax.set_title('Confusion Matrix for fastText')
        ax.set_xlabel('Predict')
        ax.set_ylabel('Fact')
        ax.set_ylim([0,2])

        f.savefig(path+"CM.png")

        #計算Precision Recall
        print(fname)
        print('Accuracy: {}'.format( accuracy_score(y_true,y_pred) ))
        print('Precision: {}'.format( precision_score(y_true,y_pred,average='macro') ))
        print('Recall: {}'.format( recall_score(y_true,y_pred,average='macro') ))        



        