import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
import os

from plots import const

def tp_format(x, pos):
    'The two args are the value and tick position'
    return f"{x/1000}k"
tp_formatter = FuncFormatter(tp_format)

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
                                                            label=const.label['measurement'],
                                                            linewidth=const.linewidth)

    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput'].values
    elif op_type == "get":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        raise ValueError("Unknown Op Type")

    cur_max_y = max(np.concatenate([throughput_means, bandwidth_throughput_limit]))

    if const.use_interactive_law_in_mw or data_origin[0] == 'client':
        ax.plot(clients, throughput_interactive_law, color=const.color['single_color_interactive_law'],
                                                    linestyle='--',
                                                    label=const.label['interactive_law'],
                                                    linewidth=const.linewidth)
        cur_max_y = max(np.concatenate([throughput_means,throughput_interactive_law,bandwidth_throughput_limit]))



    if np.unique(bandwidth_throughput_limit)[0] != "-":
        ax.plot(clients, bandwidth_throughput_limit, linestyle='--', color=const.color['network_throughput_limit'], label=const.label['network_throughput_limit'], linewidth=const.linewidth)

    # TODO [nku] decide on legend to use
    ax.legend()
    ax.yaxis.set_major_formatter(tp_formatter)

    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+2)
    ax.set_ylim(0, cur_max_y*1.1)
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
                                                                label=const.n_worker_label[n_worker],
                                                                linewidth=const.linewidth)
        cur_max_y = max(throughput_means)

        if const.use_interactive_law_in_mw or data_origin[0] == 'client':
            ax.plot(clients, throughput_interactive_law,color=const.n_worker_color[n_worker],
                                                    linestyle='--',
                                                    label=const.n_worker_inter_label[n_worker],
                                                    linewidth=const.linewidth)
            cur_max_y = max(np.concatenate([throughput_means, throughput_interactive_law]))


        max_y.append(cur_max_y)
        max_x.append(max(clients))

    if op_type == "set":
        bandwidth_throughput_limit = dfw.loc[:,'bandwidth_limit_write_per_server_throughput'].values
    elif op_type == "get":
        bandwidth_throughput_limit = dfw.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        raise ValueError("Unknown Op Type")

    if np.unique(bandwidth_throughput_limit)[0] != "-":
        ax.plot(clients, bandwidth_throughput_limit,color=const.network_throughput_limit_color,
                                                    linestyle=const.network_throughput_limit_linestyle,
                                                    label=const.label['network_throughput_limit'],
                                                    linewidth=const.linewidth)
        max_y.append(max(bandwidth_throughput_limit))

    # TODO [nku] decide on legend to use
    #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax.text(0.05, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.legend(loc='lower right')
    ax.yaxis.set_major_formatter(tp_formatter)

    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['number_of_clients'])


    ax.set_xlim(0, max(max_x)+2)
    ax.set_ylim(0, max(max_y)*1.05)

    ax.set_xticks(clients)

    #plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='right', verticalalignment='center')

def mget(ax, df):
    clients = df.loc[:,'num_clients'].values
    mget_sizes = df.loc[:,'multi_get_size'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    throughput_stds = df.loc[:,'throughput_rep_std'].values
    think_time = df.loc[:,'client_thinktime'].values

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

    throughput_interactive_law = clients / (rt_means_interactive_law + think_time) * 1000

    ax.errorbar(mget_sizes, throughput_means, throughput_stds, color=const.color['single_color'],
                                                            capsize=const.capsize,
                                                            marker='.',
                                                            markersize=const.markersize,
                                                            label=const.label['measurement'])
    max_y = max(throughput_means)
    if const.use_interactive_law_in_mw or data_origin[0] == 'client':
        ax.plot(mget_sizes, throughput_interactive_law, color=const.color['single_color_interactive_law'],
                                                    linestyle='--',
                                                    label=const.label['interactive_law'])
        max_y = max(np.concatenate([throughput_means,throughput_interactive_law]))
    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput'].values
    elif op_type == "get" or op_type == "mget":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput'].values
    else:
        print(op_type)
        raise ValueError("Unknown Op Type")

    if np.unique(bandwidth_throughput_limit)[0] != "-":
        sizes = np.arange(min(mget_sizes),max(mget_sizes))
        ax.plot(sizes, bandwidth_throughput_limit[0] / sizes, linestyle='--', color=const.network_throughput_limit_color, label=const.label['network_throughput_limit'])

    ax.legend()

    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['mget_size'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, mget_sizes[-1]+1)
    ax.set_ylim(0, max_y*1.1)
    ax.set_xticks(mget_sizes)

def mget_mix(ax, df):
    clients = df.loc[:,'num_clients'].values
    mget_sizes = df.loc[:,'multi_get_size'].values
    throughput_means_sharded = df.loc[:,'throughput_rep_mean_sharded'].values
    throughput_stds_sharded = df.loc[:,'throughput_rep_std_sharded'].values
    think_time_sharded = df.loc[:,'client_thinktime_sharded'].values

    throughput_means_nonsharded = df.loc[:,'throughput_rep_mean_nonsharded'].values
    throughput_stds_nonsharded = df.loc[:,'throughput_rep_std_nonsharded'].values
    think_time_nonsharded = df.loc[:,'client_thinktime_nonsharded'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    op_type = np.unique(df.loc[:,'op_type'].values)

    assert(op_type.shape[0]==1)
    assert(data_origin.shape[0]==1)

    rt_means_sharded = df.loc[:,'rt_rep_mean_sharded'].values
    rt_means_nonsharded = df.loc[:,'rt_rep_mean_nonsharded'].values

    if const.use_interactive_law_rtt_adjustment and data_origin[0] == 'mw':
        rtt_client_sharded = np.unique(df.loc[:,'client_rtt_sharded'].values)
        assert(rtt_client_sharded.shape[0]==1)

        rtt_client_nonsharded = np.unique(df.loc[:,'client_rtt_nonsharded'].values)
        assert(rtt_client_nonsharded.shape[0]==1)

        if rtt_client_sharded[0] != '-':
            rt_means_sharded_interactive_law = rt_means_sharded + rtt_client_sharded[0]
        else: rt_means_sharded_interactive_law = rt_means_sharded

        if rtt_client_nonsharded[0] != '-':
            rt_means_nonsharded_interactive_law = rt_means_nonsharded + rtt_client_nonsharded[0]
        else: rt_means_nonsharded_interactive_law = rt_means_nonsharded
    else:
        rt_means_sharded_interactive_law = rt_means_sharded
        rt_means_nonsharded_interactive_law = rt_means_nonsharded

    throughput_sharded_interactive_law = clients / (rt_means_sharded_interactive_law + think_time_sharded) * 1000
    throughput_nonsharded_interactive_law = clients / (rt_means_nonsharded_interactive_law + think_time_nonsharded) * 1000

    ax.errorbar(mget_sizes, throughput_means_nonsharded, throughput_stds_nonsharded, color=const.color['nonsharded'],
                                                            capsize=const.capsize,
                                                            marker='.',
                                                            markersize=const.markersize,
                                                            label=const.label['nonsharded'])

    ax.errorbar(mget_sizes, throughput_means_sharded, throughput_stds_sharded, color=const.color['sharded'],
                                                            capsize=const.capsize,
                                                            marker='.',
                                                            markersize=const.markersize,
                                                            label=const.label['sharded'])



    max_y = max(max(throughput_means_sharded),max(throughput_means_nonsharded))

    if const.use_interactive_law_in_mw or data_origin[0] == 'client':
        ax.plot(mget_sizes, throughput_sharded_interactive_law, color=const.color['sharded_interactive_law'],
                                                    linestyle='--',
                                                    label=const.label['sharded_interactive_law'])

        ax.plot(mget_sizes, throughput_nonsharded_interactive_law, color=const.color['nonsharded_interactive_law'],
                                                    linestyle='--',
                                                    label=const.label['nonsharded_interactive_law'])
        max_y = max(max_y, max(throughput_sharded_interactive_law), max(throughput_nonsharded_interactive_law))

    if op_type == "set":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_write_throughput_sharded'].values
    elif op_type == "get" or op_type == "mget":
        bandwidth_throughput_limit = df.loc[:,'bandwidth_limit_read_throughput_sharded'].values
    else:
        print(op_type)
        raise ValueError("Unknown Op Type")

    if np.unique(bandwidth_throughput_limit)[0] != "-":
        sizes = np.arange(min(mget_sizes),max(mget_sizes)+1)
        ax.plot(sizes, bandwidth_throughput_limit[0] / sizes, linestyle='--', color=const.network_throughput_limit_color, label=const.label['network_throughput_limit'])

    ax.legend()

    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['mget_size'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, mget_sizes[-1]+1)
    ax.set_ylim(0, max_y*1.1)
    ax.set_xticks(mget_sizes)

def time(ax, df):

    slots = None

    for rep in np.unique(df.loc[:,'rep'].values):
        df_rep = df[df['rep']==rep]

        slots = df_rep.loc[:,'slot'].values
        assert(slots.shape[0] == np.unique(slots).shape[0])

        throughputs = df_rep.loc[:,'throughput'].values
        ax.plot(slots, throughputs, marker='.', markersize=const.markersize, label=f"rep={rep}")

    if slots is None:
        display(df)

    ax.legend()
    ax.set_ylabel(const.axis_label['throughput'])
    ax.set_xlabel(const.axis_label['slot'])

    ax.axvspan(0, const.min_slot_inclusive-0.5, alpha=0.5, color='grey')
    ax.axvspan(const.max_slot_inclusive+0.5, slots[-1]+2, alpha=0.5, color='grey')
    ax.set_xlim(0, slots[-1]+2)
    ax.set_ylim(0, max(throughputs*1.2))
    ax.set_xticks(slots)
