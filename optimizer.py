import sys
import time
import matplotlib.pyplot as plt
import time

from Optimizers import Map as map
from Optimizers.GA import GA
from Optimizers.Utils import save_solution, save_stats

def run(run_type, file_inputs, params, exports):
    current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    input_dirs = []
    for num_node in file_inputs['num_nodes']:
        for r in file_inputs['range']:
            for file_num in file_inputs['file_num']:
                input_dir = file_inputs['input_folder'] + str(num_node) + '.' + str(r) + '.' + str(file_num) + '.txt'
                input_dirs.append(input_dir)
    
    
    #run
    for input_dir in input_dirs:
        for _ in range(run_type['num_of_runs']):
            graph = map.Map(input_dir)
            optimizer = GA(graph, params)
            if run_type['run_version'] == 0:
                start = time.time()
                best_solution, record = optimizer.run(exports)
                run_time = time.time() - start
            total_tech = str(best_solution.technician_num) + '/' + str(params['technician_num'])
            params_str = str(params['pop_size']) + '|' + str(params['generations']) + '|' + str(params['work_time'])
            if exports['to_excel']:
                save_solution(instance=graph.fileName, 
                            run_time=run_time, 
                            number_of_tech=total_tech, 
                            cost=best_solution.cost, 
                            work_time=best_solution.detail[2], 
                            version=run_type['run_version'],
                            params=params_str, 
                            t_route=str(best_solution.decode[0]), 
                            uav_route=str(best_solution.detail[1]),
                            current_time=current_time)

            if exports['save_stats']:
                save_stats(instance=graph.fileName,
                        version=run_type['run_version'],
                        run_time=run_time,
                        tech_num=total_tech,
                        work_time=params['work_time'],
                        level='upper',
                        record=record['convergence'],
                        params=params_str,
                        current_time=current_time)
