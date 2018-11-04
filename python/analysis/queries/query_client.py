
from bson.son import SON
import pandas as pd
import numpy as np

from queries.query_util import df_aggregate, utility

def load_df(suite, exp):

    results = utility.get_result_collection(suite)

    pipeline = _build_pipeline(exp)

    # create dataframe
    cursor = results.aggregate(pipeline, allowDiskUse=True)

    df =  pd.DataFrame(list(cursor))

    config_cols = ["rep", "num_clients", "data_origin", "n_server_vm", "n_client_vm", "n_vc", "workload", "workload_ratio",
        "multi_get_behaviour", "multi_get_size", "n_worker_per_mw", "n_middleware_vm", "n_instances_mt_per_machine", "n_threads_per_mt_instance"]
    value_cols = ["throughput_mean", "throughput_std", "rt_mean", "rt_std"]
    df = df.set_index(config_cols, drop=False)

    df_rep, config_cols_rep, value_cols_rep = df_aggregate.aggregate_repetitions(df, config_cols=config_cols, value_cols=value_cols)

    return df_rep.reset_index()



def _build_pipeline(exp):
    stats_window_size = 5.0 #seconds

    pipeline = [
        {"$match": {"exp": exp}},
        {"$addFields":{"num_clients": {"$multiply": ["$exp_config.n_client",
                                                     "$exp_config.n_instances_mt_per_machine",
                                                     "$exp_config.n_threads_per_mt_instance",
                                                     "$exp_config.n_vc"
                                                    ]},
                        "workload": {"$switch": {"branches": [  { "case": {"$eq":["$exp_config.workload_ratio", "1:0"]}, "then": "write-only" },
                                                                { "case": {"$eq":["$exp_config.workload_ratio", "0:1"]}, "then": "read-only" },],
                                                "default": "read-write"}}
                      }
        },
        {"$project": {"mw_stats":0}},
        {"$unwind":"$client_stats"},
        {"$group": {"_id" : {"rep":"$repetition",
                             "num_clients": "$num_clients",
                             "n_server": "$exp_config.n_server",
                             "n_client": "$exp_config.n_client",
                             "n_vc": "$exp_config.n_vc",
                             "workload": "$workload",
                             "workload_ratio": "$exp_config.workload_ratio",
                             "multi_get_behaviour":"$exp_config.multi_get_behaviour",
                             "multi_get_size":"$exp_config.multi_get_size",
                             "n_worker_per_mw": "$exp_config.n_worker_per_mw",
                             "n_middleware" : "$exp_config.n_middleware",
                             "n_instances_mt_per_machine":"$exp_config.n_instances_mt_per_machine",
                             "n_threads_per_mt_instance":"$exp_config.n_threads_per_mt_instance"},
                   "run_count" : {"$sum" :  1},
                   "throughput" : {"$sum": "$client_stats.totals.Ops/sec"},
                   "throughput_std" : {"$stdDevSamp": "$client_stats.totals.Ops/sec"},
                   "rt" : {"$avg": "$client_stats.totals.Latency"},
                   "rt_std" : {"$stdDevSamp": "$client_stats.totals.Latency"},
                   }
        },
        {"$addFields":{"data_origin": "client"}},
        {"$project": {"_id": 0,
                        "rep":"$_id.rep",
                        "num_clients": "$_id.num_clients",
                        "n_server_vm": "$_id.n_server",
                        "n_client_vm": "$_id.n_client",
                        "n_vc": "$_id.n_vc",
                        "workload": "$_id.workload",
                        "workload_ratio": "$_id.workload_ratio",
                        "multi_get_behaviour": { "$cond": { "if": { "$eq": ["$_id.multi_get_behaviour", None]}, "then": "-", "else": "$_id.multi_get_behaviour" }},
                        "multi_get_size": { "$cond": { "if": { "$eq": ["$_id.multi_get_size", None]}, "then": "-", "else": "$_id.multi_get_size" }},
                        "n_worker_per_mw": "$_id.n_worker_per_mw",
                        "n_middleware_vm" : "$_id.n_middleware",
                        "n_instances_mt_per_machine":"$_id.n_instances_mt_per_machine",
                        "n_threads_per_mt_instance":"$_id.n_threads_per_mt_instance",
                        "run_count": 1,
                        "data_origin": 1,
                        "throughput_mean":"$throughput",
                        "throughput_std":"$throughput_std",
                        "rt_mean" : "$rt",
                        "rt_std": "$rt_std"
                     }
        },
        {"$sort":SON([("n_client_vm",1),
                        ("n_middleware_vm",1),
                        ("n_server_vm",1),
                        ("workload",1),
                        ("multi_get_behaviour",1),
                        ("multi_get_size",1),
                        ("n_worker_per_mw",1),
                        ("num_clients", 1),
                        ("rep",1)
                        ])},
    ]

    return pipeline
