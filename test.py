import time

from Optimizers.GA import GA
from Optimizers.Map import Map
from main import params, exports

graph = Map("Instances/10.10.3.txt")
ga = GA(graph, params)
s = time.time()
ga.run(exports)
e = time.time()
print(f'run times: {e - s}')