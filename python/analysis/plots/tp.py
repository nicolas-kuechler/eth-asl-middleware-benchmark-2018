import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import const


def nc(ax, df): # t1
    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    throughput_stds = df.loc[:,'throughput_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    op_type = np.unique(df.loc[:,'op_type'].values)

    assert(op_type.shape[0]==1)
    assert(data_origin.shape[0]==1)

    rt_means = df.loc[:,'rt_rep_mean'].values

    if const.use_interactive_law_rtt_adjustment and data_origin[0] == 'mw':
        rtt_client = np.unique(df.loc[:,'client_rtt'].values)
        assert(rtt_client.shape[0]==1)
        if rtt_client[0] != '-':
            rt_means_interactive_law = rt_means + rtt_client[0]
        else: rt_means_interactive_law = rt_means
    else:
        rt_means_interactive_law = rt_means

    throughput_interactive_law = clients / rt_means_interactive_law * 1000

    ax.errorbar(clients, throughput_means, throughput_stds, color=const.color['single_color'],
                                                            capsize=const.capsize,
                                                            marker='.',
                                                            markersize=const.markersize,
                                                            label=const.label['measurement'])
    ax.plot(clients, throughput_interactive_law, color=const.color['single_color_interactive_law'],
                                                    linestyle='--',
                                                    label=const.label['interactive_law'])

    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput'].values
    elif op_type == "get":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        raise ValueError("Unknown Op Type")

    if np.asscalar(np.unique(bandwidth_throughput_limit)) != "-":
        ax.plot(clients, bandwidth_throughput_limit, linestyle='--', label=const.label['network_throughput_limit'])

    # TODO [nku] decide on legend to use
    ax.legend()

    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+2)
    ax.set_ylim(0, max(np.concatenate([throughput_means,throughput_interactive_law]))*1.1)
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

        if const.use_interactive_law_rtt_adjustment and data_origin[0] == 'mw':
            rtt_client = np.unique(dfw.loc[:,'client_rtt'].values)
            assert(rtt_client.shape[0]==1)
            if rtt_client[0] != '-':
                rt_means_interactive_law = rt_means + rtt_client[0]
            else: rt_means_interactive_law = rt_means
        else:
            rt_means_interactive_law = rt_means

        throughput_interactive_law = clients / rt_means_interactive_law * 1000



        ax.errorbar(clients, throughput_means, throughput_stds, color=const.n_worker_color[n_worker],
                                                                capsize=const.capsize,
                                                                marker='.',
                                                                markersize=const.markersize,
                                                                label=const.n_worker_label[n_worker])

        ax.plot(clients, throughput_interactive_law,color=const.n_worker_color[n_worker],
                                                    linestyle='--',
                                                    label=const.n_worker_inter_label[n_worker])

        max_y.append(max(np.concatenate([throughput_means, throughput_interactive_law])))
        max_x.append(max(clients))

    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput'].values
    elif op_type == "get":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        raise ValueError("Unknown Op Type")

    if np.asscalar(np.unique(bandwidth_throughput_limit)) != "-":
        ax.plot(clients, bandwidth_throughput_limit,color=const.network_throughput_limit_color,
                                                    linestyle=const.network_throughput_limit_linestyle,
                                                    label=const.label['network_throughput_limit'])


    # TODO [nku] decide on legend to use
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+2)
    ax.set_ylim(0, max(max_y)*1.1)

    ax.set_xticks(clients)
