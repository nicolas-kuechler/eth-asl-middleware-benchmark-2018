import json, paramiko, time, re, logging
from tqdm import tqdm

import utility
from configs import config

log = logging.getLogger('asl')

def execute_network_test(n_client, n_mw, n_server):
    log.info(f"Execute Network Test with Topology: {n_client} clients, {n_mw} mws, {n_server} servers")

    d_ping = execute_ping_test(n_client, n_mw, n_server)
    log.debug(f"d_ping: {d_ping}")
    bw_results = execute_bandwidth_test(n_client, n_mw, n_server)
    log.debug(f"bw_results: {bw_results}")
    results = []
    for bw_res in  bw_results:
        rtt = d_ping[bw_res['from']][bw_res['to']]["avg_rtt"]
        bw_res['rtt'] = rtt
        results.append(bw_res)
    return results

def execute_ping_test(n_client, n_mw, n_server):
    log.info(f"Execute Ping Test")

    clients = config.VM_CLIENT
    servers = config.VM_SERVER
    mws = config.VM_MIDDLEWARE

    d = {}

    if n_mw > 0:

        for client_id in tqdm(range(n_client), desc="client ping", leave=False):
            log.debug(f" client: {client_id}")
            host = clients[client_id]['host']
            mw_pings = _ping_test(host=host, connections=mws[0:n_mw])
            d[clients[client_id]['name']] = mw_pings

        for mw_id in tqdm(range(n_mw), desc="mw ping", leave=False):
            log.debug(f" mw: {mw_id}")
            host = mws[mw_id]['host']
            client_pings = _ping_test(host=host, connections=clients[0:n_client])
            server_pings = _ping_test(host=host, connections=servers[0:n_server])
            d[mws[mw_id]['name']] =  {**client_pings, **server_pings}

        for server_id in tqdm(range(n_server), desc="server ping", leave=False):
            log.debug(f" server: {server_id}")
            host = servers[server_id]['host']
            mw_pings = _ping_test(host=host, connections=mws[0:n_mw])
            d[servers[server_id]['name']] =  mw_pings

    else: # no middleware

        for client_id in tqdm(range(n_client), desc="client ping", leave=False):
            log.debug(f" client: {client_id}")
            host = clients[client_id]['host']
            server_pings = _ping_test(host=host, connections=servers[0:n_server])
            d[clients[client_id]['name']] = server_pings

        for server_id in tqdm(range(n_server), desc="server ping", leave=False):
            log.debug(f" server: {server_id}")
            host = servers[server_id]['host']
            client_pings = _ping_test(host=host, connections=clients[0:n_client])
            d[servers[server_id]['name']] =  client_pings

    return d



def execute_bandwidth_test(n_client, n_mw, n_server):
    log.info(f"Execute Bandwidth Test")
    clients = config.VM_CLIENT
    servers = config.VM_SERVER
    mws = config.VM_MIDDLEWARE

    results = []

    if n_mw > 0:
        with tqdm(total=4, desc="bw stage", leave=False) as pbar:
            # Stage 1: Clients -> MWs
            log.debug(f" Stage 1: Clients -> MW's")
            stage1 = _bandwidth_stage_test(iperf_clients=clients[0:n_client], iperf_servers=mws[0:n_mw])
            results += stage1
            pbar.update(1)

            # Stage 2: MWs -> Clients
            log.debug(f" Stage 2: MW's -> Clients")
            stage2 = _bandwidth_stage_test(iperf_clients=mws[0:n_mw], iperf_servers=clients[0:n_client])
            results += stage2
            pbar.update(1)

            # Stage 3: MW -> Server
            log.debug(f" Stage 3: MW's -> Servers")
            stage3 = _bandwidth_stage_test(iperf_clients=mws[0:n_mw], iperf_servers=servers[0:n_server])
            results += stage3
            pbar.update(1)

            # Stage 4: Server -> MW
            log.debug(f" Stage 4: Server -> MW's")
            stage4 = _bandwidth_stage_test(iperf_clients=servers[0:n_server], iperf_servers=mws[0:n_mw])
            results += stage4
            pbar.update(1)

    else: # without middlewares
        with tqdm(total=2, desc="bw stage",leave=False) as pbar:
            # Stage 1: Clients -> Servers
            log.debug(f" Stage 1: Clients -> Servers")
            stage1 = _bandwidth_stage_test(iperf_clients=clients[0:n_client], iperf_servers=servers[0:n_server])
            results += stage1
            pbar.update(1)

            # Stage 2: Servers -> Clients
            log.debug(f" Stage 2: Servers -> Clients")
            stage2 = _bandwidth_stage_test(iperf_clients=servers[0:n_server], iperf_servers=clients[0:n_client])
            results += stage2
            pbar.update(1)

    return results


def _ping_test(host, connections, ping_rep = 20):

    ssh = utility.get_ssh_client(host=host)

    ping_data = {}

    for con in connections:
        log.debug(f"Ping: {host} -> {con['host']}")
        stdin, stdout, stderr = ssh.exec_command(f"ping -c {ping_rep} {con['private_ip']}")

        summary = stdout.readlines()[-1]
        avg_rtt = summary.split("/")[4]

        ping_data[con['name']]= {"avg_rtt": float(avg_rtt)}

    return ping_data


def _bandwidth_stage_test(iperf_clients, iperf_servers, report_duration=20 ,report_interval=5):

    n_iperf_client = len(iperf_clients)
    n_iperf_server = len(iperf_servers)

    # build ssh connections to all vm's
    ssh = {
        "client":[],
        "server":[]
    }

    for iperf_client in iperf_clients:
        ssh_con = utility.get_ssh_client(host=iperf_client['host'])
        ssh['client'].append(ssh_con)

    for iperf_server in iperf_servers:
        ssh_con = utility.get_ssh_client(host=iperf_server['host'])
        ssh['server'].append(ssh_con)


    # start iperf server side
    log.debug(f"start iperf server side")
    for s in range(n_iperf_server):
        cmd = f"screen -dmS bw_test iperf -s -t {report_duration + report_interval}"
        log.debug(f"cmd: {cmd}")
        stdin, stdout, stderr = ssh['server'][s].exec_command(cmd)
        utility.format(stdout, stderr)

    # start iperf client side to each iperf server
    log.debug(f"start iperf client side")
    for c in range(n_iperf_client):
        for s in range(n_iperf_server):
            log_file = f"{iperf_clients[c]['name']}_{iperf_servers[s]['name']}"
            log.debug(f"removing old tmp log files")
            stdin, stdout, stderr = ssh['client'][c].exec_command(f"rm -r tmp{s+1}")
            utility.format(stdout, stderr)
            cmd = f"mkdir tmp{s+1};cd tmp{s+1};screen -dmS bw_test -L iperf -c {iperf_servers[s]['private_ip']} -t {report_duration} -i {report_interval}"
            log.debug(f"cmd: {cmd}")
            stdin, stdout, stderr = ssh['client'][c].exec_command(cmd)
            utility.format(stdout, stderr)

    time.sleep(report_duration+report_interval)

    # process results
    log.debug(f"processing iperf results")
    results = []
    for c in range(n_iperf_client):
        for s in range(n_iperf_server):
            log_file = f"tmp{s+1}/screenlog.0"
            log.debug(f"  iperf: c{c} s{s}")
            sftp_client = ssh['client'][c].open_sftp()
            remote_file = sftp_client.open(log_file)
            try:
                avg_bandwidth = -1
                lines = []
                bws = []
                for line in remote_file:
                    lines.append(line)
                    # parse interval
                    objInterval = re.search("(\d+\.?\d*)- (\d+\.?\d*) sec", str(line))
                    if objInterval is None:
                        objInterval = re.search("(\d+\.?\d*)-(\d+\.?\d*) sec", str(line))

                    # parse bandwidth
                    objBandwidth = re.search("(\d+\.?\d*) Mbits/sec", str(line))

                    if objBandwidth is not None:
                        bandwidth = objBandwidth.group(1)
                        interval_start = objInterval.group(1)
                        interval_end = objInterval.group(2)

                        if float(interval_start) > 0 and float(interval_end) < report_duration:
                            bws.append(float(bandwidth)) # don't use warm up and cooldown
                if len(bws) > 0:
                    avg_bandwidth = sum(bws)/len(bws)

                    res = {
                        "from": iperf_clients[c]['name'],
                        "to": iperf_servers[s]['name'],
                        "bandwidth": avg_bandwidth
                    }

                    results.append(res)
                else:
                    log.warning(f"no bandwidths found")
                    log.warning(f"lines: {lines}")


            finally:
                remote_file.close()
                # remove log files
                log.debug(f"remove remote screen log files")
                stdin, stdout, stderr = ssh['client'][c].exec_command(f"rm -r tmp{s+1}")


    # ensure all bw screen sessions are closed
    for c in range(n_iperf_client):
        cmd = f"screen -S bw_test -X quit"
        log.debug(f"cmd: {cmd}")
        stdin, stdout, stderr = ssh['client'][c].exec_command(cmd)

    for s in range(n_iperf_server):
        cmd = f"screen -S bw_test -X quit"
        log.debug(f"cmd: {cmd}")
        stdin, stdout, stderr = ssh['server'][s].exec_command(cmd)


    # close all ssh connections
    for key, val in ssh.items():
        for connection in val:
            connection.close()

    return results

if __name__ == "__main__":
    result = execute_network_test(n_client=3, n_mw=2, n_server=3)
    print(result)
