from json import dump
d = {}
for i in range(16):
    d[i+1] = {"on": False}
with open('lights_states.json', 'w') as f:
    dump(d, f)