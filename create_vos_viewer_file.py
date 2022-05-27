import json
import random

#map file -------------------------------

map_file= open("map.txt","w+")
map_file.write('id,label,weight,x,y,score\n')

with open('nodes.json') as a:
    dict1 = json.load(a)
print(dict1)

for i in dict1:
    x = random.randint(1, 100)
    y = random.randint(1, 100)
    map_file.write(f'{i["id"]},{i["group"]},{i["weight"]},{x},{y},{i["weight"]}\n')


#Net file -------------------------------

net_file= open("net.txt","w+")

with open('links.json') as a:
    dict2 = json.load(a)
print(dict2)

for i in dict2:
    net_file.write(f'{i["source"]},{i["target"]},{i["value"]}\n')