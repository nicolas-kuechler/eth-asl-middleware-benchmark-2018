import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


def nc(ax, df): # t1
    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    throughput_stds = df.loc[:,'throughput_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    op_type = np.unique(df.loc[:,'op_type'].values)

    assert(op_type.shape[0]==1)
    assert(data_origin.shape[0]==1)

    rt_means = df.loc[:,'rt_rep_mean'].values

    throughput_interactive_law = clients / rt_means * 1000

    ax.errorbar(clients, throughput_means, throughput_stds, capsize=5, marker='.', markersize=10 ,label="throughput")
    ax.plot(clients, throughput_interactive_law, linestyle='--', label="interactive law")

    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput'].values
    elif op_type == "get":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        raise ValueError("Unknown Op Type")

    if np.asscalar(np.unique(bandwidth_throughput_limit)) != "-":
        ax.plot(clients, bandwidth_throughput_limit, linestyle='--', label="throughput limit")

    ax.legend()
    ax.set_ylabel('Throughput [req/sec]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(throughput_means+throughput_interactive_law)*1.1)
    ax.set_xticks(clients)


def nc_w(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    op_type = np.unique(df.loc[:,'op_type'].values)

    assert(op_type.shape[0]==1)
    assert(data_origin.shape[0]==1)
    max_y = []
    max_x = []

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values
        throughput_means = dfw.loc[:,'throughput_rep_mean'].values
        throughput_stds = dfw.loc[:,'throughput_rep_std'].values

        rt_means = dfw.loc[:,'rt_rep_mean'].values

        throughput_interactive_law = clients / rt_means * 1000

        ax.plot(clients, throughput_interactive_law, linestyle='--',label=f"w={n_worker}")
        ax.errorbar(clients, throughput_means, throughput_stds, capsize=5, marker='.', markersize=10, label=f"w={n_worker}")

        max_y.append(max(throughput_means + throughput_interactive_law))
        max_x.append(max(clients))

    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput'].values
    elif op_type == "get":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        raise ValueError("Unknown Op Type")

    if np.asscalar(np.unique(bandwidth_throughput_limit)) != "-":
        ax.plot(clients, bandwidth_throughput_limit, linestyle='--', label="throughput limit")


    ax.legend()
    ax.set_ylabel('Throughput [req/sec]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)

    ax.set_xticks(clients)
