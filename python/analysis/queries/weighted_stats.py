from decimal import *
import copy
import numpy as np
import pandas as pd
import itertools


def weighted_quantiles_mean(df, value_col, weight_col, quantiles):

    cols = list(df.columns.values)
    cols.remove(value_col)
    cols.remove(weight_col)

    tuples = list(map(lambda x: itertools.zip_longest([x], np.unique(df.loc[:,x].values), fillvalue=x), cols))

    lst = []

    for x in itertools.product(*tuples):
        df1 = df
        for t in x:
            df1 = df1[(df1[t[0]]==t[1])]
        if df1.shape[0] > 0:

            base = df1.iloc[0,:].to_dict()

            del base[value_col]
            del base[weight_col]

            for quantile in quantiles:
                q = _wquantile(values=df1.loc[:,'rt'].values, weights= df1.loc[:,'rt_freq'].values, quantile=quantile)

                row = copy.deepcopy(base)
                row['stat'] = f"{int(quantile*100)}th percentile"
                row['rt'] = q
                lst.append(row)


            k = df1.groupby(lambda x: True).apply(lambda x: np.average(x['rt'], weights=x['rt_freq']))[1]
            row = copy.deepcopy(base)
            row['stat'] = "mean"
            row['rt'] = k
            lst.append(row)


    return pd.DataFrame(lst)



def _wquantile(values, weights, quantile):

    # sort values and weights by value defined sort order
    sorter = np.argsort(values)
    values = np.array(values)[sorter]
    weights = np.array(weights)[sorter]

    n = int(np.sum(weights))

    cum_weights = np.cumsum(weights)

    # find index of quantile element according to the book
    getcontext().rounding = ROUND_HALF_DOWN
    xth_elem = Decimal(quantile) * Decimal(n-1) + Decimal(1)
    xth_elem = int(round(xth_elem))

    for i in range(cum_weights.shape[0]):
        if xth_elem <= cum_weights[i]:
            return  values[i]

    print(xth_elem)
    print(values)
    print(weights)
    raise ValueError()


if __name__ == '__main__':
    # checks from the book
    values =  [1.9, 2.7, 2.8, 2.9, 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 3.8, 3.9, 4.1, 4.2, 4.4, 4.5, 4.8, 4.9, 5.1, 5.3, 5.6, 5.9]
    weights = [1  ,1   ,3   ,1   ,2   ,2   ,1   ,1   ,1   ,1   ,1   ,3   ,2   ,2   ,1   ,2   ,1   ,1   ,2   ,1   ,1   ,1   ]

    assert(1.9==_wquantile(values=values, weights=weights, quantile=0.0))
    assert(2.8==_wquantile(values=values, weights=weights, quantile=0.1))
    assert(3.2==_wquantile(values=values, weights=weights, quantile=0.25))
    assert(3.9==_wquantile(values=values, weights=weights, quantile=0.5))
    assert(4.5==_wquantile(values=values, weights=weights, quantile=0.75))
    assert(5.1==_wquantile(values=values, weights=weights, quantile=0.9))
    assert(5.9==_wquantile(values=values, weights=weights, quantile=1.0))
