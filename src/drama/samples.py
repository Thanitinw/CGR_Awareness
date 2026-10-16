import json, os
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samples.json')
SAMPLES = {}
for e in json.load(open(_p)):
    k = tuple(e.pop('key')); SAMPLES[k] = e
