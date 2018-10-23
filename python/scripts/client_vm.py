import utility, os
from paramiko import SSHClient
from scp import SCPClient


def start_memtier(info, client_id, client_config, exp_config):

    print(f"Starting Client: {client_id}...")
    ssh = utility.get_ssh_client(host=client_config['host'])

    print("  creating working directory...")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/{info['working_dir']}")
    utility.format(stdout, stderr)

    multikey_arg = "" if exp_config['multi_get_size'] is None else f"--multi-key-get={exp_config['multi_get_size']} "

    for instance_id in range(exp_config['n_instances_mt_per_machine']):
        mt_id = f"client_{client_id}{instance_id}"
        ip = client_config['connections'][instance_id]['ip']
        port = client_config['connections'][instance_id]['port']

        print(f"  starting memtier instance {mt_id}...")
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

    print(f"Finished Starting Client: {client_id}...")


def start_vm():
    # TODO [nku] implement client vm starting
    print("NOT IMPLEMENTED YET")

def stop_vm():
    # TODO [nku] implement client vm stop
    print("NOT IMPLEMENTED YET")
