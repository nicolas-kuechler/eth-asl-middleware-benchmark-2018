
from bson.son import SON
import pandas as pd
import numpy as np

from queries.query_util import df_aggregate, utility, const

def load_df_by_rep(suite,exp):

    results = utility.get_result_collection(suite)
    pipeline = _build_pipeline(exp)
    cursor = results.aggregate(pipeline, allowDiskUse=True)
    df =  pd.DataFrame(list(cursor))

    config_cols = ["rep", "num_clients", "data_origin", "n_server_vm", "n_client_vm", "n_vc", "workload", "workload_ratio","op_type",
        "multi_get_behaviour", "multi_get_size", "n_worker_per_mw", "n_middleware_vm", "n_instances_mt_per_machine", "n_threads_per_mt_instance",
        "write_bandwidth_limit","bandwidth_limit_write_throughput", "read_bandwidth_limit", "bandwidth_limit_read_throughput", "client_rtt", "server_rtt"]

    value_cols = ["throughput_mean", "throughput_std", "rt_mean", "rt_std", "throughputset_mean", "throughputset_std", "rtset_mean", "rtset_std", "throughputget_mean", "throughputget_std", "rtget_mean", "rtget_std"]
    df = df.set_index(config_cols, drop=False)

    return df, config_cols, value_cols


def load_df(suite, exp):

    df, config_cols, value_cols = load_df_by_rep(suite,exp)

    print(f"Client: {df[df['throughput_mean']==0].shape[0]} repetitions don't have throughput")

    df = df[df["throughput_mean"]!=0]
    df["tp_cov"] = df.apply(lambda row: row['throughput_std'] / row['throughput_mean'], axis=1)

    #df = df[df["tp_cov"]<const.cov_threshold]

    df_rep, config_cols_rep, value_cols_rep = df_aggregate.aggregate_repetitions(df, config_cols=config_cols, value_cols=value_cols)

    return df_rep.reset_index()



def _build_pipeline(exp):
    stats_window_size = 5.0 #seconds
    value_size = 4096 # bytes
    value_size_mbit = value_size / 125000.0

    exp_ext = exp + "ext"

    pipeline = [
        {"$match": {"$or": [ {"exp": exp }, {"exp": exp_ext} ]}},
        {"$addFields":{"num_clients": {"$multiply": ["$exp_config.n_client",
                                                     "$exp_config.n_instances_mt_per_machine",
                                                     "$exp_config.n_threads_per_mt_instance",
                                                     "$exp_config.n_vc"
                                                    ]},
                        "workload": {"$switch": {"branches": [  { "case": {"$eq":["$exp_config.workload_ratio", "1:0"]}, "then": "write-only" },
                                                                { "case": {"$eq":["$exp_config.workload_ratio", "0:1"]}, "then": "read-only" },],
                                                "default": "read-write"}},
                        "from_client_netstat": {"$reduce": {
                                                    "input": {"$filter":{"input": "$network_stats", "as": "e", "cond": {"$eq":[{ "$substrBytes": ["$$e.from", 0, 1]},"C"]}}},
                                                    "initialValue":{"bandwidth": 0.0,
                                                                     "rtt": 0.0,
                                                                     "count":0},
                                                    "in":{ "bandwidth": {"$add" : ["$$value.bandwidth", "$$this.bandwidth"]},
                                                            "rtt": {"$add" : ["$$value.rtt", {"$toDouble":"$$this.rtt"}]}, # TODO [nku] remove double conversion
                                                            "count": {"$add": ["$$value.count", 1]}}
                                                            }
                                                },
                        "to_server_netstat": {"$reduce": {
                                                    "input": {"$filter":{"input": "$network_stats", "as": "e", "cond": {"$eq":[{ "$substrBytes": ["$$e.to", 0, 1]},"S"]}}},
                                                    "initialValue":{"bandwidth": 0.0,
                                                                     "rtt": 0.0,
                                                                     "count":0},
                                                    "in": { "bandwidth": {"$add" : ["$$value.bandwidth", "$$this.bandwidth"]},
                                                            "rtt": {"$add" : ["$$value.rtt", {"$toDouble":"$$this.rtt"}]}, # TODO [nku] remove double conversion
                                                            "count": {"$add": ["$$value.count", 1]}}
                                                    }
                                                },
                        "to_client_netstat": {"$reduce": {
                                                    "input": {"$filter":{"input": "$network_stats", "as": "e", "cond": {"$eq":[{ "$substrBytes": ["$$e.to", 0, 1]},"C"]}}},
                                                    "initialValue":{"bandwidth": 0.0,
                                                                     "rtt": 0.0,
                                                                     "count":0},
                                                    "in":{ "bandwidth": {"$add" : ["$$value.bandwidth", "$$this.bandwidth"]},
                                                            "rtt": {"$add" : ["$$value.rtt", {"$toDouble":"$$this.rtt"}]}, # TODO [nku] remove double conversion
                                                            "count": {"$add": ["$$value.count", 1]}}
                                                    }
                                                },
                        "from_server_netstat": {"$reduce": {
                                                    "input": {"$filter":{"input": "$network_stats", "as": "e", "cond": {"$eq":[{ "$substrBytes": ["$$e.from", 0, 1]}, "S"]}}},
                                                    "initialValue":{"bandwidth": 0.0,
                                                                     "rtt": 0.0,
                                                                     "count":0},
                                                    "in":{ "bandwidth": {"$add" : ["$$value.bandwidth", "$$this.bandwidth"]},
                                                            "rtt": {"$add" : ["$$value.rtt", {"$toDouble":"$$this.rtt"}]}, # TODO [nku] remove double conversion
                                                            "count": {"$add": ["$$value.count", 1]}}
                                                }},
                      }
        },
        {"$addFields":{"write_bandwidth_limit": {"$min":["$from_client_netstat.bandwidth", "$to_server_netstat.bandwidth"]},
                       "read_bandwidth_limit":  {"$min":["$from_server_netstat.bandwidth", "$to_client_netstat.bandwidth"]},
                       "client_rtt":{"$divide":["$from_client_netstat.rtt", "$from_client_netstat.count"]},
                       "server_rtt":{"$divide":["$to_server_netstat.rtt", "$to_server_netstat.count"]}
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

                   "write_bandwidth_limit":{"$avg":"$write_bandwidth_limit"}, # should all be the same anyway
                   "read_bandwidth_limit":{"$avg":"$read_bandwidth_limit"}, # should all be the same anyway
                   "client_rtt":{"$avg":"$client_rtt"}, # should all be the same anyway
                   "server_rtt":{"$avg":"$server_rtt"}, # should all be the same anyway
                   "run_count" : {"$sum" :  1},
                   "throughput" : {"$sum": "$client_stats.totals.Ops/sec"},
                   "throughput_std" : {"$stdDevSamp": "$client_stats.totals.Ops/sec"},
                   "rt" : {"$avg": "$client_stats.totals.Latency"},
                   "rt_std" : {"$stdDevSamp": "$client_stats.totals.Latency"},
                   "throughput_set" : {"$sum": "$client_stats.sets.Ops/sec"},
                   "throughput_set_std" : {"$stdDevSamp": "$client_stats.sets.Ops/sec"},
                   "rt_set" : {"$avg": "$client_stats.sets.Latency"},
                   "rt_set_std" : {"$stdDevSamp": "$client_stats.sets.Latency"},
                   "throughput_get" : {"$sum": "$client_stats.gets.Ops/sec"},
                   "throughput_get_std" : {"$stdDevSamp": "$client_stats.gets.Ops/sec"},
                   "rt_get" : {"$avg": "$client_stats.gets.Latency"},
                   "rt_get_std" : {"$stdDevSamp": "$client_stats.gets.Latency"},
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
                        "op_type": {"$switch": {"branches": [  { "case": {"$eq":["$_id.workload", "write-only"]}, "then": "set" },
                                                                { "case": {"$eq":["$_id.workload", "read-only"]}, "then": "get" },],
                                                "default": "-"}},
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
                        "throughputset_mean":"$throughput_set",
                        "throughputset_std":"$throughput_set_std",
                        "throughputget_mean":"$throughput_get",
                        "throughputget_std":"$throughput_get_std",
                        "rt_mean" : "$rt",
                        "rt_std": "$rt_std",
                        "rtset_mean" : "$rt_set",
                        "rtset_std": "$rt_set_std",
                        "rtget_mean" : "$rt_get",
                        "rtget_std": "$rt_get_std",
                        "read_bandwidth_limit": { "$cond": { "if": { "$eq": ["$read_bandwidth_limit", None]}, "then": "-", "else": "$read_bandwidth_limit" }},
                        "bandwidth_limit_read_throughput": { "$cond": { "if": { "$eq": ["$read_bandwidth_limit", None]}, "then": "-", "else": {"$divide":["$read_bandwidth_limit", value_size_mbit]}}},
                        "write_bandwidth_limit":{ "$cond": { "if": { "$eq": ["$write_bandwidth_limit", None]}, "then": "-", "else": "$write_bandwidth_limit" }},
                        "bandwidth_limit_write_throughput": { "$cond": { "if": { "$eq": ["$write_bandwidth_limit", None]}, "then": "-", "else": {"$divide":["$write_bandwidth_limit", value_size_mbit]}}},
                        "client_rtt":{ "$cond": { "if": { "$eq": ["$client_rtt", None]}, "then": "-", "else": "$client_rtt" }},
                        "server_rtt":{ "$cond": { "if": { "$eq": ["$server_rtt", None]}, "then": "-", "else": "$server_rtt" }},
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
