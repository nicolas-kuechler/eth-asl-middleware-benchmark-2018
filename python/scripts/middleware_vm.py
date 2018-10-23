import utility


# TODO [nku] init middlewares somewhere
def init(mw_id, host):
    print(f"Initializing Middleware {mw_id}...")
    ssh = utility.get_ssh_client(host=host)

    print("  cleaning with ant...")
    stdin, stdout, stderr = ssh.exec_command("ant clean -buildfile ~/asl-fall18-project/java")
    utility.format(stdout, stderr)

    print("  retrieving code from master...")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project pull origin master")
    utility.format(stdout, stderr)

    print("  building with ant...")
    stdin, stdout, stderr = ssh.exec_command("ant -buildfile ~/asl-fall18-project/java")
    utility.format(stdout, stderr)

    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project rev-parse HEAD")
    commit_id = stdout.read()

    ssh.close()
    print(f"Finished Initializing Middleware {mw_id}")

    return commit_id


def start_middleware(info, mw_id, mw_config, exp_config):
    print(f"Starting Middleware {mw_id}...")
    ssh = utility.get_ssh_client(host=mw_config['host'])

    print("  creating working directory...")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/{info['working_dir']}")
    utility.format(stdout, stderr)

    print(f"  starting middleware in a detached screen window with id {mw_id}...")
    is_sharded = True if exp_config['multi_get_behaviour'] == 'sharded' else False
    connection_str = " ".join(list(map(lambda connection: f"{connection['ip']}:{connection['port']}", mw_config['server'])))

    stdin, stdout, stderr = ssh.exec_command(f"cd ~/{info['working_dir']};\
                                                            screen -dmS mw_0{mw_id} \
                                                             java -jar ~/asl-fall18-project/java/dist/middleware-kunicola.jar \
                                                                -l {mw_config['ip']} \
                                                                -p {mw_config['port']} \
                                                                -t {exp_config['n_worker_per_mw']} \
                                                                -s {is_sharded} \
                                                                -m {connection_str}")
    utility.format(stdout, stderr)
    ssh.close()

    print(f"Finished Starting Middleware {mw_id}")

def stop_middleware(mw_id, host):
    print(f"Stopping Middleware {mw_id}...")
    ssh = utility.get_ssh_client(host=host)

    stdin, stdout, stderr = ssh.exec_command(f"screen -S mw_0{mw_id} -X quit")
    utility.format(stdout, stderr)

    ssh.close()

    print(f"Finished Stopping Middleware {mw_id}")

def transfer_results(info, exp_config, host, rm_remote=True):
    # TODO [nku] implement mw transfer results
    print("NOT IMPLEMENTED YET")

def start_vm():
    # TODO [nku] implement mw starting
    print("NOT IMPLEMENTED YET")
    init()

def stop_vm():
    # TODO [nku] implement mw vm stop
    print("NOT IMPLEMENTED YET")
