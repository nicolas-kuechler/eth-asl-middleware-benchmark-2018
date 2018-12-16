import numpy as np

def interactive_law_mix(df_client, df_mw):

    key_col = ['workload', 'n_worker_per_mw', 'num_clients']
    cols = ['workload', 'n_worker_per_mw', 'num_clients', 'throughput_rep_mean_mw','throughput_rep_mean_client', 'rt_rep_mean_mw', 'rt_rep_mean_client']

    df = df_mw.set_index(key_col).join(df_client.set_index(key_col),lsuffix='_mw', rsuffix='_client')
    df = df.reset_index()
    df = df[cols]
    df = df.rename(columns={'throughput_rep_mean_mw': 'tp_mw',
                            'throughput_rep_mean_client': 'tp_client',
                            'rt_rep_mean_mw':'rt_mw',
                            'rt_rep_mean_client':'rt_client'
                           })

    df['rt_ilaw'] = df.apply(lambda row: row['num_clients']/row['tp_mw']*1000,axis=1)
    df['tp_ilaw'] = df.apply(lambda row: row['num_clients']/row['rt_client']*1000,axis=1)

    df['rt_ilaw_diff'] = df.apply(lambda row: round(row['rt_ilaw']-row['rt_client'],1),axis=1)
    df['tp_ilaw_diff'] = df.apply(lambda row: round(abs(row['tp_ilaw']-row['tp_mw']),0),axis=1)

    df.loc[df['rt_ilaw_diff']==-0.0, 'rt_ilaw_diff'] = 0.0

    df = df[df['workload']=='write-only'].set_index(['n_worker_per_mw', 'num_clients']).join(df[df['workload']=='read-only'].set_index(['n_worker_per_mw', 'num_clients']),how='outer', lsuffix='_wo', rsuffix='_ro')
    df = df.reset_index()


    df_piv = df.pivot(index='n_worker_per_mw', columns='num_clients', values=['rt_ilaw_diff_wo','rt_ilaw_diff_ro'])

    df_piv = df_piv.fillna('-')

    return df_piv, df

def interactive_law_mget_mix(df_client, df_mw):

    key_col = ['workload', 'n_worker_per_mw', 'num_clients', 'multi_get_size']
    cols = ['workload', 'n_worker_per_mw', 'num_clients', 'multi_get_size', 'throughput_rep_mean_mw','throughput_rep_mean_client', 'rt_rep_mean_mw', 'rt_rep_mean_client', 'client_thinktime_mw', 'client_thinktime_client']

    df = df_mw.set_index(key_col).join(df_client.set_index(key_col),lsuffix='_mw', rsuffix='_client')
    df = df.reset_index()

    df = df[cols]
    df = df.rename(columns={'throughput_rep_mean_mw': 'tp_mw',
                            'throughput_rep_mean_client': 'tp_client',
                            'rt_rep_mean_mw':'rt_mw',
                            'rt_rep_mean_client':'rt_client'
                           })



    df['rt_ilaw'] = df.apply(lambda row: row['num_clients']/row['tp_mw']*1000 - row['client_thinktime_client'],axis=1)
    df['tp_ilaw'] = df.apply(lambda row: row['num_clients']/(row['rt_client'] + row['client_thinktime_client'])*1000,axis=1)

    df['rt_ilaw_diff'] = df.apply(lambda row: round(row['rt_ilaw']-row['rt_client'],1),axis=1)
    df['tp_ilaw_diff'] = df.apply(lambda row: round(abs(row['tp_ilaw']-row['tp_mw']),0),axis=1)

    df.loc[df['rt_ilaw_diff']==-0.0, 'rt_ilaw_diff'] = 0.0


    df_piv = df.pivot(index='n_worker_per_mw', columns='multi_get_size', values=['rt_ilaw_diff'])

    df_piv = df_piv.fillna('-')

    return df_piv, df

def interactive_law_2k_mix(df_client, df_mw, num_clients):

    key_col = ['workload', 'n_server_vm', 'n_middleware_vm', 'n_worker_per_mw']
    cols = ['rt_y_avg_mw','rt_y_avg_client','tp_y_avg_mw','tp_y_avg_client']

    df = df_mw.set_index(key_col).join(df_client.set_index(key_col),lsuffix='_mw', rsuffix='_client')
    df = df.reset_index()

    df = df[cols]

    df['i'] = np.arange(1, df.shape[0]+1)
    display(df)

    df['idx']="2k"

    df['rt_ilaw'] = df.apply(lambda row: num_clients/row['tp_y_avg_mw']*1000 ,axis=1)
    df['tp_ilaw'] = df.apply(lambda row: num_clients/(row['rt_y_avg_client'])*1000,axis=1)

    df['rt_ilaw_diff'] = df.apply(lambda row: round(row['rt_ilaw']-row['rt_y_avg_client'],1),axis=1)
    df['tp_ilaw_diff'] = df.apply(lambda row: round(abs(row['tp_ilaw']-row['tp_y_avg_mw']),0),axis=1)

    df.loc[df['rt_ilaw_diff']==-0.0, 'rt_ilaw_diff'] = 0.0


    df_piv = df.pivot(index='idx', columns='i', values=['rt_ilaw_diff'])

    df_piv = df_piv.fillna('-')

    return df_piv, df

def interactive_law_client(df_client, df_mw):

    key_col = ['workload', 'n_worker_per_mw', 'num_clients']
    cols = ['workload', 'n_worker_per_mw', 'num_clients', 'throughput_rep_mean_mw','throughput_rep_mean_client', 'rt_rep_mean_mw', 'rt_rep_mean_client']

    df = df_mw.set_index(key_col).join(df_client.set_index(key_col),lsuffix='_mw', rsuffix='_client')
    df = df.reset_index()
    df = df[cols]
    df = df.rename(columns={'throughput_rep_mean_mw': 'tp_mw',
                            'throughput_rep_mean_client': 'tp_client',
                            'rt_rep_mean_mw':'rt_mw',
                            'rt_rep_mean_client':'rt_client'
                           })

    df['rt_ilaw'] = df.apply(lambda row: row['num_clients']/row['tp_client']*1000,axis=1)
    df['tp_ilaw'] = df.apply(lambda row: row['num_clients']/row['rt_client']*1000,axis=1)

    df['rt_ilaw_diff'] = df.apply(lambda row: round(row['rt_ilaw']-row['rt_client'],1),axis=1)
    df['tp_ilaw_diff'] = df.apply(lambda row: round(abs(row['tp_ilaw']-row['tp_client']),0),axis=1)

    df.loc[df['rt_ilaw_diff']==-0.0, 'rt_ilaw_diff'] = 0.0

    df = df[df['workload']=='write-only'].set_index(['n_worker_per_mw', 'num_clients']).join(df[df['workload']=='read-only'].set_index(['n_worker_per_mw', 'num_clients']),how='outer', lsuffix='_wo', rsuffix='_ro')
    df = df.reset_index()


    df_piv = df.pivot(index='n_worker_per_mw', columns='num_clients', values=['rt_ilaw_diff_wo','rt_ilaw_diff_ro'])

    df_piv = df_piv.fillna('-')

    return df_piv, df


def table(df_piv, wo_col_count, ro_col_count):

    num_workers = df_piv.unstack().reset_index()['num_clients'].unique()

    if wo_col_count > 0 and ro_col_count > 0:
        header = f"\\begin{{tabular}}{{|cr|*{{{wo_col_count}}}{{r}}|*{{{ro_col_count}}}{{r}}|}}"
        header += f"\n\\cline{{3-{2+wo_col_count+ro_col_count}}}"
        header += f"\n\\multicolumn{{2}}{{c|}}{{}} & \\multicolumn{{{wo_col_count}}}{{c|}}{{number of clients}} & \\multicolumn{{{ro_col_count}}}{{c|}}{{number of clients}} \\Tstrut\\\\"

        wo_num_workers = " & ".join(map(str, num_workers[0:wo_col_count]))
        ro_num_workers = " & ".join(map(str, num_workers[0:ro_col_count]))

        header += f"\n\\multicolumn{{2}}{{c|}}{{}} & {wo_num_workers} & {ro_num_workers} \\\\"
        header += "\n\\hline"

        footer = f"& & \\multicolumn{{{wo_col_count}}}{{c|}}{{in milliseconds}} & \\multicolumn{{{ro_col_count}}}{{c|}}{{in milliseconds}}\\\\"
        footer += f"\n\\hline\n\\multicolumn{{2}}{{c}}{{}} & \\multicolumn{{{wo_col_count}}}{{c}}{{write-only}} & \\multicolumn{{{ro_col_count}}}{{c}}{{read-only}} \\Tstrut\\\\ \n\\end{{tabular}}"

    elif wo_col_count > 0:
        header = f"\\begin{{tabular}}{{|cr|*{{{wo_col_count}}}{{r}}|}}"
        header += f"\n\\cline{{3-{2+wo_col_count}}}"
        header += f"\n\\multicolumn{{2}}{{c|}}{{}} & \\multicolumn{{{wo_col_count}}}{{c|}}{{number of clients}} \\Tstrut\\\\"

        wo_num_workers = " & ".join(map(str, num_workers[0:wo_col_count]))

        header += f"\n\\multicolumn{{2}}{{c|}}{{}} & {wo_num_workers} \\\\"
        header += "\n\\hline"

        footer = f"& & \\multicolumn{{{wo_col_count}}}{{c|}}{{in milliseconds}} \\\\"
        footer += f"\n\\hline\n\\multicolumn{{2}}{{c}}{{}} & \\multicolumn{{{wo_col_count}}}{{c}}{{write-only}} \\Tstrut\\\\ \n\\end{{tabular}}"

    else:
        raise ValueError("Not Implemented Yet")


    x = df_piv.apply(lambda row: f"& {row.name} & " + " & ".join(map(str, np.concatenate((row['rt_ilaw_diff_wo'][0:wo_col_count], row['rt_ilaw_diff_ro'][0:ro_col_count]), axis=0))) + " \\\\", axis=1)

    rows = x.values

    worker_label = "\\parbox[t]{2mm}{\\multirow{4}{*}{\\rotatebox[origin=c]{90}{worker}}} "
    rows[0] = worker_label + rows[0].replace(" \\\\", "\\Tstrut\\\\")

    table = header

    for row in rows:
        table += f"\n{row}"
    table += f"\n{footer}"

    return table

def table_mget(df_piv, n_mget, desc):

    multi_get_sizes = df_piv.unstack().reset_index()['multi_get_size'].unique()

    header = f"\\begin{{tabular}}{{|c|*{{{n_mget}}}{{r}}|}}"
    header += f"\n\\cline{{2-{1+n_mget}}}"
    header += f"\n\\multicolumn{{1}}{{c|}}{{}} & \\multicolumn{{{n_mget}}}{{c|}}{{multi-get size}} \\Tstrut\\\\"

    multi_get_sizes = " & ".join(map(str, multi_get_sizes[0:n_mget]))

    header += f"\n\\multicolumn{{1}}{{c|}}{{}} & {multi_get_sizes} \\Tstrut\\\\"
    header += "\n\\hline"

    footer = f"& \\multicolumn{{{n_mget}}}{{c|}}{{in milliseconds}} \\\\\n\\hline "
    footer += f"\n\\end{{tabular}}"


    x = df_piv.apply(lambda row: f"{desc} & " + " & ".join(map(str, row['rt_ilaw_diff'][0:n_mget])) + " \\Tstrut\\\\", axis=1)

    rows = x.values

    #label = f"\\parbox[t]{{2mm}}{{\\multirow{{4}}{{*}}{{{desc}}}} "
    #rows[0] = label + rows[0].replace(" \\\\", "\\Tstrut\\\\")

    table = header

    for row in rows:
        table += f"\n{row}"
    table += f"\n{footer}"

    return table
