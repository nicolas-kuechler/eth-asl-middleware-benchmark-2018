import utility, logging

log = logging.getLogger('asl')

def init(mw_id, host):
    log.info(f"Initializing Middleware {mw_id}...")
    ssh = utility.get_ssh_client(host=host)

    log.info("cleaning with ant")
    stdin, stdout, stderr = ssh.exec_command("ant clean -buildfile ~/asl-fall18-project/java")
    utility.format(stdout, stderr)

    log.info("retrieving code from master")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project pull origin master")
    utility.format(stdout, stderr)

    log.info("building with ant")
    stdin, stdout, stderr = ssh.exec_command("ant -buildfile ~/asl-fall18-project/java")
    utility.format(stdout, stderr)

    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project rev-parse HEAD")
    commit_id = stdout.read()
    log.info(f"commit_id: {commit_id}")

    ssh.close()
    log.info(f"Finished Initializing Middleware {mw_id}")

    return commit_id


def start_middleware(info, mw_id, mw_config, exp_config):
    log.info(f"Starting Middleware {mw_id}...")
    log.debug(f"  with info:{info} mw_id:{mw_id} mw_config:{mw_config} exp_config:{exp_config}")

    ssh = utility.get_ssh_client(host=mw_config['host'])

    log.debug("creating working directory")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/{info['working_dir']}")
    utility.format(stdout, stderr)

    log.debug(f"starting middleware in a detached screen window with id {mw_id}")
    is_sharded = True if exp_config['multi_get_behaviour'] == 'sharded' else False
    connection_str = " ".join(list(map(lambda connection: f"{connection['ip']}:{connection['port']}", mw_config['server'])))

    stdin, stdout, stderr = ssh.exec_command(f"cd ~/{info['working_dir']};\
                                                            screen -dmS mw_0{mw_id} -L \
                                                             java -jar ~/asl-fall18-project/java/dist/middleware-kunicola.jar \
                                                                -l {mw_config['ip']} \
                                                                -p {mw_config['port']} \
                                                                -t {exp_config['n_worker_per_mw']} \
                                                                -s {is_sharded} \
                                                                -m {connection_str}")
    utility.format(stdout, stderr)
    ssh.close()

    log.info(f"Finished Starting Middleware {mw_id}")

def stop_middleware(mw_id, host):
    log.info(f"Stopping Middleware {mw_id}...")
    log.debug(f"  with host:{host}")

    ssh = utility.get_ssh_client(host=host)

    stdin, stdout, stderr = ssh.exec_command(f"screen -S mw_0{mw_id} -X quit")
    utility.format(stdout, stderr)

    ssh.close()

    log.info(f"Finished Stopping Middleware {mw_id}")
