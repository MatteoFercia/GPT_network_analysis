import json
import random


years = ['2010','2012','2015','2017','2019']

#map file -------------------------------
for year in years:
    map_file= open(f"./Blockchain/map/map_{year}.txt","w+")
    map_file.write('id,label,weight,x,y,score\n')

    with open(f'./Blockchain/nodes_{year}.json') as a:
        dict1 = json.load(a)

    for i in dict1:
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        map_file.write(f'{i["id"]},{i["id"]},{i["weight"]},{x},{y},{i["weight"]}\n')


#Net file -------------------------------

for year in years:
    net_file= open(f"./Blockchain/net/net_{year}.txt","w+")

    with open(f'./Blockchain/links_{year}.json') as a:
        dict2 = json.load(a)

    for i in dict2:
        net_file.write(f'{i["source"]},{i["target"]},{i["value"]}\n')