import json, itertools, paramiko, logging
from string import Template
from configs import config

log = logging.getLogger('asl')

def get_config(path:str):

    log.debug(f"building product of configurations: {path}")

    # open file
    with open(path) as file:
        config = json.load(file)

    # transform values to singleton list
    for key, value in config.items():
        if not isinstance(value, list):
            config[key] = [value]

    # build tuple (to avoid cross product for these keys)
    config['tmp'] = list(zip(config['n_middleware'], config['n_instances_mt_per_machine'], config['n_threads_per_mt_instance']))
    del config['n_middleware']
    del config['n_instances_mt_per_machine']
    del config['n_threads_per_mt_instance']

    # build cross product and transform back
    for c in (dict(zip(config, x)) for x in itertools.product(*config.values())):
        c['n_middleware'] = c['tmp'][0]
        c['n_instances_mt_per_machine'] = c['tmp'][1]
        c['n_threads_per_mt_instance'] = c['tmp'][2]
        del c['tmp']
        yield(c)


def get_ssh_client(host):
    log.debug(f"get ssh client host={host}, username={config.SSH_USERNAME}, key_file={config.SSH_PRIVATE_KEY_FILE}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=config.SSH_USERNAME, key_filename=config.SSH_PRIVATE_KEY_FILE)
    return ssh

def format(stdout, stderr):
    for line in iter(stderr.readline, ""):
        log.error(f"\t{line}")
    for line in iter(stdout.readline, ""):
        log.debug(f"\t{line}")



def resolve_path(info, exp_config):
    translations = {
        "1:0": "write_only",
        "0:1": "read_only",
        "1:1": "read_write"
    }

    return Template(exp_config['path_template']).substitute(experiment_suite_id = info['experiment_suite_id'],
                                    experiment_name = info['experiment_name'],
                                    repetition = info['repetition'],
                                    n_server = exp_config['n_server'],
                                    n_client = exp_config['n_client'],
                                    n_instances_mt_per_machine  = exp_config['n_instances_mt_per_machine'],
                                    n_threads_per_mt_instance = exp_config['n_threads_per_mt_instance'],
                                    n_vc=exp_config['n_vc'],
                                    workload_ratio = translations.get(exp_config['workload_ratio'], exp_config['workload_ratio']),
                                    multi_get_behaviour = exp_config['multi_get_behaviour'],
                                    multi_get_size = exp_config['multi_get_size'],
                                    n_middleware = exp_config['n_middleware'],
                                    n_worker_per_mw = exp_config['n_worker_per_mw'])

def list_screen_windows(host):
    ssh = utility.get_ssh_client(host=host)
    log.debug("screen windows: ")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)
    ssh.close()