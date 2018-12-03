

exp21 = {
    "write-only" : [288, 384, 480],
    "read-only" : [288, 384, 480]
}

exp31 = {
    "write-only" : {
        8: [144, 192, 288],
        16:[288],
        32:[288],
        64:[]
    },
    "read-only":{
        8: [192, 288],
        16:[192, 288],
        32:[192, 288],
        64:[192, 288]
    }
}



exp32 = {
    "write-only" : {
        8: [384, 480],
        16:[384, 480],
        32:[384, 480],
        64:[480]
    },
    "read-only" : {
        8: [192, 288],
        16:[192, 288],
        32:[192, 288],
        64:[192, 288]
    }
}

exp41 = {
    "write-only" : {
        8: [480],
        16:[480],
        32:[480],
        64:[480]
    }
}


def filter_df_nc_w(df, filter_dict):

    wo_filter_num_clients = filter_dict['write-only']

    if 'read-only' in filter_dict:
        ro_filter_num_clients = filter_dict['read-only']

        df = df[((df['workload']=='write-only')&(df['n_worker_per_mw']==8) & (~ df['num_clients'].isin(wo_filter_num_clients[8]))) |
                    ((df['workload']=='write-only')&(df['n_worker_per_mw']==16) & (~ df['num_clients'].isin(wo_filter_num_clients[16]))) |
                    ((df['workload']=='write-only')&(df['n_worker_per_mw']==32) & (~ df['num_clients'].isin(wo_filter_num_clients[32]))) |
                    ((df['workload']=='write-only')&(df['n_worker_per_mw']==64) & (~ df['num_clients'].isin(wo_filter_num_clients[64]))) |
                    ((df['workload']=='read-only')&(df['n_worker_per_mw']==8) & (~ df['num_clients'].isin(ro_filter_num_clients[8]))) |
                    ((df['workload']=='read-only')&(df['n_worker_per_mw']==16) & (~ df['num_clients'].isin(ro_filter_num_clients[16]))) |
                    ((df['workload']=='read-only')&(df['n_worker_per_mw']==32) & (~ df['num_clients'].isin(ro_filter_num_clients[32]))) |
                    ((df['workload']=='read-only')&(df['n_worker_per_mw']==64) & (~ df['num_clients'].isin(ro_filter_num_clients[64])))
                  ]
    else:
        df = df[((df['workload']=='write-only')&(df['n_worker_per_mw']==8) & (~ df['num_clients'].isin(wo_filter_num_clients[8]))) |
                    ((df['workload']=='write-only')&(df['n_worker_per_mw']==16) & (~ df['num_clients'].isin(wo_filter_num_clients[16]))) |
                    ((df['workload']=='write-only')&(df['n_worker_per_mw']==32) & (~ df['num_clients'].isin(wo_filter_num_clients[32]))) |
                    ((df['workload']=='write-only')&(df['n_worker_per_mw']==64) & (~ df['num_clients'].isin(wo_filter_num_clients[64])))
                  ]

    return df
