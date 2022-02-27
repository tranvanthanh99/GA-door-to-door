import sys
import random
import numpy as np
from Optimizers.Chromesome import Chromesome



class GA():
    def __init__(self, graph, params) -> None:
        self.graph = graph
        self.params = params

    def init_pop(self):
        pop = []
        rng = np.random.default_rng()
        gen = np.round((self.params['technician_num']-(10**-self.params['accuracy'])) * rng.random((self.graph.numNodes - 1) * 2, dtype=np.float32), self.params['accuracy'])
        idv = Chromesome(self.graph, gen, self.params['technician_num'])
        pop.append(idv)
        for _ in range(self.params['pop_size']):
            while self.is_duplicated(pop, idv):
                gen = np.round((self.params['technician_num']-(10**-self.params['accuracy'])) * rng.random((self.graph.numNodes - 1) * 2, dtype=np.float32), self.params['accuracy'])
                idv = Chromesome(self.graph, gen, self.params['technician_num'], False)
            idv.get_fitness(idv.decode[2], idv.decode[1], idv.decode[0])
            pop.append(idv)

        # genes_list = np.round((self.params['technician_num']-(10**-self.params['accuracy'])) * rng.random((self.params['pop_size'], ((self.graph.numNodes - 1) * 2)), dtype=np.float32), self.params['accuracy'])
        # for gen in genes_list:
        #     pop.append(Chromesome(self.graph, gen, self.params['technician_num']))
        return pop

    def crossover_SBX(self, p1, p2, eta_c):
        c1 = np.zeros((self.graph.numNodes - 1) * 2, dtype=np.float32)    
        c2 = np.zeros((self.graph.numNodes - 1) * 2, dtype=np.float32)    
        for i in range(p1.genes.shape[0]):
            u = random.random()
            if u <= 0.5:
                beta = (2.0 * u) ** (1.0 / (eta_c + 1.0))
            else:
                beta = (0.5 / (1.0 - u)) ** (1.0 / (eta_c + 1.0))
            c1[i] = 0.5*((1.0 + beta) * p1.genes[i] + (1.0 - beta) * p2.genes[i])
            c2[i] = 0.5*((1.0 - beta) * p1.genes[i] + (1.0 + beta) * p2.genes[i])
            c1[i], c2[i] = round(c1[i], self.params['accuracy']), round(c2[i], self.params['accuracy'])
            c1[i] = min(max(c1[i], 0), self.params['technician_num']-(10**-self.params['accuracy']))
            c2[i] = min(max(c2[i], 0), self.params['technician_num']-(10**-self.params['accuracy']))
        return Chromesome(self.graph, c1, self.params['technician_num'], False), Chromesome(self.graph, c2, self.params['technician_num'], False)

    def crossover_BLX(self, p1, p2, alpha):
        c1 = np.zeros((self.graph.numNodes - 1) * 2, dtype=np.float32)    
        c2 = np.zeros((self.graph.numNodes - 1) * 2, dtype=np.float32) 
        for i in range(p1.genes.shape[0]):
            d = abs(p1.genes[i] - p2.genes[i])
            X1 = min(p1.genes[i], p2.genes[i]) - (alpha * d)
            X2 = max(p1.genes[i], p2.genes[i]) + (alpha * d)
            c1[i] = (X2 - X1) * random.random() + X1
            c1[i] = min(max(c1[i], 0), self.params['technician_num']-(10**-self.params['accuracy']))
        return Chromesome(self.graph, c1, self.params['technician_num'], False)

    def mutate_poly(self, c, prob, eta_m):
        if random.random() < prob:
            for i in range(c.genes.shape[0]):
                u = random.random()
                if u <= 0.5:
                    delta = (2 * u) ** (1.0 / (eta_m + 1.0)) - 1.0
                else:
                    delta = 1.0 - (2.0 * (1.0 - u)) ** (1.0 / (eta_m + 1.0))
                if u <= 0.5:
                    c.genes[i] = c.genes[i] + delta * c.genes[i]
                else:
                    c.genes[i] = c.genes[i] + delta * (1.0 - c.genes[i])
                c.genes[i] = round(c.genes[i], self.params['accuracy'])
                c.genes[i] = min(max(c.genes[i], 0), self.params['technician_num']-(10**-self.params['accuracy']))
            c.decoder()

    def tournament_selection(self, pop):
        # Selecting randomly 4 individuals to select 2 parents by a binary tournament
        p_ids = set()
        while len(p_ids) < 4:
            p_ids |= {random.randint(0, len(pop) - 1)}
        p_ids = list(p_ids)
        # Selecting 2 parents with the binary tournament
        parent1 = pop[p_ids[0]] if pop[p_ids[0]].fitness < pop[p_ids[1]].fitness else pop[p_ids[1]]
        parent2 = pop[p_ids[2]] if pop[p_ids[2]].fitness < pop[p_ids[3]].fitness else pop[p_ids[3]]
        return parent1, parent2

    def rank_pop(self, pop):
        fitness_results = {}
        for i in range(0, len(pop)):
            fitness_results[i] = pop[i].fitness
        pop_ranked = sorted(fitness_results.items(), key = lambda x: x[1], reverse = False)
        return list(map(lambda x: x[0], pop_ranked))

    def select_elite(self, pop, pop_ranked, eliteSize):
        elite_pop = []
        for i in pop_ranked[:eliteSize]:
            elite_pop.append(pop[i])
        return elite_pop

    def is_duplicated(self, pop, idv):
        for chromesome in pop:
            if idv.decode_str == chromesome.decode_str:
                return True
        return False

    def run(self, exports):

        pop = self.init_pop()
        # p1, p2 = self.tournament_selection(pop)
        # self.rank_pop(pop)
        # c1, c2 = self.crossover_SBX(pop[0], pop[1], 2)
        # print(c1.decode_str, c2.decode_str)
        # print(pop[0].decode_str, pop[1].decode_str)
        # print(pop[0].decode_str)
        # self.mutate_poly(pop[0], 1, 2)
        # print(pop[0].decode_str)
        # sys.exit()
        # print(self.is_duplicated(pop, c2))

        # cal_pop = []
        cal_pop = set()
        record = {
            'convergence': [],
        }

        for i in range(0, self.params['generations']):
            # print("=====================================")
            # print(f'generation {i+1}')
            
            for idv in pop:
                cal_pop.add(idv.decode_str)

            pop_ranked = self.rank_pop(pop)
            best_idv = pop[pop_ranked[0]]
            # print(f'best_fitness: {best_idv.fitness}')
            # print(best_idv.decode[0])
            # print(best_idv.detail[1])

            if exports['save_stats']:
                record['convergence'] +=[best_idv.fitness]

            next_pop = self.select_elite(pop, pop_ranked, self.params['elite_size'])
            while (len(next_pop) < self.params['pop_size']):
                p1, p2 = self.tournament_selection(pop)
                c1, c2 = self.crossover_SBX(p1, p2, 1)

                # p1, p2 = self.tournament_selection(pop)
                # p3, p4 = self.tournament_selection(pop)
                # c1, c2 = self.crossover_BLX(p1, p2, 0.5), self.crossover_BLX(p3, p4, 0.5)

                self.mutate_poly(c1, self.params['mutation_rate'], 1)
                self.mutate_poly(c2, self.params['mutation_rate'], 1)
                # while self.is_duplicated(pop, c1) and self.is_duplicated(pop, c2):
                while c1.decode_str in cal_pop and c2.decode_str in cal_pop:
                    # print(c1.decode_str, c2.decode_str)
                    p1, p2 = self.tournament_selection(pop)
                    c1, c2 = self.crossover_SBX(p1, p2, 1)

                    # p1, p2 = self.tournament_selection(pop)
                    # p3, p4 = self.tournament_selection(pop)
                    # c1, c2 = self.crossover_BLX(p1, p2, 0.5), self.crossover_BLX(p3, p4, 0.5)

                    self.mutate_poly(c1, self.params['mutation_rate'], 1)
                    self.mutate_poly(c2, self.params['mutation_rate'], 1)
                if c1.decode_str not in cal_pop:
                    c1.get_fitness(c1.decode[2], c1.decode[1], c1.decode[0])
                    next_pop += [c1]
                if c2.decode_str not in cal_pop:
                    c2.get_fitness(c2.decode[2], c2.decode[1], c2.decode[0])
                    next_pop += [c2]
            pop = next_pop[:self.params['pop_size']]
        return best_idv, record

