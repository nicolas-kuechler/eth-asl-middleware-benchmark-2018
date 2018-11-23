import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import const

def nc(ax, df):

    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)


    rt_means = df.loc[:,'rt_rep_mean'].values
    rt_stds = df.loc[:,'rt_rep_std'].values

    rt_interactive_law = clients / throughput_means * 1000

    if const.use_interactive_law_rtt_adjustment and data_origin[0] == 'mw':
        rtt_client = np.unique(df.loc[:,'client_rtt'].values)
        assert(rtt_client.shape[0]==1)
        if rtt_client[0] != '-':
            rt_interactive_law = rt_interactive_law - rtt_client[0]

    ax.errorbar(clients, rt_means, rt_stds, capsize=const.capsize,
                                            color=const.color['single_color'],
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.label['measurement'])

    max_y = max(rt_means)

    if const.use_interactive_law_in_mw or data_origin[0] == 'client':
        ax.plot(clients, rt_interactive_law,color=const.color['single_color_interactive_law'],
                                        linestyle='--',
                                        label=const.label['interactive_law'])
        max_y = max(np.concatenate([rt_means, rt_interactive_law]))

    # TODO [nku] decide on legend
    ax.legend()
    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+2)
    ax.set_ylim(0, max_y*1.1)
    ax.set_xticks(clients)


def nc_w(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    max_y = []
    max_x = []

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values
        throughput_means = dfw.loc[:,'throughput_rep_mean'].values

        rt_means = dfw.loc[:,'rt_rep_mean'].values
        rt_stds = dfw.loc[:,'rt_rep_std'].values

        rt_interactive_law = clients / throughput_means * 1000

        if const.use_interactive_law_rtt_adjustment and data_origin[0] == 'mw':
            rtt_client = np.unique(df.loc[:,'client_rtt'].values)
            assert(rtt_client.shape[0]==1)

            if rtt_client[0] != '-':
                rt_interactive_law = rt_interactive_law - rtt_client[0]

        ax.errorbar(clients, rt_means, rt_stds, color=const.n_worker_color[n_worker],
                                                capsize=const.capsize,
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.n_worker_label[n_worker])

        cur_max_y = max(rt_means)

        if const.use_interactive_law_in_mw or data_origin[0] == 'client':
            ax.plot(clients, rt_interactive_law,color=const.n_worker_color[n_worker],
                                            linestyle='--',
                                            label=const.n_worker_inter_label[n_worker])
            cur_max_y = max(np.concatenate([rt_means, rt_interactive_law]))

        max_y.append(cur_max_y)
        max_x.append(max(clients))

    # TODO [nku] decide on legend to use
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+2)
    ax.set_ylim(0, max(max_y)*1.1)
    ax.set_xticks(clients)

def mget_perc(ax,df): # rt 3
    stats = np.unique(df.loc[:,'stat'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    max_y = []
    max_x = []

    for stat in stats:
        dfs = df[df["stat"]==stat]

        mget_sizes = dfs.loc[:,'multi_get_size'].values
        rts = dfs.loc[:,'rt_rep_mean'].values
        stds = dfs.loc[:,'rt_rep_std'].values

        ax.errorbar(mget_sizes, rts, stds, capsize=const.capsize,
                                            marker='.',
                                            markersize=const.markersize,
                                            color=const.stat_color[stat],
                                            label=const.stat_label[stat])

        max_y.append(max(rts))
        max_x.append(max(mget_sizes))

    # TODO [nku] decide on legend to use
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['mget_size'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)

    ax.set_xticks(mget_sizes)


def mget_hist(ax,df): # rt 4

    bins = x = np.sort(np.unique(np.concatenate([df['rt_bin_low'].values,df['rt_bin_high'].values])))
    bins[-1]=15

    rts = df.loc[:,'rt_bin_avg'].values
    rts[-1] = 14.75
    rt_freqs = df.loc[:,'rt_freq_mean'].values

    rt_stds = df.loc[:,'rt_freq_std'].values

    # TODO [nku] set fixed hist ylim
    ylim = max(rt_freqs+5000)

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    y, _ , _ = ax.hist(rts, weights=rt_freqs, bins=bins, color=const.color['hist'])
    ax.errorbar(rts, y, fmt='none', yerr=rt_stds, capsize=const.capsize, color=const.color['hist_error'])


    ax.set_ylabel(const.axis_label['freq'])
    ax.set_xlabel(const.axis_label['rt'])

    ax.text(0.95, 0.95, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_ylim(0, ylim)

def mget(ax, df):
    mget_sizes = df.loc[:,'multi_get_size'].values
    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    think_time = df.loc[:,'client_thinktime'].values
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)


    rt_means = df.loc[:,'rt_rep_mean'].values
    rt_stds = df.loc[:,'rt_rep_std'].values

    rt_interactive_law = clients / throughput_means * 1000 - think_time

    if const.use_interactive_law_rtt_adjustment and data_origin[0] == 'mw':
        rtt_client = np.unique(df.loc[:,'client_rtt'].values)
        assert(rtt_client.shape[0]==1)
        if rtt_client[0] != '-':
            rt_interactive_law = rt_interactive_law - rtt_client[0]

    ax.errorbar(mget_sizes, rt_means, rt_stds, capsize=const.capsize,
                                            color=const.color['single_color'],
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.label['measurement'])
    max_y = max(rt_means)

    if const.use_interactive_law_in_mw or data_origin[0] == 'client':
        ax.plot(mget_sizes, rt_interactive_law,color=const.color['single_color_interactive_law'],
                                        linestyle='--',
                                        label=const.label['interactive_law'])
        max_y = max(np.concatenate([rt_means, rt_interactive_law]))

    # TODO [nku] decide on legend
    ax.legend()
    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['mget_size'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+2)
    ax.set_ylim(0, max_y*1.1)
    ax.set_xticks(mget_sizes)

def queueing_model(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    assert(n_workers.shape[0]==1)

    clients = df.loc[:,'num_clients'].values

    meas_rts = df.loc[:,'meas_rt'].values
    mm1_rts = df.loc[:,'mm1_rt'].values
    mmm_rts = df.loc[:,'mmm_rt'].values

    ax.plot(clients, meas_rts,  color=const.queueing_color["meas"],
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.queueing_label["meas"])

    ax.plot(clients, mm1_rts,  color=const.queueing_color["mm1"],
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.queueing_label["mm1"])

    ax.plot(clients, mmm_rts,  color=const.queueing_color["mmm"],
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.queueing_label["mmm"].replace("m", f"{n_workers[0]*2}"))

    ax.legend()

    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['number_of_clients'])


    ax.set_xlim(0, max(clients)+2)
    ax.set_ylim(0, max(np.concatenate([meas_rts]))*1.5)
    ax.set_xticks(clients)



def component_nc_w(ax, df):


    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    N = np.unique(df.loc[:,'num_clients'].values).shape[0]
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ind = np.arange(N)    # the x locations for the groups
    width = 0.2        # the width of the bars

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values



        ntt_means = dfw.loc[:,'ntt_rep_mean'].values
        qwt_means = dfw.loc[:,'qwt_rep_mean'].values
        wtt_means = dfw.loc[:,'wtt_rep_mean'].values - dfw.loc[:,'sst_rep_mean'].values
        sst_means = dfw.loc[:,'sst_rep_mean'].values

        print(ind)
        print(ntt_means)

        ax.bar(ind, ntt_means, width, bottom=0, color='r', label="ntt")
        ax.bar(ind, qwt_means, width, bottom=ntt_means, color='b',  label="qwt")
        ax.bar(ind, wtt_means, width, bottom=qwt_means+ntt_means, color='y', label="wtt")
        ax.bar(ind, sst_means, width, bottom=wtt_means+qwt_means+ntt_means, color='g', label="sst")

        ind = ind + width

    ax.legend()

def time(ax, df):
    for rep in np.unique(df.loc[:,'rep'].values):
        df_rep = df[df['rep']==rep]

        slots = df_rep.loc[:,'slot'].values
        assert(slots.shape[0] == np.unique(slots).shape[0])

        rt_means = df_rep.loc[:,'rt_mean'].values
        rt_stds = df_rep.loc[:,'rt_std'].values
        ax.errorbar(slots, rt_means, rt_stds, marker='.', markersize=const.markersize, capsize=const.capsize, label=f"rep={rep}")

    ax.legend()
    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['slot'])

    ax.axvspan(0, const.min_slot_inclusive- 0.5, alpha=0.5, color='grey')
    ax.axvspan(const.max_slot_inclusive+ 0.5, slots[-1]+2, alpha=0.5, color='grey')
    ax.set_xlim(0, slots[-1]+2)
    ax.set_ylim(0, max(rt_means)+30)
    ax.set_xticks(slots)
