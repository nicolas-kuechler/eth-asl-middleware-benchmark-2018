import pymongo, logging

import const

from configs import config
from bson.objectid import ObjectId

log = logging.getLogger('asl')

def throughput_check(suite, result_ids, threshold=0.05):

    client = pymongo.MongoClient(f"mongodb://{config.MONGODB_IP}:{config.MONGODB_PORT}/")
    db = client[suite]
    results = db.collection['results']

    pipeline = _build_pipeline(result_ids)
    cursor = results.aggregate(pipeline, allowDiskUse=True)

    fail_count = 0
    total_count = 0

    for c in cursor:
        log.debug(f"throughput check result: {c}")

        for cov in c["throughput_slot_covs"]:
            total_count +=1
            if cov > threshold:
                fail_count +=1

        if fail_count == 0 and c["throughput_cov"] > threshold:
            log.debug("failed repetition cov")
            fail_count += 1

    log.info(f"Throughput Check - Fail Count: {fail_count}   Total Count: {total_count}   Success Count: {total_count-fail_count}")
    return  fail_count, total_count


def _build_pipeline(result_ids):
    stats_window_size = 5.0 #seconds
    start_slot =  const.min_slot_inclusive
    end_slot = const.max_slot_inclusive
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
        {"$addFields": {"throughput": {"$divide" : ["$sum_rt_count", stats_window_size]}}},
        {"$group": {"_id" : {   "res_id": "$_id.res_id",
                                "rep": "$_id.rep",
                                "op_type": "$_id.op_type"},
                   "throughput_slot_mean" : {"$avg": "$throughput"},
                   "throughput_slot_std" : {"$stdDevSamp": "$throughput"},
                   }
        },
        {"$group": {"_id" : {"op_type": "$_id.op_type"},
                   "throughput_std" : {"$stdDevSamp": "$throughput_slot_mean"},
                   "throughput_mean" : {"$avg": "$throughput_slot_mean"},
                   "throughput_slot_means" : {"$push": "$throughput_slot_mean"},
                   "throughput_slot_stds" : {"$push": "$throughput_slot_std"},
                   "throughput_slot_covs" : {"$push": { "$cond": [ { "$eq": [ "$throughput_slot_mean", 0 ] }, "N/A", {"$divide":["$throughput_slot_std", "$throughput_slot_mean"]} ] }
                   }
        }},
        {"$match": {"throughput_mean":{"$gt":0}}},
        {"$addFields": {"throughput_cov": {"$divide" : ["$throughput_std", "$throughput_mean"]}}},
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
    fail_count, total_count = throughput_check(suite=suite, result_ids=result_ids)

    print(f"Throughput Check - Fail Count: {fail_count}   Total Count: {total_count}   Success Count: {total_count-fail_count}")
    assert(fail_count==1)

    result_ids = [ObjectId("5bdd40a07566de113c87e4ad"), ObjectId("5bdd41037566de113c87e4af"), ObjectId("5bdd41677566de113c87e4b1")]
    fail_count, total_count = throughput_check(suite=suite, result_ids=result_ids)

    print(f"Throughput Check - Fail Count: {fail_count}   Total Count: {total_count}   Success Count: {total_count-fail_count}")
    assert(fail_count==0)
