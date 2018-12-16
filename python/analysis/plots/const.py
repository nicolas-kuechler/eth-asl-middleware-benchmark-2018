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


color_d = {
"network":["#3182bd","#6baed6", "#9ecae1", "#c6dbef"],
"sst":["#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2"],
"wtt":["#31a354", "#74c476", "#a1d99b", "#c7e9c0"],
"qwt":["#756bb1","#9e9ac8", "#bcbddc", "#dadaeb"],
"ntt": ["#636363","#969696","#bdbdbd", "#d9d9d9"]
}

network_throughput_limit_color = "black"
network_throughput_limit_linestyle = "--"

color = {
    "single_color":seq_colors[3],
    "single_color_interactive_law": seq_colors[2],
    "network_throughput_limit": "grey",
    "hist_error": "grey",
    "hist": seq_colors[1],
    "sharded": '#a1dab4',
    "nonsharded": '#2c7fb8',
    "sharded_interactive_law":"#a1dab4",
    "nonsharded_interactive_law": "#2c7fb8"
}


rt_component_color = {
    "network": color_d['network'][2], #"#01295f", #"#bfd2bf", #"#f5ee9e",
    "ntt": color_d['ntt'][2],#"#437f97", #"#646f4b", #"#2d728f",
    "qwt": color_d['qwt'][2], #"#849324", #"#46351d", #"#3b8ea5",
    "wtt": color_d['wtt'][2],#"#ffb30f",#"#839d9a", #"#f49e4c",
    "sst": color_d['sst'][2]#"#fd151b", #"#7bb2d9"#"#ab3428"
}

sst_color = {
    "tsst": color_d['sst'][0], #"#849324",
    "sst0": color_d['sst'][2],#"#fb6a4a",
    "sst1": color_d['sst'][0],#"#de2d26",
    "sst2": "#a50f15"#color_d['sst'][0] #"#a50f15",
}

sst_label = {
    "tsst": "total",
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
    "mget_size": "multi-GET Size",
    "freq": "Frequency",
    "slot": "Slot",
    "queue_size": "Queue Length",
    "sst":"Server Service Time [ms]",
    "n_worker": "Number of Worker-Threads",
    "qwt": "Queue Waiting Time [ms]",
    "util": "Utilization [%]"
}

label = {
    "interactive_law": "interactive law",
    "measurement": "measurement",
    "network_throughput_limit": "bandwidth limit",
    "sharded": "GET sharded",
    "nonsharded": "GET non-sharded",
    "sharded_interactive_law" : "sharded interactuve law",
    "nonsharded_interactive_law" : "non-sharded interactuve law"
}

queueing_color = {
    "meas" : seq_colors[3],
    "mm1": "#e6550d",
    "mmm": "#31a354" #seq_colors[1]
}

queueing_label = {
    "meas" : "measured",
    "mm1":  "M/M/1",
    "mmm": "M/M/m"
}

noq_color = {
    "1mw":["#e6550d", "#fdae6b", "#fdd0a2"],
    "2mw":["#31a354","#a1d99b"]
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
    "mean": "#fd8d3c"#"#dfc27d"
}

stat_label = {
    "25th percentile": "GET 25th percentile",
    "50th percentile": "GET 50th percentile",
    "75th percentile": "GET 75th percentile",
    "90th percentile": "GET 90th percentile",
    "99th percentile": "GET 99th percentile",
    "mean": "GET average"
}
