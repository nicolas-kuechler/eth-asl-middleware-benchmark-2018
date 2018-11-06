import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import rt, tp, qwt, ntt, wtt, sst

pd.options.display.max_columns = None
output_folder = "./../../../exp_plots"

def generate(plot_func, df, suite=None, name=None):
    fig, ax = plt.subplots()
    plot_func(ax, df)

    if name is not None:
        assert(suite is not None)
        path = f"{output_folder}/{suite}"
        try:
            os.makedirs(path)
        except OSError:
            pass

        fig.savefig(f"{path}/{name}.pdf")
    plt.show()


def dashboard(df):
    generate(qwt.nc_w, df)
    generate(ntt.nc_w, df)
    generate(wtt.nc_w, df)
    generate(sst.nc_w, df)
