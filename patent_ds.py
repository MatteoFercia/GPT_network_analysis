import matplotlib.pyplot as plt
import networkx as nx
import json

G = nx.Graph()

with open('nodes.json') as a:
    dict1 = json.load(a)
print(dict1)

for i in dict1:
    G.add_nodes_from([i['id']])
print(G.nodes)

with open('links.json') as a:
    dict2 = json.load(a)
print(dict2)

for i in dict2:
    d = {}
    d['weight'] = i['value']
    G.add_edges_from([(i['source'],i['target'], d)])
print(G.edges)


nx.draw(G)
print('end')

