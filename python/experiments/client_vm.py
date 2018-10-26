import utility, os, logging
from paramiko import SSHClient
from scp import SCPClient

log = logging.getLogger('asl')

def init(client_id, host):
    return    # do nothing (currently no init necessary)

def start_memtier(info, client_id, client_config, exp_config):
    log.info(f"Starting Memtier Instances on Client: {client_id}...")
    log.debug(f"  with info:{info} client_id:{client_id} client_config:{client_config} exp_config:{exp_config}")

    ssh = utility.get_ssh_client(host=client_config['host'])

    log.debug("creating working directory")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/{info['working_dir']}")
    utility.format(stdout, stderr)

    multikey_arg = "" if exp_config['multi_get_size'] is None else f"--multi-key-get={exp_config['multi_get_size']} "

    for instance_id in range(exp_config['n_instances_mt_per_machine']):
        mt_id = f"client_{client_id}{instance_id}"
        ip = client_config['connections'][instance_id]['ip']
        port = client_config['connections'][instance_id]['port']

        log.info(f"starting memtier instance {mt_id}")
        stdin, stdout, stderr = ssh.exec_command(f"cd ~/{info['working_dir']};\
                                                screen -dmS {mt_id} \
                                                    memtier_benchmark \
                                                        --threads={exp_config['n_threads_per_mt_instance']} \
                                                        --clients={exp_config['n_vc']} \
                                                        --ratio={exp_config['workload_ratio']} \
                                                        --server={ip} \
                                                        --port={port} \
                                                        {multikey_arg}\
                                                        --json-out-file={mt_id}.log \
                                                        --test-time={client_config['test_time']} \
                                                        --protocol=memcache_text \
                                                        --key-maximum=10000 \
                                                        --data-size=4096 \
                                                        --expiry-range=9999-10000")
        utility.format(stdout, stderr)

    ssh.close()

    log.info(f"Finished Starting Memtier Instances on Client: {client_id}")
