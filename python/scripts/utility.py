import json, itertools, paramiko


def get_config(path:str):
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
    # TODO [nku] move to config file?
    username = 'kunicola'
    key_filename= 'C:/Users/nicok/.ssh/asl_new/asl-private-openssh.ppk'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, key_filename=key_filename)
    return ssh

def format(stdout, stderr):
    for line in iter(stderr.readline, ""):
        print(f"\t{line}", end='')
    for line in iter(stdout.readline, ""):
        print(f"\t{line}", end='')
