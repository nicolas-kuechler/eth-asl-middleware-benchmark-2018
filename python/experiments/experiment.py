import time, json, logging, math
from tqdm import tqdm
import utility, client_vm, middleware_vm, server_vm, results, network_test, quick_check
from configs import config

log = logging.getLogger('asl')

def run(experiment_suite_id, experiment_name):
    log.info(f"Run Experiment {experiment_name}")
    log.debug(f"  with test time: {config.EXP_TEST_TIME}")

    configurations = utility.get_config(f"./configs/{experiment_name}.json")
    network_test_done = False

    for exp_config in tqdm(configurations, desc=f"  {experiment_name}"):
        log.info("Start New Config")
        log.debug(f"  with exp_config: {exp_config}")

        if (not network_test_done) or exp_config['n_client'] != n_client or exp_config['n_middleware'] != n_middleware or exp_config['n_server'] != n_server:
            network_test_done = True
            n_server = exp_config['n_server']
            n_middleware = exp_config['n_middleware']
            n_client = exp_config['n_client']
            network_stats = network_test.execute_network_test(n_client=n_client, n_mw=n_middleware, n_server=n_server)

        result_ids = []

        for repetition in tqdm(range(exp_config['repetitions']), desc="    rep", leave=False):
            result_id = run_repetition(experiment_suite_id, experiment_name, repetition, exp_config, network_stats)
            result_ids.append(result_id)

        pass_check = quick_check.throughput_check(suite=experiment_suite_id, result_ids=result_ids, threshold=1300)

        if not pass_check: # if throughput std threshold is exceeded, run one more repetition (can be assumed that something went wrong)
            repetition = exp_config['repetitions']
            run_repetition(experiment_suite_id, experiment_name, repetition, exp_config, network_stats)

def run_repetition(experiment_suite_id, experiment_name, repetition, exp_config, network_stats):
    log.info(f"Repetition {repetition}")
    info = {
        "experiment_suite_id" : experiment_suite_id,
        "experiment_name" : experiment_name,
        "repetition" : repetition
    }

    info["working_dir"] = f"/exp_output/{experiment_suite_id}/" + utility.resolve_path(info, exp_config)

    start_experiment(info, exp_config)

    for _ in tqdm(range(int(math.ceil(config.EXP_TEST_TIME/2))), desc="      run", leave=False):
        time.sleep(2)

    time.sleep(0.1)

    stop_experiment(info, exp_config)

    transfer_results(info, exp_config)

    result_id = results.process(config.BASE_DIR + info["working_dir"], info, exp_config, network_stats=network_stats, rm_local=config.EXP_REMOVE_FILES_LOCAL)

    log.info(f"Result: {result_id}")

    return result_id


def start_experiment(info, exp_config):
    log.info("Starting Experiment...")
    log.debug(f"  with info:{info} exp_config:{exp_config}")

    log.debug("Starting Experiment on Servers")
    server_connections = []
    for server_id in range(exp_config['n_server']):
        server_config = {
            'host': config.VM_SERVER[server_id]['host'],
            'ip' :  config.VM_SERVER[server_id]['private_ip'],
            'port' : config.VM_MEMCACHED_PORT
        }

        server_connections.append({"ip":server_config['ip'], "port" : server_config['port']})
        server_vm.start_memcached(info=info, server_id=server_id, server_config=server_config)

    log.debug("Starting Experiment on Middlewares")
    mw_connections = []
    for mw_id in range(exp_config['n_middleware']):
        mw_config = {
            'host': config.VM_MIDDLEWARE[mw_id]['host'],
            'ip': config.VM_MIDDLEWARE[mw_id]['private_ip'],
            'port' : config.VM_MW_PORT,
            'server' : server_connections
        }
        mw_connections.append({"ip":mw_config['ip'], "port" : mw_config['port']})
        middleware_vm.start_middleware(info=info, mw_id=mw_id, mw_config=mw_config, exp_config=exp_config)

    if exp_config['n_middleware'] > 0:
        connections = mw_connections
    else:
        connections = server_connections

    # TODO [nku] optimize timing
    time.sleep(2) # give middleware some time to initialize

    log.debug("Starting Experiment on Clients")
    for client_id in range(exp_config['n_client']):
        client_config = {
                'host': config.VM_CLIENT[client_id]['host'],
                'connections' : connections,
                'test_time': config.EXP_TEST_TIME
        }
        client_vm.start_memtier(info=info, client_id=client_id, client_config=client_config, exp_config=exp_config)

    log.info("Finished Starting Experiment")

def stop_experiment(info, exp_config):
    log.info("Stopping Experiment...")
    log.debug(f"  with info:{info} exp_config:{exp_config}")

    log.debug("Stopping Experiment on Middlewares")
    for mw_id in range(exp_config['n_middleware']):
        middleware_vm.stop_middleware(mw_id=mw_id, host=config.VM_MIDDLEWARE[mw_id]['host'])

    log.debug("Stopping Experiment on Servers")
    for server_id in range(exp_config['n_server']):
        server_vm.stop_memcached(server_id=server_id, host=config.VM_SERVER[server_id]['host'])

    # Clients Finished Through Time Limit Automatically -> don't need to be stopped


def transfer_results(info, exp_config):
    log.info("Transfer Experiment Results...")
    log.debug(f"  with info:{info} exp_config:{exp_config}")
    rm_remote = config.EXP_REMOVE_FILES_VM

    for mw_id in range(exp_config['n_middleware']):
        results.transfer(info=info, exp_config=exp_config, host=config.VM_MIDDLEWARE[mw_id]['host'], id=mw_id, rm_remote=rm_remote, rename_mw_logs=True)

    for client_id in range(exp_config['n_client']):
        results.transfer(info=info, exp_config=exp_config, host=config.VM_CLIENT[client_id]['host'], id=client_id, rm_remote=rm_remote)

    log.info("Finished Transfering Experiment Results")
