use_interactive_law_rtt_adjustment = True

markersize = 8
capsize = 5


# from http://colorbrewer2.org
seq_colors = ['#a1dab4', '#41b6c4', '#2c7fb8', '#253494']



network_throughput_limit_color = "black"
network_throughput_limit_linestyle = "--"

color = {
    "single_color":seq_colors[3],
    "single_color_interactive_law": seq_colors[2],
    "hist_error": "grey",
    "hist": seq_colors[1]
}


axis_label = {
    "number_of_clients": "Number of Clients",
    "throughput": "Throughput [req/sec]",
    "rt": "Response Time [ms]",
    "mget_size": "Multi Get Size",
    "freq": "Frequency",
    "slot": "Slot"
}

label = {
    "interactive_law": "interactive law",
    "measurement": "measurement",
    "network_throughput_limit": "throughput limit"
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
    8:  "  8 worker threads",
    16: "16 worker threads",
    32: "32 worker threads",
    64: "64 worker threads",
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
