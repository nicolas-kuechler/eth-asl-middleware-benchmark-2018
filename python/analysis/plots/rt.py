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
    #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.legend()

    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['number_of_clients'])


    ax.set_xlim(0, max(max_x)+2)
    ax.set_ylim(0, max(max_y)*1.1)
    ax.set_xticks(clients)

def mget_perc(ax,df, y_lim=None): # rt 3
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

    if y_lim is None:
        y_lim = max(max_y)*1.1

    ax.set_ylim(0, y_lim)

    ax.set_xticks(mget_sizes)


def mget_hist(ax,df, y_lim): # rt 4

    bins = x = np.sort(np.unique(np.concatenate([df['rt_bin_low'].values,df['rt_bin_high'].values])))
    bins[-1]=15

    rts = df.loc[:,'rt_bin_avg'].values
    rts[-1] = 14.75
    rt_freqs = df.loc[:,'rt_freq_mean'].values

    rt_stds = df.loc[:,'rt_freq_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    y, _ , _ = ax.hist(rts, weights=rt_freqs, bins=bins, color=const.color['hist'])
    ax.errorbar(rts, y, fmt='none', yerr=rt_stds, capsize=const.capsize-2, color=const.color['hist_error'])

    ax.set_ylabel(const.axis_label['freq'])
    ax.set_xlabel(const.axis_label['rt'])

    ax.text(0.95, 0.95, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')
    ax.set_xticks(np.arange(0,16))
    ax.set_ylim(0, y_lim)

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

    ax.set_xlim(0, mget_sizes[-1]+1)
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
                                            linestyle='None',
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.queueing_label["mm1"])

    ax.plot(clients, mmm_rts,  color=const.queueing_color["mmm"],
                                            linestyle='None',
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.queueing_label["mmm"].replace("m", f"{n_workers[0]*2}"))

    ax.legend()

    ax.set_ylabel(const.axis_label['rt'])
    ax.set_xlabel(const.axis_label['number_of_clients'])


    ax.set_xlim(0, max(clients)+2)
    ax.set_ylim(0, max(np.concatenate([meas_rts]))*1.5)
    ax.set_xticks(clients)

def component_w(ax, df):
    clients = df['num_clients'].unique()
    assert(clients.shape[0]==1)

    ntts = df.loc[:,'ntt'].values
    qwts = df.loc[:,'qwt'].values

    if df.loc[:,'workload'].unique() == 'write-only':
        ssts = df.loc[:,'sstmax'].values
    else:
        ssts = df.loc[:,'sst'].values

    wtts = df.loc[:,'wtt'].values

    rts_client = df.loc[:,'rt_client'].values
    network = rts_client - (wtts+qwts+ntts+ssts)
    network = network.clip(min=0)

    n_workers = df['n_worker_per_mw'].unique()

    ind = np.arange(n_workers.shape[0])
    width = 0.7
    cum = 0
    ax.bar(ind, ntts, width, bottom = cum,
                                color=const.rt_component_color['ntt'],
                                label=const.rt_component_label['ntt'])
    cum = ntts
    ax.bar(ind, qwts, width, bottom = cum,
                                    color=const.rt_component_color['qwt'],
                                    label=const.rt_component_label['qwt'])

    cum = cum + qwts
    ax.bar(ind, wtts, width, bottom = cum,
                                    color=const.rt_component_color['wtt'],
                                    label=const.rt_component_label['wtt'])

    cum = cum + wtts
    ax.bar(ind, ssts, width, bottom = cum,
                                    color=const.rt_component_color['sst'],
                                    label=const.rt_component_label['sst'])

    cum = cum + ssts

    ax.bar(ind, network, width, bottom = cum,
                                    color=const.rt_component_color['network'],
                                    label=const.rt_component_label['network'])

    ax.set_ylabel("Time [ms]")

    labels = [const.n_worker_label_short[n_worker] for n_worker in n_workers]
    plt.xticks(ind, (8,16,32,64))
    ax.set_xlabel(const.axis_label['n_worker'])
    ax.set_xlim(-0.5, 7)
    ax.legend(loc='lower right')
    #ax.legend(bbox_to_anchor=(1.0, 0, 0.5, 1), ncol=1, mode="expand", borderaxespad=0)




def component_nc(ax, df, max_y):

    clients = df.loc[:,'num_clients'].values

    ntts = df.loc[:,'ntt'].values
    qwts = df.loc[:,'qwt'].values

    if df.loc[:,'workload'].unique() == 'write-only':
        ssts = df.loc[:,'sstmax'].values
    else:
        ssts = df.loc[:,'sst'].values

    wtts = df.loc[:,'wtt'].values

    rts_client = df.loc[:,'rt_client'].values
    network = rts_client - (wtts+qwts+ntts+ssts)
    network = network.clip(min=0)

    cum = ntts
    ax.plot(clients, cum, color='black', marker='.' ,markersize=const.markersize)

    cum += qwts
    ax.plot(clients, cum, color='black', marker='.' ,markersize=const.markersize)

    cum += wtts
    ax.plot(clients, cum, color='black', marker='.' ,markersize=const.markersize)

    cum += ssts
    ax.plot(clients, cum, color='black', marker='.' ,markersize=const.markersize)


    cum += network
    ax.plot(clients, cum, color='black', marker='.' ,markersize=const.markersize)
    ax.fill_between(clients, 0, cum, alpha=0.2, facecolor=const.rt_component_color['network'], hatch = '/',edgecolor=const.rt_component_color['network'], label=const.rt_component_label['network'])
    ax.fill_between(clients, 0, cum-network, alpha=0.2, facecolor=const.rt_component_color['sst'], hatch = '/', edgecolor=const.rt_component_color['sst'], label=const.rt_component_label['sst'])
    ax.fill_between(clients, 0, cum-network-ssts, alpha=0.2, facecolor=const.rt_component_color['wtt'], hatch = '/', edgecolor=const.rt_component_color['wtt'], label=const.rt_component_label['wtt'])
    ax.fill_between(clients, 0, cum-network-ssts-wtts, alpha=0.2, facecolor=const.rt_component_color['qwt'], hatch = '/', edgecolor=const.rt_component_color['qwt'], label=const.rt_component_label['qwt'])
    ax.fill_between(clients, 0, cum-network-ssts-wtts-qwts, alpha=0.2, facecolor=const.rt_component_color['ntt'], hatch = '/', edgecolor=const.rt_component_color['ntt'], label=const.rt_component_label['ntt'])

    ax.plot(clients, cum, color='black', marker='.' ,markersize=const.markersize)


    ax.set_ylabel("Time [ms]")
    ax.set_xlabel(const.axis_label['number_of_clients'])


    ax.set_xlim(0, max(clients)+2)
    ax.set_ylim(0, max_y)
    ax.set_xticks(clients)
    ax.legend()

def component_mget(ax, df):
    mget_sizes = df['multi_get_size'].unique()

    ntts = df.loc[:,'ntt'].values
    qwts = df.loc[:,'qwt'].values

    ssts = df.loc[:,'tsst'].values
    wtts = df.loc[:,'wtt'].values

    rts_client = df.loc[:,'rt_client'].values
    network = rts_client - (wtts+qwts+ntts+ssts)
    network = network.clip(min=0)

    mget_sizes = df['multi_get_size'].unique()

    ind = np.arange(mget_sizes.shape[0])
    width = 0.7
    cum = 0
    ax.bar(ind, ntts, width, bottom = cum,
                                color=const.rt_component_color['ntt'],
                                label=const.rt_component_label['ntt'])
    cum = ntts
    ax.bar(ind, qwts, width, bottom = cum,
                                    color=const.rt_component_color['qwt'],
                                    label=const.rt_component_label['qwt'])

    cum = cum + qwts
    ax.bar(ind, wtts, width, bottom = cum,
                                    color=const.rt_component_color['wtt'],
                                    label=const.rt_component_label['wtt'])

    cum = cum + wtts
    ax.bar(ind, ssts, width, bottom = cum,
                                    color=const.rt_component_color['sst'],
                                    label=const.rt_component_label['sst'])

    cum = cum + ssts

    ax.bar(ind, network, width, bottom = cum,
                                    color=const.rt_component_color['network'],
                                    label=const.rt_component_label['network'])

    ax.set_ylabel("Time [ms]")


    plt.xticks(ind, (1,3,6,9))
    ax.set_xlabel(const.axis_label['mget_size'])
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(0,9)
    ax.legend(loc='upper left')
    #ax.legend(bbox_to_anchor=(1.0, 0, 0.5, 1), ncol=1, mode="expand", borderaxespad=0)



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
