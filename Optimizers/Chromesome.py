import sys
import copy
import numpy as np
from Optimizers.Utils import index_2d
from main import params


class Chromesome():
    def __init__(self, graph, genes, technician_num, isChosen=True) -> None:
        self.graph = graph
        self.genes = genes
        self.technician_num = technician_num
        self.decode = None
        self.decode_str = ''
        self.fitness = 0
        self.detail = None
        self.decoder()
        # print(self.decode_str)
        # sys.exit()
        if isChosen:
            self.get_fitness(self.decode[2], self.decode[1], self.decode[0])

    def decoder(self):
        # decode genes
        routes={}
        self.decode_str = ''
        # get specific route of each technician {0:{0,4,1,3}, 1:{2,5}}
        for index, gen in enumerate(self.genes[:self.graph.numNodes-1]):
            if int(gen) not in routes:
                routes[int(gen)] = []
            routes[int(gen)].append((index+1, gen))
        for tid in routes:
            routes[tid] = sorted(routes[tid], key=lambda x: x[1])
            routes[tid] = list(map(lambda x: x[0], routes[tid]))
            self.decode_str += '-'.join(map(str, routes[tid])) +'|'
        if params['technician_num'] != len(routes) or self.technician_num != len(routes):
            new_routes = {}
            self.technician_num = len(routes)
            for i, v in enumerate(routes.items()):
                new_routes[i] = v[1]
            routes = new_routes

        sorted_routes, _, _ = self.sort_by_time(routes)
        # self.decode_str += '-'.join(map(str, sorted_routes.keys())) +'|'

        uav_bin = []
        for gen in self.genes[self.graph.numNodes-1:]:
            if gen < params['technician_num'] / 3:
                uav_bin += [0,0]
                self.decode_str += '00'
            elif gen < params['technician_num'] * 2/3:
                uav_bin += [1,0]
                self.decode_str += '10'
            else:
                uav_bin += [1,1]
                self.decode_str += '11'
        uav_bin.pop()
        uav_bin = np.array(uav_bin, dtype=np.int8)

        self.decode = (routes, sorted_routes, uav_bin)

    def sort_by_time(self, specific_routes):
        routes = {}
        t_back_time = {}
        for tid in range(self.technician_num):
            path = specific_routes[tid]

            travel_time = 0 
            for index, node in enumerate(path):
                if index == 0:
                    travel_time += self.graph.ttime[0][node]
                    routes[node] = travel_time
                else:
                    travel_time += self.graph.ttime[path[index - 1]][path[index]]
                    routes[node] = travel_time
        
            t_back_time[tid] = travel_time + self.graph.ttime[path[-1]][0] #time that each technician gets back to base {'0': 132.3, '1': 212.23}

        sorted_routes = dict(sorted(routes.items(), key= lambda item: item[1])) #route sorted in time order
    
        #find max cost 
        max_cost = 0 #total cost when there are no uav support
        for tid in range(self.technician_num):
            for node in specific_routes[tid]:
                max_cost += t_back_time[tid] - sorted_routes[node] 

        return sorted_routes, t_back_time, max_cost

    def adjust_idv(self, idv, routes, specific_routes):
        t_map = list(specific_routes.values())
        t_end = [[-1] for _ in range(self.technician_num)]
        cur_trip = []
        for i in range(1, idv.shape[0], 2):
            if idv[i-1]:
                cur_trip.append(i-1)
                t_end[index_2d(t_map, routes[(i-1)//2])][0] = i-1
            if idv[i]:
                for last_des in t_end:
                    if last_des[0] >= 0:
                        cur_trip.remove(last_des[0])
                for des in cur_trip:
                    idv[des] = 0
                t_end = [[-1] for _ in range(self.technician_num)]
                cur_trip = []
            if i == idv.shape[0] - 2 and idv[i+1]:
                cur_trip.append(i+1)
                t_end[index_2d(t_map, routes[(i+1)//2])][0] = i+1
                for last_des in t_end:
                    if last_des[0] >= 0:
                        cur_trip.remove(last_des[0])
                for des in cur_trip:
                    idv[des] = 0

    def get_fitness(self, idv, sorted_routes, specific_routes):
        routes = list(sorted_routes.keys())
    

        search_space = copy.deepcopy(sorted_routes)
        # search_space = sorted_routes[:]

        # fix gene that violates the constraint
        self.adjust_idv(idv, routes, specific_routes)

        C = []

        for index in range(len(routes) -1):
            C.append(routes[index])
            C.append(0)
        
        C.append(routes[-1])
        # print(C)


        k = 0 # so luong hanh trinh cua uav
        uav_tour = {} 
        uav_tour[k] = []
        uav_tour[k].append(0)

        u_time = 0
        endurance = 0

        #route detail
        route_details = {}
        route_details['time_at_node'] = {}
        route_details['uav_route'] = []

        #[4, 0, 3, 0, 6, 0, 1, 0, 5, 0, 2]
        test_chosen_idx = [0, 1, 2, 3, 4,5,6,7,8,9]

        # cost = {}

        for i in range(0, len(C)):
            src = uav_tour[k][-1] #get last elemetn of uav tour k
            #for debug
            next_node = C[i] 
            # t_time = search_space[next_node]

            if C[i] == src: #if 2 node 0 in a row 
                continue

            if idv[i]: 
            #if i in test_chosen_idx:
                #expected destination and expected travel time 
                e_des = C[i]
                e_travel_time = self.graph.dtime[src][e_des]

                if e_des == 0:
                    u_time += e_travel_time
                    endurance += e_travel_time
                else:
                    #constrain 1: T
                    if endurance + e_travel_time + self.graph.dtime[e_des][0] > params['drone_time']: 
                        #if uav cannot flyback to base when chosing the e_des as next node 
                        route_details['time_at_node'][next_node] = (search_space[next_node], -1)
                        continue
                    else:
                        route_details['time_at_node'][next_node] = (search_space[next_node], u_time + e_travel_time)
                    
                    e_uav_arrive_time = u_time + e_travel_time #expected uav arrival time 
                     

                    if params['technician_can_wait']:
                        if e_uav_arrive_time > search_space[e_des]: #if uav come after technician
                            #TODO: make small func additional time that technician have to wait for uav at edes
                            for sid in specific_routes:
                                subtour = specific_routes[sid]

                                if e_des in subtour:
                                    index = subtour.index(e_des)           
                                    for updating_node in subtour[index+1 :(len(subtour))]:
                                        search_space[updating_node] += e_uav_arrive_time - search_space[e_des]

                            u_time = e_uav_arrive_time
                            endurance += e_travel_time
                            
                        else: #uav come before
                            u_time = search_space[e_des]
                            endurance += e_travel_time + (search_space[e_des]- e_uav_arrive_time) 

                    else:
                        # UAV arrive before techincan
                        if e_uav_arrive_time  > search_space[e_des]:
                            continue
                        
                        u_time = search_space[e_des]
                        endurance += e_travel_time

                uav_tour[k].append(e_des)
 
                #check if close subtour  
                if uav_tour[k][-1] == 0:
                    sub_route_data = {
                        'k': k,
                        'route': uav_tour[k],
                        'endurance': endurance
                    }
                    route_details['uav_route'].append(sub_route_data)

                    #create new subtour 
                    k = k + 1
                    uav_tour[k] = []
                    uav_tour[k].append(0)

                    #reset endurance 
                    endurance = 0
            else:
                if next_node != 0:
                    route_details['time_at_node'][next_node] = (search_space[next_node], -1)
            
        

        if uav_tour[k][-1] != 0:
            uav_tour[k].append(0)

            u_time += self.graph.dtime[uav_tour[k][-1]][0]

        if len(uav_tour[k]) == 1: #case when there are only start node 0
            del uav_tour[k]

        
        
        lattest_node = list(search_space.keys())[-1]
        work_time = search_space[lattest_node] + self.graph.ttime[lattest_node][0]
        
        # if work_time > params['work_time']:
        #     cost = INFINITY
        # else:
        #     cost, wait_times = self.find_cost(time_at_nodes=route_details['time_at_node'], uav_tour=uav_tour, specific_routes=specific_routes)
        #     route_details['wait_times'] = wait_times


        cost, wait_times = self.find_cost(time_at_nodes=route_details['time_at_node'], uav_tour=uav_tour, specific_routes=specific_routes)
        route_details['wait_times'] = wait_times
        if work_time > params['work_time']:
            penalty_rate = (work_time - params['work_time']) / params['work_time']
            penalty_rate = 0.8 * penalty_rate + 0.2
            cost += cost * penalty_rate

        self.fitness = cost
        self.detail = (route_details, uav_tour, work_time)
        # return cost, route_details, uav_tour, work_time
    
    def find_cost(self, time_at_nodes, uav_tour, specific_routes):

        t_back_time = {}
        
        specific_route = copy.deepcopy(specific_routes)
        # specific_route = specific_routes[:]
        wait_times = {}
       
        # print(time_at_nodes)
        for tid in specific_routes:
            
            path = specific_routes[tid]
            last_node = path[-1]
            
            
            time_leave_last_node = max(time_at_nodes[last_node][0],time_at_nodes[last_node][1] )
            t_back_time[tid] = time_leave_last_node + self.graph.ttime[last_node][0]

        
        #iterate over each subtour
        for stid in uav_tour:
            subtour = uav_tour[stid]
            
            #caculate time when uav back to base 
            last_sub_node_idx = len(subtour) - 2 #last node's index of uav subtour (except 0)
            back_time = max(time_at_nodes[subtour[last_sub_node_idx]][0],time_at_nodes[subtour[last_sub_node_idx]][1] )  + self.graph.dtime[subtour[last_sub_node_idx]][0] 


            #iterate over each non-zero node in above subtour
            for unid in range(1, (len(subtour) - 1)):
                #iterate over each technician route 
                for tid in specific_route:
                    index = -1

                    #if subtour node in route of tid technician 
                    if subtour[unid] in specific_route[tid]:
                        index = specific_route[tid].index(subtour[unid])

                        for finished_node in specific_route[tid][0:(index+1)]:
                            wait_times[finished_node] = (back_time - time_at_nodes[finished_node][0], 'uav')
                        
                        del specific_route[tid][0:(index+1)]

        #node that are brought back by technician
        for tid in specific_route:
            for node in specific_route[tid]:
                wait_times[node] = ((t_back_time[tid] - max(time_at_nodes[node][0],time_at_nodes[node][1] )), 'technician')
        
        cost = 0
        for idx in wait_times:
            cost += wait_times[idx][0]
        
        return cost, wait_times

