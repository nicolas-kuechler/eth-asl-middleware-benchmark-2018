import pymongo


def get_result_collection(suite):
        ip = "localhost"
        port = "27017"
        client = pymongo.MongoClient(f"mongodb://{ip}:{port}/")
        db = client[suite]
        results = db.collection['results']
        return results
