import random
import json
import torch
import numpy as np
import networkx as nx
from utils import *
from datetime import datetime


# data_chronic_urticaria
# data_lupus_erythematosus
# data_rheumatoid_arthritis

MODEL_PATH_BET = './model/GNN-Bet.pth'
MODEL_PATH_CLOSE = './model/GNN-Close.pth'

DATA_FILE_PATH = './datasets/my_data/Immunology/data_chronic_urticaria.json'
SAVE_DATA_PATH = './datasets/res/Immunology/res_chronic_urticaria.json'

model_size = 27000
torch.manual_seed(20)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


""" 1 read data 
"""
with open(DATA_FILE_PATH, 'r', encoding='utf-8') as fp:
    row_datas = json.load(fp)
    fp.close()


""" 2 build nodes
"""
nodes = dict()
index = 0
for data in row_datas:
    authors = data['AuthorList']
    for author in authors:
        # if the map doesn't containKey 'participant', 
        # add {'author': id} pair
        if author not in nodes:
            nodes[author] = index
            index += 1

print('Total number of authors (nodes): ' + str(len(nodes)))


""" 3 build edges
"""
edges = []
for data in row_datas:
    authors = data['AuthorList']
    # ex.
    # source: [p1, p2, p3]
    # edges : p1->p2, p1->p3, p2->p3
    for i in range(0, len(authors)):
        for j in range(i + 1, len(authors)):
            first_author = nodes[authors[i]]
            second_author = nodes[authors[j]]
            edge = {
                'source': first_author,
                'target': second_author
            }
            edges.append(edge)

print('Total number of edges: ' + str(len(edges)))



""" 4 extract years of experience
"""
author_experience = {}
for data in row_datas:
    if 'Years' in data and data['Years']:
        year = int(data['Years'][0]['Year'])
        month = int(data['Years'][0]['Month'])
        day = int(data['Years'][0]['Day'])
        pub_date = datetime(year, month, day)
    else:
        pub_date = datetime.now() 
    
    for author in data['AuthorList']:
        if author in author_experience:
            author_experience[author] = min(author_experience[author], pub_date)
        else:
            author_experience[author] = pub_date

# Calculate years of experience
results = {}
for author, date in author_experience.items():
    current_yoe = (datetime.now() - date).days / 365.25
    results[author] = current_yoe

# Map years of experience to node indices
yoes = {nodes[author]: yoe for author, yoe in results.items()}

# Create a list of node indices ordered by years of experience in decreasing order
YOE_FEATURE = [node_index for node_index, _ in sorted(yoes.items(), key=lambda item: item[1], reverse=True)]
print('YOE feature processed.')


""" 5 init Graph
"""
kol_graph = nx.Graph()


""" 6 add nodes and edges
"""
for kol_name, id in nodes.items():
    kol_graph.add_node(id, name=kol_name)

for edge in edges:
    source = edge['source']
    target = edge['target']
    kol_graph.add_edge(source, target)   

node_seq = list(kol_graph.nodes())
random.shuffle(node_seq)

list_graph = []
list_n_seq = []
list_num_node = []

list_graph.append(kol_graph)
list_n_seq.append(node_seq)
list_num_node.append(len(node_seq))


""" 7 get adj matrix
"""
list_adj_bet, list_adj_bet_t = graph_to_adj_bet(list_graph, list_n_seq, list_num_node, model_size)

list_adj_close, list_adj_close_t = graph_to_adj_close(list_graph, list_n_seq, list_num_node, model_size)


""" 8 predict
"""
def predict(model, list_adj, list_adj_t):
    model.eval()

    adj = list_adj[0]
    adj_t = list_adj_t[0]

    adj = adj.to(device)
    adj_t = adj_t.to(device)
    
    with torch.no_grad():
        y_out = model(adj,adj_t)

    y_out = y_out.reshape((model_size))
    y_out = y_out.cpu().detach().numpy()

    top_k = y_out.argsort()[::-1]

    res = []
    for index in top_k:
        if index >= len(node_seq):
            res.append(-1)
        else:
            res.append(node_seq[index])
    
    return res
    

# for BC
model1 = torch.load(MODEL_PATH_BET)
model1.to(device)

print('Predicting BC...')
BC = predict(model1, list_adj_bet,list_adj_bet_t)

# for CC
model2 = torch.load(MODEL_PATH_CLOSE)
model2.to(device)

print('Predicting CC...')
CC = predict(model2, list_adj_close,list_adj_close_t)

# for DC
res = nx.degree_centrality(kol_graph)
kol_list = sorted(res.items(), key=lambda x: x[1], reverse=True)

print('Predicting DC...')
DC = []
for kol in kol_list:
    DC.append(kol[0])

# print(BC[:100])
# print(CC[:100])
# print(DC[:100])


""" 9 ranking
"""
print('Computing weights...')
weights = np.zeros(len(node_seq))

for i in range(len(node_seq)):
    current_node = YOE_FEATURE[i]
    weights[current_node] += i * 0.2
 
for i in range(len(node_seq)):
    current_node = DC[i]
    weights[current_node] += i

for i in range(model_size):
    current_node = BC[i]
    if current_node != -1:
        weights[current_node] += i

for i in range(model_size):
    current_node = CC[i]
    if current_node != -1:
        weights[current_node] += i

ranking = weights.argsort()[:50]

print('Final ranking with DC CC and BC:')
print(ranking)


print('Result:')
kol_list = []
rank = 1
for id in ranking:
    kol_name = ''
    for name, author_id in nodes.items():
        if id == author_id:
            print('top ' + str(rank) + ': ' + name)
            kol_name = name
            break

    kol_score = weights[id]
    kol_yoe = yoes[id]

    info = {
        'kol_name': kol_name,
        'kol_score': kol_score,
        'kol_yoe': kol_yoe
    }
    kol_list.append(info)
    rank += 1       

with open(SAVE_DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(kol_list, f, ensure_ascii=False, indent=4)
