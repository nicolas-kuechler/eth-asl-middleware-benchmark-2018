use_interactive_law_rtt_adjustment = False
use_interactive_law_in_mw = False

markersize = 6
capsize = 5
linewidth=1.5

min_slot_inclusive = 3
max_slot_inclusive = 14
cov_threshold = 0.05

figsize = {
    2: (3.54,1.69),
    3: (3*2.36,3*0.98)
}


# from http://colorbrewer2.org
seq_colors = ['#a1dab4', '#41b6c4', '#2c7fb8', '#253494']



network_throughput_limit_color = "black"
network_throughput_limit_linestyle = "--"

color = {
    "single_color":seq_colors[3],
    "single_color_interactive_law": seq_colors[2],
    "network_throughput_limit": "grey",
    "hist_error": "grey",
    "hist": seq_colors[1]
}

rt_component_color = {
    "network": "#01295f", #"#bfd2bf", #"#f5ee9e",
    "ntt": "#437f97", #"#646f4b", #"#2d728f",
    "qwt": "#849324", #"#46351d", #"#3b8ea5",
    "wtt": "#ffb30f",#"#839d9a", #"#f49e4c",
    "sst": "#fd151b", #"#7bb2d9"#"#ab3428"
}

sst_color = {
    "sst0": "#fb6a4a",
    "sst1": "#de2d26",
    "sst2": "#a50f15",
}

sst_label = {
    "sst0": "server 1",
    "sst1": "server 2",
    "sst2": "server 3",
}

rt_component_label = {
    "network": "network mw-client",
    "ntt": "net-thread decoding",
    "qwt": "queue waiting time",
    "wtt": "worker-thread processing",
    "sst": "server service time"
}


axis_label = {
    "number_of_clients": "Number of Clients",
    "throughput": "Throughput [req/sec]",
    "rt": "Response Time [ms]",
    "mget_size": "Multi Get Size",
    "freq": "Frequency",
    "slot": "Slot",
    "queue_size": "Number of Requests in Queue",
    "sst":"Server Service Time [ms]",
    "n_worker": "Number of Worker-Threads"
}

label = {
    "interactive_law": "interactive law",
    "measurement": "measurement",
    "network_throughput_limit": "bandwidth limit"
}

queueing_color = {
    "meas" : '#a1dab4',
    "mm1": '#41b6c4',
    "mmm": '#2c7fb8'
}

queueing_label = {
    "meas" : "measured",
    "mm1":  "M/M/1",
    "mmm": "M/M/m"
}

n_worker_color = {
    8:  seq_colors[0],
    16: seq_colors[1],
    32: seq_colors[2],
    64: seq_colors[3],
}


n_worker_label = {
    8:  "  8 worker-threads",
    16: "16 worker-threads",
    32: "32 worker-threads",
    64: "64 worker-threads",
}

n_worker_label_short = {
    8:  "  8 worker-threads",
    16: "16 worker-threads",
    32: "32 worker-threads",
    64: "64 worker-threads",
}

n_worker_inter_label = {
    8:  "  8 worker threads interactive law",
    16: "16 worker threads interactive law",
    32: "32 worker threads interactive law",
    64: "64 worker threads interactive law",
}

stat_color = {
    "25th percentile": seq_colors[0],
    "50th percentile": seq_colors[1],
    "75th percentile": seq_colors[2],
    "90th percentile": seq_colors[3],
    "99th percentile": "black",
    "mean": "#dfc27d"
}

stat_label = {
    "25th percentile": "25th percentile",
    "50th percentile": "50th percentile",
    "75th percentile": "75th percentile",
    "90th percentile": "90th percentile",
    "99th percentile": "99th percentile",
    "mean": "mean"
}
