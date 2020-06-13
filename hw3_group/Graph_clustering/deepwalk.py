#coding:utf-8
from gensim.models import Word2Vec
import pandas as pd
import networkx as nx
import random

class RandomWalker:
    def __init__(self, G, p=1, q=1):
        """
        :param G:
        param p: 返回參數，控制立即遍歷節點的可能。

        param q: In-out參數，允許區分向內向外
        """
        self.G = G
        self.p = p
        self.q = q
    
    def deepwalk_walk(self, walk_length, start_node):
#         開始節點
        walk = [start_node]
#         到達程度停止
        while len(walk) < walk_length:
            cur = walk[-1]
#             獲取當前節點的鄰居節點
            cur_nbrs = list(self.G.neighbors(cur))
            if len(cur_nbrs) > 0:
#                 從鄰居節點中隨機選擇一個節點
                walk.append(random.choice(cur_nbrs))
            else:
                break
        return walk

    def simulate_walks(self, num_walks, walk_length, workers=1, verbose=0):
#         :num_walks  將所有節點隨機遊走的次數
#         :walk_length 每次遊走的長度

        G = self.G

        nodes = list(G.nodes())
        walks = self._simulate_walks(nodes,num_walks,walk_length)
        
#         多線程同時處理
#         results = Parallel(n_jobs=workers, verbose=verbose, )(
#         delayed(self._simulate_walks)(nodes, num, walk_length) for num in
#         partition_num(num_walks, workers))

#         walks = list(itertools.chain(*results))

        return walks

    def _simulate_walks(self, nodes, num_walks, walk_length,):
#         :num_walks  將所有節點遊走的次數
#         :walk_length 每次遊走的長度
        walks = []
        for _ in range(num_walks):
            random.shuffle(nodes)
            for v in nodes:
                if self.p == 1 and self.q == 1:
                    walks.append(self.deepwalk_walk(
                        walk_length=walk_length, start_node=v))
                else:
                    walks.append(self.node2vec_walk(
                        walk_length=walk_length, start_node=v))
        return walks

    def get_alias_edge(self, t, v):
        """
        compute unnormalized transition probability between nodes v and its neighbors give the previous visited node t.
        :param t:
        :param v:
        :return:
        """
        G = self.G
        p = self.p
        q = self.q

        unnormalized_probs = []
        for x in G.neighbors(v):
            weight = G[v][x].get('weight', 1.0)  # w_vx
            if x == t:  # d_tx == 0
                unnormalized_probs.append(weight/p)
            elif G.has_edge(x, t):  # d_tx == 1
                unnormalized_probs.append(weight)
            else:  # d_tx > 1
                unnormalized_probs.append(weight/q)
        norm_const = sum(unnormalized_probs)
        normalized_probs = [
            float(u_prob)/norm_const for u_prob in unnormalized_probs]

        return create_alias_table(normalized_probs)

    def preprocess_transition_probs(self):
        """
        Preprocessing of transition probabilities for guiding the random walks.
        """
        G = self.G

        alias_nodes = {}
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr].get('weight', 1.0)
                                  for nbr in G.neighbors(node)]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob)/norm_const for u_prob in unnormalized_probs]
            alias_nodes[node] = create_alias_table(normalized_probs)

        alias_edges = {}

        for edge in G.edges():
            alias_edges[edge] = self.get_alias_edge(edge[0], edge[1])

        self.alias_nodes = alias_nodes
        self.alias_edges = alias_edges

        return

def DeepWalk(file_path):
    # 讀取graph的節點
    G = nx.read_edgelist(file_path,
                            create_using=nx.DiGraph(), nodetype=None,
                            data=[('weight', int)])

    walker = RandomWalker(G, p=1, q=1 )
    num_walks = 10
    walk_length = 16
    workers = 1
    sentences = walker.simulate_walks(num_walks=num_walks, walk_length=walk_length, workers=workers, verbose=0)
    embed_size=128
    window_size=5
    workers=3
    iter=5
    kwargs = {}
    kwargs["sentences"] = sentences
    kwargs["min_count"] = 0
    kwargs["size"] = embed_size
    kwargs["sg"] = 1  # skip gram
    kwargs["hs"] = 1  # deepwalk use Hierarchical Softmax
    kwargs["workers"] = workers
    kwargs["window"] = window_size
    kwargs["iter"] = iter


    print("Learning embedding vectors...")
    model = Word2Vec(**kwargs)
    print("Learning embedding vectors done!")

    # 保存模型
    model.save('graph_embedding_model')
    
    return G