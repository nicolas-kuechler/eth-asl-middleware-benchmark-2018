import utility

"""
Example Config:
config = {
    'host': vm["client"][0]['host'],
    'server' : 'localhost',
    'port' : 11211,
    'n_threads_per_mt_instance' : 2,
    'n_vc':1,
    'workload_ratio': '1:1', # Set:Get ratio [read_only, write_only]
    'multi_get_size': None # 1
}
"""


def start(experiment_name, client_id, config):
    print(f"Starting Client {client_id} in Experiment {experiment_name}...")
    ssh = utility.get_ssh_client(host=config['host'])

    print("  creating experiment directory...")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/experiments/{experiment_name}/{client_id}/")
    utility.format(stdout, stderr)

    print(f"  starting client in a detached screen window with id: {client_id}...")


    multikey_arg = "" if config['multi_get_size'] is None else f"--multi-key-get={config['multi_get_size']} "

    stdin, stdout, stderr = ssh.exec_command(f"cd ~/experiments/{experiment_name}/{client_id};\
                                                            screen -dmS {client_id} \
                                                             memtier_benchmark \
                                                                --threads={config['n_threads_per_mt_instance']} \
                                                                --clients={config['n_vc']} \
                                                                --ratio={config['workload_ratio']} \
                                                                --server={config['server']} \
                                                                --port={config['port']} \
                                                                {multikey_arg}\
                                                                --json-out-file={client_id}.log \
                                                                --protocol=memcache_text \
                                                                --key-maximum=10000 \
                                                                --data-size=4096 \
                                                                --expiry-range=9999-10000")
    utility.format(stdout, stderr)
    format_stdout(stderr)

    print(f"  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print("  closing ssh client...")
    ssh.close()

    print("Finished Starting Client")

def stop(experiment_name, client_id, config):
    print(f"Stopping Client {client_id} in Experiment {experiment_name}...")
    ssh = utility.get_ssh_client(host=config['host'])

    print("  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print(f"  stopping client {client_id}...")
    stdin, stdout, stderr = ssh.exec_command(f"screen -S {client_id} -X quit")
    utility.format(stdout, stderr)

    print("  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print("  closing ssh client...")
    ssh.close()

    print("Finished Stopping Client")
