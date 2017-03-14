
from flask import Flask, request
from pymongo import MongoClient
from utils import *

application = Flask(__name__)

@application.route("/jobs")
def get_all_jobs():
    db_server = MongoClient("/tmp/mongodb-27017.sock")
    db_jobs = db_server["jobs"]
    dirty_jobs_collection = db_jobs["dirty_jobs"]
    jobs_to_return_collection = db_jobs["jobs_to_return"]
    # TODO - Query some API for URLS instead of hardcoding them
    urls = {
        "sfo": "http://rein1-sfo.reinproject.org:2016/query?owner={0}&query={1}&testnet={2}",
        "ams": "http://rein2-ams.reinproject.org:2016/query?owner={0}&query={1}&testnet={2}"
    }
    jobs = []
    jobs_to_return_up_to_date = 0

    # Only a registered user can get jobs.
    query = "jobs"
    testnet = 0
    owner = request.args.get("maddr")
    if owner == None:
        return json.dumps({"result": "error"})

    # Check if dirty_jobs is up to date. If not, insert.
    for url in urls:
        server_dirty_jobs = requests.get(urls[url].format(owner, query, testnet)).text
        db_dirty_jobs = dirty_jobs_collection.find_one({"region": url}, {"_id": False})
        if not db_dirty_jobs:
            dirty_jobs_collection.insert_one({"contents": server_dirty_jobs, "region": url})
        elif db_dirty_jobs["contents"] != server_dirty_jobs:
            dirty_jobs_collection.update_one({"region": url}, {"$set": {"contents": server_dirty_jobs}})
        else:
            jobs_to_return_up_to_date += 1

    # Update jobs_to_return if necessary.
    if jobs_to_return_up_to_date < len(urls):
        jobs_to_return_collection.drop()
        db_dirty_jobs = dirty_jobs_collection.find({}, {"_id": False})
        for dirty_jobs in db_dirty_jobs:
            jobs += filter_and_parse_valid_sigs(json.loads(dirty_jobs["contents"])['jobs'])
        unique_jobs = unique(get_live_jobs(jobs), "Job ID")
        for job in unique_jobs:
            jobs_to_return_collection.insert(job)

    jobs_to_return = [job for job in jobs_to_return_collection.find({}, {"_id": False})]
    return json.dumps({"result": "success", "jobs": jobs_to_return})

if __name__ == "__main__":
    application.run()