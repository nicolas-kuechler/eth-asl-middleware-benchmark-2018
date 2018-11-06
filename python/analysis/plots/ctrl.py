import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import rt, tp

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
