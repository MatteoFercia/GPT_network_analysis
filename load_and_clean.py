# ----------------------------------------------------------------------------------------------------------------------

import pandas as pd
from collections import defaultdict
from statistics import mean
from list_datasets import datasets

# ----------------------------------------------------------------------------------------------------------------------

def load_dataset(path):
    return pd.read_csv(path, low_memory=False, sep=",", index_col="Publication Number")

# ----------------------------------------------------------------------------------------------------------------------

def get_patent_title(path, patent_code):
    ds = load_dataset(path) ; columns = list(ds.columns)
    for column in columns:
        if 'Title' in column and 'DWPI' in column: colonna = column ; break
    ds = ds[[f'{colonna}']]
    ds = ds.filter(items=[patent_code], axis=0)
    try: return ds[f'{colonna}'].values[0]
    except: return ''

# ----------------------------------------------------------------------------------------------------------------------

def clean_classes(dict1):
    for publication_date in dict1.keys():
        for item in dict1[publication_date]:
            try: float(item) ; dict1[publication_date].remove(item)
            except:
                if item == "": dict1[publication_date].remove(item)
        lista_codes = " | ".join([ str(item) for item in dict1[publication_date] ])
        dict1[publication_date] = lista_codes.split(' | ')
    return dict1


def level_of_detail_class(dict1, x=5):
    for publication_date in dict1.keys():
        app=[]
        for item in dict1[publication_date]:
            try: float(item)
            except:
                try: app.append(item[:x])
                except: app.append(item[:5])
        dict1[publication_date]=app
    return dict1

def count_occurrences_classes(dict1):
    for publication_date in dict1.keys():
        cpc_year = []
        for item in dict1[publication_date]:
            cpc_year.append((item, dict1[publication_date].count(item)))
        dict1[publication_date] = list(set(cpc_year))
    return dict1

def add_index(dict1):
    i = 1
    for year in dict1.keys():
        cpc_year_with_index = []
        for item in dict1[year]:
            cpc_year_with_index.append((i, item[0], item[1]))
            i += 1
        dict1[year] = cpc_year_with_index
    return dict1

def extract_dicts_classes(path,date, NumLettClasses=5, index=True, clean=True):
    ds_vos = load_dataset(path)
    dict1 = defaultdict(list)
    for publication_date, dwpi_code in ds_vos[["Publication Date", "DWPI Manual Codes"]].values:
        if publication_date[:4]<= date:
            dict1[publication_date[:4]].append(dwpi_code)
    if clean:
        dict1 = clean_classes(dict1)
        dict1 = level_of_detail_class(dict1, x=NumLettClasses)
        dict1 = count_occurrences_classes(dict1)
        if index: dict1 = add_index(dict1)
    return dict1

# ----------------------------------------------------------------------------------------------------------------------

def get_importance(path):
    diz = extract_dicts_classes(path)
    importance = defaultdict(list)
    for publication_date in diz.keys():
        for _, code, occurrences  in diz[publication_date]:
            importance[publication_date].append((code, occurrences/len(diz[publication_date])))
            # len(diz[publication_date]) is the number of classes appeared that year
    importance = dict(importance)
    for publication_date in importance.keys(): importance[publication_date]=dict(importance[publication_date])
    return importance

# ----------------------------------------------------------------------------------------------------------------------

def get_codes_patents(dict1, publication_date):
    codes_patents=[ codes_patent.split(' | ') for codes_patent in dict1[publication_date] if str(codes_patent)!='nan' ]
    app2 = []
    for patent in codes_patents:
        app1 = []
        for classe in patent:
            app1.append(classe[:5])
        app2.append(app1)
    codes_patents = [list(set(patent)) for patent in app2]
    return codes_patents

def get_frequency_code(code, codes_patents):
    count=0
    for patent in codes_patents:
        if code in patent: count+=1
    return count


def get_classes_appeared_that_year(dict1, publication_date):
    return list(set([ code for code, _ in dict1[publication_date] ]))

def get_pairs(codes, doubles=True):
    # doubles concerns about cases like: "T01-N_T01-J" & "T01-J_T01-N"
    if doubles: return [f'{code1}_{code2}' for code1 in codes for code2 in codes]
    if not doubles:
        app = []
        for pair in [f'{code1}_{code2}' for code1 in codes for code2 in codes]:
            code1, code2 = pair.split('_')
            if f"{code2}_{code1}" not in app: app.append(pair)
        return app

def get_pairs_patent(brevetti_with_classes, doubles=False):
    app = dict()
    for patent_id, codes in brevetti_with_classes.items():
        app[patent_id] = get_pairs(codes, doubles=doubles)
    return app

def count_pairs(patent_with_pairs_code, pairs):
    for patent_id, couples in patent_with_pairs_code.items():
        for couple in couples:
            code1, code2 = couple.split('_')
            if couple in pairs.keys(): pairs[f"{code1}_{code2}"]+=1
            else: pairs[f"{code2}_{code1}"]+=1
    return pairs

def get_counted_pairs(dict2, publication_date, dict1):
    app, i = [], 0
    for item in dict2[publication_date]: app.append((i, item)); i += 1
    brevetti_with_classes = dict(app)
    codes_year = get_classes_appeared_that_year(dict1, publication_date)
    pairs = get_pairs(codes_year, doubles=False)
    pairs = dict([(pair, 0) for pair in pairs])
    da_eliminare = []
    for patent_id, codes in brevetti_with_classes.items():
        try: brevetti_with_classes[patent_id] = set([code[:5] for code in codes.split(' | ')])
        except: da_eliminare.append(patent_id)
    for key in da_eliminare: del brevetti_with_classes[key]
    patent_with_pairs_code = get_pairs_patent(brevetti_with_classes)
    counted_pairs = count_pairs(patent_with_pairs_code, pairs)
    return counted_pairs

def frequencies_code_together(code1, code2, counted_pairs):
    if f"{code1}_{code2}" in counted_pairs.keys(): return counted_pairs[f"{code1}_{code2}"]
    elif f"{code2}_{code1}" in counted_pairs.keys(): return counted_pairs[f"{code2}_{code1}"]
    else: return 0

def get_probabilities(path):
    dict1 = extract_dicts_classes(path=path, index=False)
    dict2 = extract_dicts_classes(path=path, clean=False)
    probabilities = defaultdict(dict)
    publication_dates = [ publication_date for publication_date in dict2.keys() ]
    for publication_date in publication_dates:
        codes_patents = get_codes_patents(dict2, publication_date)
        counted_pairs = get_counted_pairs(dict2, publication_date, dict1)
        classes_appeared_that_year = get_classes_appeared_that_year(dict1, publication_date)
        pairs=get_pairs(classes_appeared_that_year)
        i=0 ; print(len(pairs))
        for couple in set(pairs):
            code1, code2 = couple.split('_')
            frequency_code1 = get_frequency_code(code1, codes_patents)
            couple_frequencies = frequencies_code_together(code1, code2, counted_pairs)
            print(i, code1, code2, couple_frequencies/frequency_code1) ; i+=1
            probabilities[publication_date][couple] = couple_frequencies/frequency_code1
    return probabilities

def write_probabilities(probabilities, dataset=''):
    for publication_date in probabilities.keys():
        with open(f'../Probabs/{dataset}/probabs_{dataset}_{publication_date}.csv', 'w') as f:
            f.write("Couple,Probability\n")
            for couple in probabilities[publication_date].keys():
                f.write("%s,%s\n" % (couple, probabilities[publication_date][couple]))

# ----------------------------------------------------------------------------------------------------------------------

def get_all_possible_companies(path=''):
    if not path:
        paths = [ datasets[dataset].replace('./app/PatentAnalysis', '..') for dataset in datasets.keys() ]
        dfs = [ load_dataset(path) for path in paths ]
        app = [ df['Ultimate Parent'].values  for df in dfs ]
        app = [ company for item in app for company in item.tolist() if str(company) != 'nan' ]
        companies = [ company  for comps in app for company in comps.split(' | ') if str(comps) != 'nan' ]
        return list(set([(company, companies.count(company)) for company in companies]))
    else:
        df = load_dataset(path)
        app = df['Ultimate Parent'].values
        app = [ company for company in app.tolist() if str(company) != 'nan']
        companies = [ company for comps in app for company in comps.split(' | ') if str(comps) != 'nan']
        return list(set([(company, companies.count(company)) for company in companies]))

def get_patents_companies(path, NumLettClasses=5):
    ds = load_dataset(path) ; ds = ds[['Ultimate Parent', 'DWPI Manual Codes']]
    codes = defaultdict(list)
    for _, company, list_codes in ds.to_records():
        try:
            split_companies = company.split(' | ')
            for comp in split_companies:
                codes[comp].append(list_codes)
        except: pass
    for company in codes.keys():
        codes[company] = [ code for code in codes[company] if str(code) != 'nan']
        app = ' | '.join(codes[company]) ; codes[company] = app.split(' | ')
    companies = []
    for company, num_patents in get_all_possible_companies(path=path): #get_companies(path):
        cods = [ code[:NumLettClasses] for code in codes[company] ]
        companies.append((company, [num_patents, cods ]))
    return dict(companies)

def get_effort_micro(path):
    companies = get_patents_companies(path)
    effort_micro = defaultdict(dict)
    for company in companies.keys():
        list_codes = companies[company][1]
        # num_patents_company = companies[company][0]
        for code in list_codes:
            effort_micro[company][code] = list_codes.count(code)/len(list_codes)#*num_patents_company
    return effort_micro

# ----------------------------------------------------------------------------------------------------------------------

def get_effort_macro(path):
    effort_micro = get_effort_micro(path)
    effort_macro = defaultdict(list)
    companies = get_patents_companies(path)
    for company in companies.keys():
        list_codes = companies[company][1]
        num_patents_company = companies[company][0]
        for code in list_codes:
            effort_macro[code].append(effort_micro[company][code]*num_patents_company)
    for code in effort_macro.keys(): effort_macro[code] = mean(effort_macro[code])
    return dict(effort_macro)


# ----------------------------------------------------------------------------------------------------------------------

if __name__=='__main__':
    # write_probabilities(get_probabilities("../Datasets/Blockchain_patent families.csv"), dataset='Blockchain')
    # write_probabilities(get_probabilities("../Datasets/Digital Twins.csv"), dataset='Digital Twins')
    print('Done')

# ----------------------------------------------------------------------------------------------------------------------