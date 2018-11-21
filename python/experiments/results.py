import os, pymongo, json, logging
import utility
from configs import config
from paramiko import SSHClient
from scp import SCPClient
from datetime import datetime

log = logging.getLogger('asl')

def process(working_dir, info, exp_config, network_stats, rm_local=False):

    log.info("Start processing results...")
    log.debug(f"  with working_dir {working_dir}, info {info}, exp_config {exp_config}, rm_local {rm_local}")

    client = pymongo.MongoClient(f"mongodb://{config.MONGODB_IP}:{config.MONGODB_PORT}/")

    db = client[info['experiment_suite_id']]
    results = db.collection['results']

    result = {
        "exp": info['experiment_name'],
        "exp_config": exp_config,
        "repetition": info['repetition'],
        "client_stats":[],
        "mw_stats":[],
        "network_stats": network_stats
    }

    mw_stats = {}

    for file in os.listdir(working_dir):

        file_path = f"{working_dir}/{file}"
        split = os.path.splitext(file)[0].split("_")
        instance_id = f"{split[0]}_{split[-1]}"

        log.debug(f"process file {file_path}")

        if instance_id.startswith('client'):
            client_stat = process_client_stats(file_path, instance_id)
            result['client_stats'].append(client_stat)

        elif instance_id.startswith('mw'):
            if instance_id not in mw_stats:
                mw_stats[instance_id] = {'id':instance_id}

            if '_stat_' in file: # stats mw log file
                mw_stats_1 = process_mw_stats(file_path)
                mw_stats[instance_id] = mw_stats_1

            else: # general mw log file
                out_log = process_mw_out(file_path)
                mw_stats[instance_id]['out'] = out_log
        elif file.startswith('screen'):
            pass
        else:
            raise ValueError(f"Unknown File: {file}")

        if rm_local:
            log.debug("delete result file locally")
            os.remove(file_path)

    for mw_id in sorted(mw_stats):
        result['mw_stats'].append(mw_stats[mw_id])

    result_id = results.insert_one(result).inserted_id

    return result_id

def process_client_stats(file_path, id):
    log.debug(f"process {id} stats file: {file_path}")
    with open(file_path) as data:
        d = json.load(data)

    client_stat = {
        "id" : id,
        "runtime": d['run information']['Seconds'],
        "sets": d['ALL STATS']['Sets'],
        "gets": d['ALL STATS']['Gets'],
        "totals": d['ALL STATS']['Totals'],
        "set" : d['ALL STATS']['SET'],
        "get": d['ALL STATS']['GET']
    }

    return client_stat


def process_mw_stats(file_path):
    log.debug(f"process mw stats file: {file_path}")
    mw_stats = {}

    with open(file_path) as file:
        headers = {}
        for header in file:
            header = header.replace("\n", "")
            if "===" in header: # read headers until break appears
                break
            header = header.split("; ") # split header at delimiter
            header_type = header[2]
            headers[header_type] = header[3:]

            assert(headers[header_type][2] == "stat_type") # assert that type is in the correct position


        for line in file:
            entry = {}
            stat_type = line.split("; ")[2]
            line = line.replace("\n", "")

            for i, value in enumerate(line.split("; ")):
                if value.startswith("{") and value.endswith("}"): # value is a dict of the form {key1=val1, key2=val2, ...}
                    value = value.replace("{", "").replace("}", "")
                    entry_lst = []
                    for pair in value.split(", "):
                        v = pair.split("=")
                        e = {
                            'key' : _parse_value(v[0]),
                            'val': _parse_value(v[1])
                        }
                        entry_lst.append(e)
                    entry[headers[stat_type][i]] = entry_lst
                else:
                    entry[headers[stat_type][i]] = _parse_value(value)

            try:
                mw_stats[stat_type]
            except KeyError:
                mw_stats[stat_type] = []

            mw_stats[stat_type].append(entry)

    return mw_stats

def _parse_value(value):
    try:
        value = int(value) # try casting to int
    except ValueError: # value is no int
        try:
            value = float(value) # try casting to float
        except ValueError: # value is no float
            try:
                value = datetime.strptime(f'01.01.1900-{value}', '%d.%m.%Y-%H:%M:%S.%f') # try transforming to datetime
            except ValueError: # value is no datetime
                pass
    return value


def process_mw_out(file_path):
    log.debug(f"process mw out file: {file_path}")
    out = []
    with open(file_path) as file:
        for line in file:
            parts = line.split(None, 4)
            log_entry = {
                'time' : datetime.strptime(f'01.01.1900-{parts[0]}', '%d.%m.%Y-%H:%M:%S.%f'),
                'thread': parts[1],
                'level':parts[2],
                'class':parts[3],
                'msg':parts[4]
            }
            out.append(log_entry)

    return out

def transfer(info, exp_config, host, id, rm_remote=True, rename_mw_logs=False):
    log.debug("transfer results file")
    ssh = utility.get_ssh_client(host=host)

    try:
        os.makedirs(config.BASE_DIR + info['working_dir']) # create local directories
    except OSError:
        pass

    if rename_mw_logs:
        stdin, stdout, stderr = ssh.exec_command(f"mv ~{info['working_dir']}/mw_stat.log ~/{info['working_dir']}/mw_stat_0{id}.log")
        utility.format(stdout, stderr)
        stdin, stdout, stderr = ssh.exec_command(f"mv ~{info['working_dir']}/mw_out.log ~/{info['working_dir']}/mw_out_0{id}.log")
        utility.format(stdout, stderr)


    local_path = config.BASE_DIR + info['working_dir'].rsplit('/', 1)[0]

    with SCPClient(ssh.get_transport()) as scp:
        scp.get(f"~{info['working_dir']}", local_path=local_path, recursive=True)

    if rm_remote:
        log.debug("delete result file on remote")
        stdin, stdout, stderr = ssh.exec_command(f"rm -r ~{info['working_dir']}")
        utility.format(stdout, stderr)

    ssh.close()

if __name__ == "__main__": process(working_dir="C:/Development/asl-fall18-project/java/dist/out", info={"experiment_suite_id":"process_demo2", "repetition":0, "experiment_name":"demo"}, exp_config=None, rm_local=False)
