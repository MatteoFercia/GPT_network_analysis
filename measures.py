# ----------------------------------------------------------------------------------------------------------------------

import json
import math
import networkx as nx
from statistics import mean
from collections import defaultdict
from load_and_clean import extract_dicts_classes

# ----------------------------------------------------------------------------------------------------------------------

def get_weights(dict):
    weights = defaultdict(list)
    for year in dict.keys():
        for index, classe, occurrences in dict[year]:
            weight = occurrences / len(dict[year]) # numero occorrenze / numero totale di classi apparse
            weights[classe].append(weight)
    app={ classe:mean(weights[classe]) for classe in weights.keys() }
    max_weight = max(app.values())
    app2={ classe:(app[classe] * 30)/max_weight for classe in app.keys() }
    weights = {}
    for classe in app2.keys():
        if app2[classe]<1: weights[classe]=round(math.log(1)+4,2)
        else: weights[classe] = round(math.log(app2[classe]*10)+4,2)
    return weights

def find_clusters(dataset, threshold, date):
    input_filename = f'./{dataset.title()}/links_{date}.tsv' ; output_filename = f'./{dataset.title()}/links_{date}.json'
    tsv2json(input_filename, output_filename, threshold)
    links = json.load(open(output_filename))
    G = nx.Graph()
    for diz in links:
        G.add_edge(diz['source'], diz['target'])
    clusters = nx.clustering(G)
    rounded_clusters = { key:value for key, value in clusters.items() }
    return rounded_clusters

def scrivifile_nodes(name, dict, dataset, weights, threshold, date):
    nodes = open(name, "w")
    rounded_clusters = find_clusters(dataset=dataset, threshold=threshold, date=date)
    nodes.write("id\tgroup\tweight\n")
    classes_done=[]
    for year in dict.keys():
        for index, classe, occurences in dict[year]:
            if classe not in classes_done:
                try: nodes.write(f"{classe}\t{int(rounded_clusters[classe]*10)}\t{weights[classe]}\n") ; classes_done.append(classe)
                except: pass
    nodes.flush() ; nodes.close()

def get_classes_appeared_together(links,NumLettClasse=5):
    comparse_insieme = defaultdict(list)
    for year in links.keys():
        for classi_brevetto_singolo in links[year]:
            try: float(classi_brevetto_singolo)
            except:
                for classe in classi_brevetto_singolo.split(' | '):
                    for classe2 in classi_brevetto_singolo.split(' | '):
                        if classe2 != classe:
                            try: comparse_insieme[classe[:NumLettClasse]].append(classe2[:NumLettClasse])
                            except: comparse_insieme[classe[:5]].append(classe2[:5])
    return comparse_insieme

def coefficients_due_classi(links):
    comparse_insieme = get_classes_appeared_together(links)
    diz_comparse_insieme = defaultdict(int)
    for classe in comparse_insieme.keys():
        for classe2 in comparse_insieme[classe]:
            diz_comparse_insieme[f"{classe}_{classe2}"] = comparse_insieme[classe].count(classe2)/100
    return diz_comparse_insieme

def scrivifile_links(name, diz_comparse_insieme):
    links = open(name, "w")
    links.write(f"source\ttarget\tvalue\n")
    for classi in diz_comparse_insieme.keys():
        classe1, classe2 = classi.split('_')
        links.write(f"{classe1}\t{classe2}\t{diz_comparse_insieme[classi]}\n")
    links.flush() ; links.close()

def tsv2json(input_file, output_file, threshold, links=[]):
    arr = []
    file = open(input_file, 'r')
    a = file.readline()
    titles = [t.strip() for t in a.split('\t')]
    for line in file:
        d = {}
        for t, f in zip(titles, line.split('\t')):
            d[t] = f.strip()
        # questo if serve per costruire una mappa più snella, prendendo solo le coppie che compaiono insieme almeno
        # hanno come value almeno il threshold
        if 'value' in d.keys() and float(d['value']) > threshold: arr.append(d)
        elif 'value' not in d.keys():
            for link in links:
                if d['id']==link['source']:
                    arr.append(d)
                    break
    with open(output_file, 'w', encoding='utf-8') as output_file:
        output_file.write(json.dumps(arr, indent=4))
    print('Tsv to Json done.')

def merge_json_files(dataset, date):
    try:
        map = {
                "nodes": json.load(open(f'nodes_{date}.json')),
                "graph_map_net": json.load(open(f'links_{date}.json'))
              }
        with open(f"{dataset.title()}_{date}.json", "w") as outfile:
            json.dump(map, outfile, indent=4)
        print('Map Done')
    except:
        map = {
                "nodes": json.load(open(f'nodes_{date}.json')),
                "graph_map_net": json.load(open(f'links_{date}.json'))
              }
        with open(f"{dataset.title()}_{date}.json", "w") as outfile:
            json.dump(map, outfile, indent=4)
        print('Map Done')


def write_tsv(dataset, dict1, weights, diz_comparse_insieme, date):
    scrivifile_links(name=f"./{dataset.title()}/links_{date}.tsv", diz_comparse_insieme=diz_comparse_insieme)
    print(f'Links.tsv {dataset.title()} done.')
    scrivifile_nodes(name=f"./{dataset.title()}/nodes_{date}.tsv", dict=dict1, dataset=dataset.title(), weights=weights,threshold=0, date=date)
    print(f'Nodes.tsv {dataset} done.')

def pipeline_map(path, dataset, threshold=0.1, first_time=False, date='2018'):
    links = extract_dicts_classes(path, clean=False, date=date)
    print(links)
    if first_time:
        dict1 = extract_dicts_classes(path, date=date)
        weights = get_weights(dict1)
        diz_comparse_insieme = coefficients_due_classi(links=links)
        print(diz_comparse_insieme)
        write_tsv(dataset=dataset,dict1=dict1,weights=weights,diz_comparse_insieme=diz_comparse_insieme, date=date)
    try:
        input_filename = f'./{dataset.title()}/links_{date}.tsv' ; output_filename = f'./{dataset.title()}/links_{date}.json'
        tsv2json(input_filename, output_filename, threshold=threshold)
        print(f'Links.json {dataset.title()} done.')
        links = json.load(open(f'./{dataset.title()}/links_{date}.json'))
        input_filename = f'./{dataset.title()}/nodes_{date}.tsv';
        output_filename = f'./{dataset.title()}/nodes_{date}.json'
        tsv2json(input_filename, output_filename, threshold=threshold, links=links)
        print(f'Nodes.json {dataset.title()} done.')
    except:
        input_filename = f'links_{date}.tsv'
        output_filename = f'links_{date}.json'
        tsv2json(input_filename, output_filename, threshold=threshold)
        print('Links_.json done.')
        links=json.load(open(f'links_{date}.json'))
        input_filename = f'nodes_{date}.tsv'
        output_filename = f'nodes_{date}.json'
        tsv2json(input_filename, output_filename, threshold=threshold, links=links)
        print('Nodes.json done.')
    merge_json_files(dataset=dataset, date=date)
    print('Pipeline done.')

# ----------------------------------------------------------------------------------------------------------------------

if __name__=="__main__":

    # to change the weights of the nodes you need to add the first_time option

    #path = "/Users/matteofercia/Desktop/datascience/network/blockchain_patents.csv"
    #pipeline_map(path=path, dataset='Digital Twins', threshold=0.2)

    path = "/Users/matteofercia/Desktop/datascience/network/blockchain_patents.csv"
    pipeline_map(path=path, dataset='Blockchain', threshold=0.04, date='2010', first_time=True)




# ----------------------------------------------------------------------------------------------------------------------
