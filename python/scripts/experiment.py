import utility, client, midleware, server
import time

def run_experiment():
    experiment_name = "exp21"
    configurations = utility.get_config("./experiments/exp21.json")

    vm = None # TODO [nku] load vm config

    for config in configurations:
        print("Start New Config")
        for repetition in range(config['repetitions']):
            print(f"\nRepetition: {repetition}")
            start_experiment(experiment_name, config, vm)
            time.sleep(1) # TODO [nku] figure out a way on what to wait
            stop_experiment(experiment_name, config, vm)
            print(f"End Repetition: {repetition}\n")

def start_experiment(experiment_name, config, vm):
    server_connections = []
    for server in range(config['n_server']):
        server_config = {
            'host': vm["server"][server]['host'],
            'ip' :  vm["server"][server]['private_ip'],
            'port' : 11211, # TODO [nku] also load from vm config?
        }
        server_connections.append(f"{server_config['ip']}:{server_config['port']}")
        server.start(experiment_name=experiment_name, server_id=server, config=server_config)

    mw_connections = []
    for mw in range(config['n_middleware']):
        mw_config = {
            'host': vm["middleware"][mw]['host'],
            'ip': vm["middleware"][mw]['private_ip'],
            'port' : 6379, # TODO [nku] also load from vm config?
            'n_worker_per_mw' : config['n_worker_per_mw'],
            'multi_get_behaviour' : config['multi_get_behaviour'],
            'server' : server_connections
        }
        mw_connections.append(f"{mw_config['ip']}:{mw_config['port']}")
        middleware.start(experiment_name=experiment_name, mw_id=mw, config=mw_config)

    if config['n_middleware'] > 0:
        # TODO [nku] define criteria to what the clients should connect
        connections = [] #list of dicts [{'ip':'localhost', 'port':1234}]
    else:
        connections = []

    for client in range(config['n_client']):
        for instance in range(config['n_instances_mt_per_machine']):
            client_config = {
                'host': vm["client"][client]['host'],
                'server' : connections[instance]['ip'],
                'port' : connections[instance]['port'],
                'n_threads_per_mt_instance' : config['n_threads_per_mt_instance'],
                'n_vc': config['n_vc'],
                'workload_ratio': config['workload_ratio'],
                'multi_get_size': config['multi_get_size']
            }
            start(experiment_name=experiment_name, client_id=client, config=client_config)
            print(f"start instance {instance} on client {client}")

def stop_experiment(config):
    for server in range(config['n_server']):
        print(f"stop server {server}")

    for mw in range(config['n_middleware']):
        print(f"stop mw {mw} and transfer results")

    for client in range(config['n_client']):
        for instance in range(config['n_instances_mt_per_machine']):
            print(f"stop instance {instance} on client {client} and transfer results")

if __name__ == "__main__":
    run_experiment()
