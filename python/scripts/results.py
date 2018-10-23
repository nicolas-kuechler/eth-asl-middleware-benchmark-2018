import os, pymongo, json
import utility
from paramiko import SSHClient
from scp import SCPClient


def process(working_dir, info, exp_config, rm_local=False):

    ip = "localhost"
    port = "27017"

    client = pymongo.MongoClient(f"mongodb://{ip}:{port}/")

    #db = client[info['experiment_suite_id']]
    db = client['abc']
    results = db.collection['results']

    result = {
        "exp": info['experiment_name'],
        "exp_config": exp_config,
        "repetition": info['repetition'],
        "client_stats":[],
        "mw_stats":[],
        "ping":[]
    }

    mw_stats = {}

    for file in os.listdir(working_dir):

        file_path = f"{working_dir}/{file}"
        id = os.path.splitext(file)[0]

        if id not in mw_stats:
            mw_stats[id] = {'id':id}

        if id.startswith('client'):
            client_stat = process_client_stats(file_path, id)
            result['client_stats'].append(client_stat)

        elif id.startswith('mw_stat'):
            op_stats, queue_stats = process_mw_stats(file_path)
            mw_stats[id]['ops'] = op_stats
            mw_stats[id]['queue'] = queue_stats

        elif id.startswith('mw'): # general mw log file
            out = process_mw_out(file_path)
            mw_stats[id]['out'] = out

        else:
            raise ValueError(f"Unknown File: {file}")

        if rm_local:
            os.remove(file_path)

    for mw_id in sorted(mw_stats):
        result['mw_stats'].append(mw_stats[mw_id])


    result_id = results.insert_one(result).inserted_id

    return result_id

def process_client_stats(file_path, id):
    with open(file_path) as data:
        d = json.load(data)

    client_stat = {
        "id" : id,
        "sets": d['ALL STATS']['Sets'],
        "gets": d['ALL STATS']['Gets'],
        "totals": d['ALL STATS']['Totals'],
        "set" : d['ALL STATS']['SET'],
        "get": d['ALL STATS']['GET']
    }

    return client_stat


def process_mw_stats(file_path):

    op_stats = []
    queue_stats = []

    with open(file_path) as file:

        header = file.readline()
        header = header.split()[2:] # split header at spaces and exclude  first

        for line in file:
            op = {}
            for i, value in enumerate(line.split()):
                op[header[i]]= value

            if op['type'] == 'queue':
                queue_stats.append(op)
            else:
                op_stats.append(op)

    return op_stats, queue_stats

def process_mw_out(file_path):
    out = []
    with open(file_path) as file:
        for line in file:
            parts = line.split(None, 4)
            log = {
                'time' : parts[0],
                'thread': parts[1],
                'level':parts[2],
                'class':parts[3],
                'msg':parts[4]
            }
            out.append(log)

    return out

def transfer(info, exp_config, host, id, rm_remote=True, rename_mw_logs=False):

    ssh = utility.get_ssh_client(host=host)

    try:
        os.makedirs(info['working_dir']) # create local directories
    except OSError:
        pass

    if rename_mw_logs:
        stdin, stdout, stderr = ssh.exec_command(f"mv ~/{info['working_dir']}/mw_stat.log ~/{info['working_dir']}/mw_stat_0{id}.log")
        utility.format(stdout, stderr)
        stdin, stdout, stderr = ssh.exec_command(f"mv ~/{info['working_dir']}/mw_out.log ~/{info['working_dir']}/mw_out_0{id}.log")
        utility.format(stdout, stderr)


    with SCPClient(ssh.get_transport()) as scp:
        scp.get(info['working_dir'], local_path=info['working_dir'].rsplit('/', 1)[0], recursive=True)

    if rm_remote:
        stdin, stdout, stderr = ssh.exec_command(f"rm -r ~/{info['working_dir']}")
        utility.format(stdout, stderr)

    ssh.close()
