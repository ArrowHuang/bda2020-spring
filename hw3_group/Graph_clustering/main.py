#coding:utf-8
from deepwalk import DeepWalk
import networkx as nx
import matplotlib.pyplot as plt
from sklearn import metrics
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from process import Preprocess,Translate,Trans_format

def plot_SC(data):
    plt.figure(figsize=(120,100))
    plt.plot(list(range(2,551)),data)
    plt.xticks(range(2,551,1)) 
    plt.grid(linestyle='--')
    plt.xlabel("Number of Clusters Initialized")
    plt.ylabel("Sihouette Score")
    plt.savefig("SC.png")


def plot_MSE(data):
	plt.figure(figsize=(120,100))
	plt.plot(range(2,551),data,'o-')
	plt.xticks(range(2,551,1))
	plt.grid(linestyle='--')
	plt.xlabel("Number of Clusters Initialized")
	plt.ylabel('SSE')
	plt.title("SSE")
	plt.savefig("SEE .png")

# 畫圖找到最好的K
def find_best_k(G_vector):
    MSE = [] #到聚類中心的平方和
    SC = [] #輪廓係數

    for k in range(2,551):
        kmean_model = KMeans(n_clusters=k)
        kmean_model.fit(G_vector)
        labels = kmean_model.labels_
        score = metrics.silhouette_score(G_vector, labels)
        SC.append(score)
        MSE.append(kmean_model.inertia_)
		
    plot_MSE(MSE)
    plot_SC(SC)

# 分類並將顧客分群
def customer_vote(G_list,G_vector):
    kmean_model = KMeans(n_clusters=50)
    kmean_model.fit(G_vector)
    labels = kmean_model.labels_
    # print(len(G_list))
    # print(len(labels))

if __name__ == '__main__':
    # Preprocess('../91ForNTUDataSet/OrderSlaveData.csv')

    #Translate('dataset/dataset.txt')

    #Trans_format('dataset/confidence.txt')

    G = DeepWalk('dataset/result.txt')

    model = Word2Vec.load('graph_embedding_model')

    G_list = G.nodes()
    G_vector = []
    for item in G_list:
	    G_vector.append(model.wv[item])

    #find_best_k(G_vector)

    customer_vote(G_list,G_vector)
