import utility

"""
Example Config:

config = {
    'host': vm["middleware"][0]['host'],
    'ip': vm["middleware"][0]['private_ip'],
    'port' : 6379,
    'n_worker_per_mw' : 10,
    'multi_get_behaviour' : 'non-sharded',
    'server' : ['localhost:11211',  'localhost:11212', 'localhost:11213']
}
"""
# TODO [nku] consider having init() and start() (don't want to build everytime new)
def start(experiment_name, mw_id, config):
    print(f"Starting Middleware {mw_id} in Experiment {experiment_name}...")
    ssh = utility.get_ssh_client(host=config['host'])

    print("  cleaning with ant...")
    stdin, stdout, stderr = ssh.exec_command("ant clean -buildfile ~/asl-fall18-project/java")
    utility.format(stdout, stderr)

    print("  retrieving code from master...")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project pull origin master")
    utility.format(stdout, stderr)

    print("  git commit id...")
    stdin, stdout, stderr = ssh.exec_command("git -C ~/asl-fall18-project rev-parse HEAD")
    utility.format(stdout, stderr)

    print("  building with ant...")
    stdin, stdout, stderr = ssh.exec_command("ant -buildfile ~/asl-fall18-project/java")
    utility.format(stdout, stderr)

    print("  creating experiment directory...")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/experiments/{experiment_name}/{mw_id}")
    utility.format(stdout, stderr)

    print(f"  starting middleware in a detached screen window with id: {mw_id}...")
    is_sharded = True if config['multi_get_behaviour'] == 'sharded' else False
    stdin, stdout, stderr = ssh.exec_command(f"cd ~/experiments/{experiment_name}/{mw_id};\
                                                            screen -dmS {mw_id} \
                                                             java -jar ~/asl-fall18-project/java/dist/middleware-kunicola.jar \
                                                                -l {config['ip']} \
                                                                -p {config['port']} \
                                                                -t {config['n_worker_per_mw']} \
                                                                -s {is_sharded} \
                                                                -m {' '.join(config['server'])}")
    utility.format(stdout, stderr)

    print(f"  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print("  closing ssh client...")
    ssh.close()

    print("Finished Starting Middleware")

def stop(experiment_name, mw_id, config):
    print(f"Stopping Middleware {mw_id} in Experiment {experiment_name}...")
    ssh = utility.get_ssh_client(host=config['host'])

    print("  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print(f"  stopping middleware {mw_id}...")
    stdin, stdout, stderr = ssh.exec_command(f"screen -S {mw_id} -X quit")
    utility.format(stdout, stderr)

    print("  listing screen windows...")
    stdin, stdout, stderr = ssh.exec_command("screen -list")
    utility.format(stdout, stderr)

    print("  closing ssh client...")
    ssh.close()

    print("Finished Stopping Middleware")
