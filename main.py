import optimizer

run_type = {
    # 'level': 'upper',
    'num_of_runs': 5,
    'run_version': 0
}

file_inputs = {
    'input_folder': 'Instances/',
    'num_nodes': [10],
    'range': [20],
    'file_num': [1]
    # 'num_nodes': [6],
    # 'range': [5],
    # 'file_num': [3]
}

params = {
    'create_sample': 'txt',
    'generations': 50,
    'pop_size': 200,
    'elite_size': 10,
    'accuracy': 2,  # 2 ~ 0.01, 3 ~ 0.001
    'mutation_rate':  0.1,
    "distance_rate": 0.1,
    'drone_time': 30000,
    'work_time': 120,
    'technician_num': 1,
    'technician_can_wait': True,
    'early_stop': True,
}

exports= {
    'to_excel': True,
    'save_stats': True,
    'diff_stats': True
}

if __name__=="__main__":
    optimizer.run(run_type=run_type, file_inputs= file_inputs, params=params, exports= exports)