import utility

"""
Example Config:

config = {
    'host': vm["server"][0]['host'],
    'ip' : 'localhost',
    'port' : 11211,
}
"""

def start(experiment_name, server_id, config):
    print(f"Starting Server {server_id} in Experiment {experiment_name}...")
    ssh = utility.get_ssh_client(host=config['host'])

    print("  retrieving code from master...")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project pull origin master")
    utility.format(stdout, stderr)

    print("  git commit id...")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project rev-parse HEAD")
    utility.format(stdout, stderr)

    print("  starting memcached...")
    stdin, stdout, stderr = ssh.exec_command(f"screen -dmS {server_id} memcached -l {config['ip']} -p {config['port']}")
    utility.format(stdout, stderr)

    print("  initializing memcached...")
    stdin, stdout, stderr = ssh.exec_command(f"python3.6 asl-fall18-project/python/scripts/init_memcached.py -ip {config['ip']} -port {config['port']}")
    utility.format(stdout, stderr)

    print(f"  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print("  closing ssh client...")
    ssh.close()

    print("Finished Starting Server")

def stop(experiment_name, server_id, config):
    print(f"Stopping Server {server_id} in Experiment {experiment_name}...")
    ssh = utility.get_ssh_client(host=config['host'])

    print("  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print(f"  stopping server {server_id}...")
    stdin, stdout, stderr = ssh.exec_command(f"screen -S {server_id} -X quit")
    utility.format(stdout, stderr)

    print("  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print("  closing ssh client...")
    ssh.close()

    print("Finished Stopping Server")
