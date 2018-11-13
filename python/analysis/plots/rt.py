import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def nc(ax, df): # rt1

    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)


    rt_means = df.loc[:,'rt_rep_mean'].values
    rt_stds = df.loc[:,'rt_rep_std'].values

    rt_interactive_law = clients / throughput_means * 1000

    ax.errorbar(clients, rt_means, rt_stds, capsize=5, marker='.', markersize=10,label="response time")
    ax.plot(clients, rt_interactive_law, linestyle='--', label="interactive law")



    ax.legend()
    ax.set_ylabel('Response Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(rt_means+rt_interactive_law)*1.1)
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

        ax.errorbar(clients, rt_means, rt_stds, capsize=5, marker='.', markersize=10, label=f"w={n_worker}")
        ax.plot(clients, rt_interactive_law, linestyle='--',label=f"w={n_worker}")

        max_y.append(max(rt_means+rt_interactive_law))
        max_x.append(max(clients))

    ax.legend()
    ax.set_ylabel('Response Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
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


        ax.errorbar(mget_sizes, rts, stds, capsize=5, marker='.', markersize=10, label=f"{stat}")


        max_y.append(max(rts))
        max_x.append(max(mget_sizes))

    ax.legend()
    ax.set_ylabel('Response Time [ms]')
    ax.set_xlabel('Multi Get Size')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)


def mget_hist(ax,df): # rt 4

    #bins =  np.arange(0.0, 20.0, 0.5)
    bins = x = np.sort(np.unique(np.concatenate([df['rt_bin_low'].values,df['rt_bin_high'].values])))
    bins[-1]=20


    rts = df.loc[:,'rt_bin_avg'].values
    rts[-1] = 19.75
    rt_freqs = df.loc[:,'rt_freq_mean'].values

    rt_stds = df.loc[:,'rt_freq_std'].values

    ylim = max(rt_freqs+5000)
    #data_origin = np.unique(df.loc[:,'data_origin'].values)
    #assert(data_origin.shape[0]==1)

    y, _ , _ = ax.hist(rts, weights=rt_freqs, bins=bins)
    ax.errorbar(rts, y, fmt='none', yerr=rt_stds, capsize=5)


    ax.set_ylabel('Frequency')
    ax.set_xlabel('Response Time [ms]')

    #ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_ylim(0, ylim)
