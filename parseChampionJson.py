import json

with open('champion.json', 'r', encoding='utf-8') as f:
    json_data = f.read()

data = json.loads(json_data)

champIdToName = {}
champNameToId = {}
champNameToMyId = {}

index = 0
for champ_name, champ_data in (data['data'].items()):
    champNameToId[champ_name] = champ_data['key']
    champIdToName[champ_data['key']] = champ_name
    champNameToMyId[champ_name] = index
    index += 1

with open('champNameToId.json', 'w') as f:
    f.write(json.dumps(champNameToId))

with open('champIdToName.json', 'w') as f:
    f.write(json.dumps(champIdToName))

with open('champNameToMyId.json', 'w') as f:
    f.write(json.dumps(champNameToMyId))