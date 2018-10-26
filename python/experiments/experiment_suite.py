import argparse, json, logging
from tqdm import tqdm
import experiment, azure
from configs import config

parser = argparse.ArgumentParser(description='')

parser.add_argument('-id', dest='experiment_suite_id', required=True, help='experiment suite id')
parser.add_argument('-exp', dest='exp', nargs='+', required=True, help='name of experiments to run (option: all)')
parser.add_argument('-vmstart', dest='vmstart',  choices=['initial', 'required'], required=True, , help='start all vm initially or start them when required')

args = parser.parse_args()
experiment_suite_id = args.experiment_suite_id

logging.basicConfig(level=logging.INFO, filename=f'{experiment_suite_id}.log')
log = logging.getLogger('asl')


if 'all' in args.exp:
    exp_ids = ['exp21', 'exp22', 'exp31', 'exp32', 'exp41', 'exp51', 'exp52', 'exp60']
else:
    exp_ids = args.exp

if 'exp51' in exp_ids or 'exp52' in exp_ids:
    # TODO [nku] implement Throughput Maximizing Number of Worker Threads
    raise ValueError(f"Cannot run exp51 or exp52: Throughput Maximizing Number of Worker Threads not Implemented")


configs = {}
max_n_server = 0
max_n_middleware = 0
max_n_client = 0

# check if all specified experiments are available and determine max number of vm's
for exp_id in exp_ids:

    with open(f"./configs/{exp_id}.json") as file:
        configs[exp_id] = json.load(file)

    x = configs[key]['n_server']
    if x > max_n_server:
        max_n_server = x

    x = configs[key]['n_middleware']
    if x > max_n_middleware:
        max_n_middleware = x

    x = configs[key]['n_client']
    if x > max_n_client:
        max_n_client = x


try:
    if args.vmstart == 'initial':
        # if configured start all vm's necessary for the whole experiment suite in the beginning
        azure.start(n_client=max_n_client, n_middleware=max_n_middleware, n_server=max_n_server)

    for exp_id in tqdm(exp_ids, desc="suite"):
        # ensure necessary vm's for this experiment are started
        azure.start(n_client=configs[exp_id]['n_client'],
                    n_middleware=configs[exp_id]['n_middleware']
                    n_server=configs[exp_id]['n_server'])

        # run the experiment on the vm's
        experiment.run(experiment_suite_id=experiment_suite_id, experiment_name=exp_id)
finally:
    # Deallocate all VM's
    azure.deallocate_all()
