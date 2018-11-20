import utility, logging

log = logging.getLogger('asl')

def init(server_id, host):
    log.info(f"Initializing Server {server_id}...")
    ssh = utility.get_ssh_client(host=host)

    log.info("retrieving code from master")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project pull origin master")
    utility.format(stdout, stderr)

    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project rev-parse HEAD")
    commit_id = stdout.read()
    log.info(f"commit_id: {commit_id}")

    ssh.close()
    log.info(f"Finished Initializing Server {server_id}")

    return commit_id


def start_memcached(info, server_id, server_config):
    log.info(f"Starting Memcached Server {server_id}...")
    log.debug(f"  with info:{info} server_config:{server_config}")

    ssh = utility.get_ssh_client(host=server_config['host'])

    stdin, stdout, stderr = ssh.exec_command(f"screen -dmS server_0{server_id} memcached -l {server_config['ip']} -p {server_config['port']} -t 1")
    utility.format(stdout, stderr)

    log.info("initializing memcached")
    stdin, stdout, stderr = ssh.exec_command(f"python3.6 asl-fall18-project/python/experiments/scripts/init_memcached.py -ip {server_config['ip']} -port {server_config['port']}")
    utility.format(stdout, stderr)

    ssh.close()

    log.info(f"Finished Starting and Initializing Memcached Server {server_id}")

def stop_memcached(server_id, host):
    log.info(f"Stopping Memcached Server {server_id}...")
    log.debug(f"  with host:{host}")
    ssh = utility.get_ssh_client(host=host)

    stdin, stdout, stderr = ssh.exec_command(f"screen -S server_0{server_id} -X quit")
    utility.format(stdout, stderr)

    ssh.close()

    log.info(f"Finished Stopping Memcached Server {server_id}")
