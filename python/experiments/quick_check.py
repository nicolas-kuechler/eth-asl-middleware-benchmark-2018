import pymongo, logging

from configs import config
from bson.objectid import ObjectId

log = logging.getLogger('asl')

def throughput_check(suite, result_ids, threshold=1300):

    client = pymongo.MongoClient(f"mongodb://{config.MONGODB_IP}:{config.MONGODB_PORT}/")
    db = client[suite]
    results = db.collection['results']

    pipeline = _build_pipeline(result_ids)
    cursor = results.aggregate(pipeline, allowDiskUse=True)

    pass_check = True
    for c in cursor:
        logging.debug(f"throughput check result: {c}")
        if c['throughput_std'] > threshold:
            pass_check = False

    logging.info(f"Pass Throughput Std Dev Test: {pass_check}")
    return pass_check


def _build_pipeline(result_ids):
    stats_window_size = 5.0 #seconds
    start_slot = 1
    end_slot = 13
    pipeline = [
        {"$match": {"_id":{ "$in": result_ids}}},
        {"$unwind": "$mw_stats"},
        {"$project": {"mw_stats.rt_hist":0}},
        {"$unwind": "$mw_stats.op"},
        {"$match": {"mw_stats.op.slot": {"$gte": start_slot, "$lte": end_slot}}},
        {"$group": {"_id" : {   "res_id":"$_id",
                                "slot":"$mw_stats.op.slot",
                                "rep":"$repetition",
                                "op_type": "$mw_stats.op.op_type"},
                   "sum_rt_count" : {"$sum": "$mw_stats.op.rt_count"},
                   }
        },
        {"$match": {"_id.slot": {"$gte": start_slot, "$lte": end_slot}}},
        {"$addFields": {"throughput": {"$divide" : ["$sum_rt_count", stats_window_size]}}},
        {"$group": {"_id" : {   "res_id": "$_id.res_id",
                                "rep": "$_id.rep",
                                "op_type": "$_id.op_type"},
                   "throughput" : {"$avg": "$throughput"},
                   }
        },
        {"$group": {"_id" : {"op_type": "$_id.op_type"},
                   "throughput_std" : {"$stdDevSamp": "$throughput"},
                   "throughput_avg" : {"$avg": "$throughput"},
                   "throughputs" : {"$push": "$throughput"}
                   }
        }
    ]
    return pipeline

if __name__ == "__main__":
    suite = "base_run"

    client = pymongo.MongoClient(f"mongodb://{config.MONGODB_IP}:{config.MONGODB_PORT}/")
    db = client[suite]
    results = db.collection['results']

    for x in results.find({"exp":"exp32"}):
        if x['exp_config']['n_worker_per_mw'] == 64 and x['exp_config']['n_vc']==16:
            print(f"{x['_id']}     rep={x['repetition']}   n_vc={x['exp_config']['n_vc']}    w={x['exp_config']['n_worker_per_mw']}")

    result_ids = [ObjectId("5bdd3bff7566de113c87e495"), ObjectId("5bdd3c627566de113c87e497"), ObjectId("5bdd3cc67566de113c87e499")]
    pass_check = throughput_check(suite=suite, result_ids=result_ids)
    print(f"Pass Check: {pass_check}")
    assert(not pass_check)


    result_ids = [ObjectId("5bdd40a07566de113c87e4ad"), ObjectId("5bdd41037566de113c87e4af"), ObjectId("5bdd41677566de113c87e4b1")]
    pass_check = throughput_check(suite=suite, result_ids=result_ids)
    print(f"Pass Check: {pass_check}")
    assert(pass_check)
