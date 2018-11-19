import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from queries import query_mw
from plots import rt, tp, qwt, ntt, wtt, sst, queue

pd.options.display.max_columns = None
output_folder = "./../../exp_plots"

def generate(plot_func, df, suite=None, name=None):
    plt.rc('font', family='serif', serif='Times')
    plt.rc('text', usetex=False)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)
    plt.rc('axes', labelsize=12)

    fig, ax = plt.subplots()
    plot_func(ax, df)

    if name is not None:
        assert(suite is not None)
        path = f"{output_folder}/{suite}"
        try:
            os.makedirs(path)
        except OSError:
            pass

        fig.savefig(f"{path}/{name}.pdf", bbox_inches='tight')
    plt.show()

def generate_latex(latex_str, suite=None, name=None):
    path = f"{output_folder}/{suite}"
    try:
        os.makedirs(path)
    except OSError:
        pass

    with open(f"{path}/{name}.tex", "w+") as f:
        f.write(latex_str)


def dashboard_nc(df):
    generate(qwt.nc_w, df)
    generate(ntt.nc_w, df)
    generate(wtt.nc_w, df)
    generate(sst.nc_w, df)
    generate(queue.nc_w, df)

def dashboard_mget(df):
    generate(tp.mget, df)
    generate(rt.mget, df)
    generate(qwt.mget, df)
    generate(ntt.mget, df)
    generate(wtt.mget, df)
    generate(sst.mget, df)
    generate(queue.mget, df)

def dashboard_time(suite, exp_name):
    df = query_mw.load_df_by_slot(suite=suite ,exp=exp_name)
    for n_w in np.unique(df.loc[:,'n_worker_per_mw'].values):
        for op_type in np.unique(df.loc[:,'op_type'].values):
            for num_clients in np.unique(df.loc[:,'num_clients'].values):
                for mget_size in np.unique(df.loc[:,'multi_get_size'].values):
                    df_filtered = df[(df['n_worker_per_mw']==n_w) & (df['op_type']==op_type) & (df['num_clients']==num_clients) & (df['multi_get_size']==mget_size)]

                    print(f"n_w={n_w}   op_type={op_type}  num_clients={num_clients}   mget_size={mget_size}")
                    generate(tp.time, df_filtered)
                    generate(rt.time, df_filtered)
                    generate(qwt.time, df_filtered)
                    generate(ntt.time, df_filtered)
                    generate(wtt.time, df_filtered)
                    generate(sst.time, df_filtered)
                    generate(queue.time, df_filtered)
