import matplotlib.pyplot as plt
import networkx as nx
import json

G = nx.Graph()

with open('Blockchain/nodes.json') as a:
    dict1 = json.load(a)
print(dict1)

for i in dict1:
    G.add_nodes_from([i['id']])
print(G.nodes)

with open('Blockchain/links.json') as a:
    dict2 = json.load(a)
print(dict2)

for i in dict2:
    d = {}
    d['weight'] = i['value']
    if i['source'] == i['target']:
        pass
    else:
        G.add_edges_from([(i['source'],i['target'], d)])
print(G.edges)


#nx.draw(G, with_labels = True)

#pos = nx.circular_layout(G)
#nx.draw(G, pos=pos, with_labels = True)

#plt.show()

#---------------------------------

