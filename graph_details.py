# ----------------------------------------------------------------------------------------------------------------------

import networkx as nx
import json

# ----------------------------------------------------------------------------------------------------------------------

def get_results(years):
    results = {}

    for year in years:
        G = nx.Graph()
        with open(f'./Blockchain/nodes_{year}.json') as a:
            dict1 = json.load(a)
        for i in dict1:
            G.add_nodes_from([i['id']])
        with open(f'./Blockchain/links_{year}.json') as a:
            dict2 = json.load(a)

        lista_generi = []
        for i in dict2:
            lista_generi.append(i['source'][0])
        lista_generi = list(set(lista_generi))
        coppie = []
        for i in lista_generi:
            for j in lista_generi:
                if (i,j) not in coppie and (j,i) not in coppie and i!=j:
                    coppie.append((i,j))

        omofilies = {}
        for coppia in coppie:
            link_omo, link_eter = 0,0
            app = [ item for item in dict2 if item['source'][0]==coppia[0] or item['source'][0]==coppia[1] ]
            totale = len(app)
            for i in app:
                if i['source'][0] == i['target'][0]:
                    link_omo += 1
                else:
                    link_eter += 1

            p = link_omo/totale
            q =  link_eter/totale
            prod = 2*p*q

            if q < prod:
                test = 'True'
            else:
                test = 'False'

            omofilies[coppia] = test


        for i in dict2:
            d = {}
            d['weight'] = float(i['value'])
            G.add_edges_from([(i['source'], i['target'], d)])

        results[year] = {'betweennes':
                         nx.betweenness_centrality(G, k=None, normalized=True, endpoints=False, seed=None),
                         'centrality': nx.degree_centrality(G),
                         'clustering_coef': nx.clustering(G, weight='weight'),
                         'omophily': omofilies,
                         'density': nx.density(G)
                         }

    return results


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    years = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020']
    results = get_results(years=years)
    print(results)

    print('Main done.')

# ----------------------------------------------------------------------------------------------------------------------