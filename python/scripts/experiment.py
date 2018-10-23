import time, json
import utility, client_vm, middleware_vm, server_vm, results

TEST_TIME = 80 # sec

def run(experiment_suite_id, experiment_name):

    configurations = utility.get_config(f"./experiments/{experiment_name}.json")

    with open("./../vm_config.json") as file:
        vm_config = json.load(file)

    for exp_config in configurations:
        print("Start New Config")
        for repetition in range(exp_config['repetitions']):
            info = {
                "experiment_suite_id" : experiment_suite_id,
                "experiment_name" : experiment_name,
                "repetition" : repetition
            }

            info["working_dir"] = utility.resolve_path(info, exp_config)

            start_experiment(info, exp_config, vm_config)
            time.sleep(TEST_TIME + 0.5)
            stop_experiment(info, exp_config, vm_config)

            transfer_results(info, exp_config, vm_config)

            result_id = results.process(info["working_dir"], info, exp_config, rm_local=False)
            print(result_id)

def start_experiment(info, exp_config, vm_config):
    server_connections = []
    for server_id in range(exp_config['n_server']):
        server_config = {
            'host': vm_config["server"][server_id]['host'],
            'ip' :  vm_config["server"][server_id]['private_ip'],
            'port' : 11211, # TODO [nku] also load from vm config?
        }

        server_connections.append({"ip":server_config['ip'], "port" : server_config['port']})
        server_vm.start_memcached(info=info, server_id=server_id, server_config=server_config)

    mw_connections = []
    for mw_id in range(exp_config['n_middleware']):
        mw_config = {
            'host': vm_config["middleware"][mw_id]['host'],
            'ip': vm_config["middleware"][mw_id]['private_ip'],
            'port' : 6379, # TODO [nku] also load from vm config?
            'server' : server_connections
        }
        mw_connections.append({"ip":mw_config['ip'], "port" : mw_config['port']})
        middleware_vm.start_middleware(info=info, mw_id=mw_id, mw_config=mw_config, exp_config=exp_config)

    if exp_config['n_middleware'] > 0:
        connections = mw_connections
    else:
        connections = server_connections

    for client_id in range(exp_config['n_client']):
        client_config = {
                'host': vm_config["client"][client_id]['host'],
                'connections' : connections,
                'test_time': TEST_TIME
        }
        client_vm.start_memtier(info=info, client_id=client_id, client_config=client_config, exp_config=exp_config)

def stop_experiment(info, exp_config, vm_config):

    for mw_id in range(exp_config['n_middleware']):
        middleware_vm.stop_middleware(mw_id=mw_id, host=vm_config["middleware"][mw_id]['host'])

    for server_id in range(exp_config['n_server']):
        server_vm.stop_memcached(server_id=server_id, host=vm_config["server"][server_id]['host'])

    # Clients Finished Through Time Limit Automatically -> don't need to be stopped


def transfer_results(info, exp_config, vm_config):
        for mw_id in range(exp_config['n_middleware']):
            results.transfer(info=info, exp_config=exp_config, host=vm_config["middleware"][mw_id]['host'], id=mw_id, rm_remote=True, rename_mw_logs=True)

        for client_id in range(exp_config['n_client']):
            results.transfer(info=info, exp_config=exp_config, host=vm_config["client"][client_id]['host'], id=client_id, rm_remote=True)

if __name__ == "__main__":
    run()
