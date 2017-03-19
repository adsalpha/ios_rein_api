# Portions of this code was copied from https://github.com/ReinProject/python-rein/
# This file is subject to the same license terms as the files the code was copied from.
#
# (c) Alexander Dushkin 2017
# (c) ReinProject 2017

import re, requests, json, time
from bitcoin.signmessage import BitcoinMessage, VerifyMessage

SECONDS_IN_A_DAY = 86400
FIELDS_TO_RETURN = {"name", "_id", "tags", "details", "expiresAt", "creator",
                    "creatorContact", "mediator", "mediatorContact"}

def compute_expiration_time(time_created, lifetime_in_days):
    return time_created + lifetime_in_days * SECONDS_IN_A_DAY

def get_modified_job(job, expiration_time):
    job["name"] = job.pop("Job name")
    job["_id"] = job.pop("Job ID")
    job["tags"] = job.pop("Tags")
    job["details"] = re.search(r"(?<=Description: ).*?(?=\nBlock hash:)", job["original"], re.DOTALL).group()
    job["expiresAt"] = expiration_time
    job["creator"] = job.pop("Job Creator")
    job["creatorContact"] = job.pop("Job creator contact")
    job["mediator"] = job.pop("Mediator")
    job["mediatorContact"] = job.pop("Mediator contact")
    modified_job = {}
    for key in job:
        if key in FIELDS_TO_RETURN:
            modified_job[key] = job[key]
    return modified_job

def get_live_jobs(jobs):
    """
    Filter out valid jobs.
    For those which are, adjust their contents to be OK to return with the API.

    :param jobs: Jobs that should be filtered.
    :return: A list of jobs.
    """
    live = []
    if len(jobs):
        for job in jobs:
            try:
                block_hash = job["Block hash"]
                lifetime_in_days = int(job["Expiration (days)"])
                time_created = int(job["Time"])
            except KeyError:
                continue
            block_time = get_block_time(block_hash)
            if block_time == time_created:
                expiration_time = compute_expiration_time(time_created, lifetime_in_days)
                if expiration_time > int(time.time()):
                    live.append(get_modified_job(job, expiration_time))
    return live

def filter_and_parse_valid_sigs(docs, expected_field=None):
    valid = []
    fails = 0
    for m in docs:
        data = verify_sig(m)
        data['original'] = m
        if expected_field:
            if data['valid'] and expected_field in data:
                valid.append(data)
            else:
                fails += 1
        else:
            if data['valid']:
                valid.append(data)
            else:
                fails += 1
    return valid

def verify_sig(sig):
    '''The base function for verifying an ASCII-armored signature.'''
    sig_info = parse_sig(sig)
    if sig_info:
        message = strip_armor(sig)
        valid = verify(
            sig_info['signature_address'],
            message,
            sig_info['signature']
        )
    else:
        valid = False
    if sig_info:
        sig_info['valid'] = valid
    else:
        sig_info = {'valid': False}
    return sig_info

def parse_sig(sig):
    '''
    Takes an ASCII-armored signature and returns a dictionary of its info.
    Returns the signature string, the signing key, and all of the information
    assigned within the message, for example:
       parse_sig(sig)['Name/handle'] === "David Sterry"
    '''
    ret = {}
    m = re.search('\n(Rein .*)\n', sig)
    if m:
        ret['Title'] = m.group(1)
    matches = re.finditer("(.+?):\s(.+)\n", sig)
    for match in matches:
        ret[match.group(1)] = match.group(2)
    m = re.search(
        "-{5}BEGIN SIGNATURE-{5}\n([A-z\d=+/]+)\n([A-z\d=+/]+)"
        "\n-{5}END BITCOIN SIGNED MESSAGE-{5}",
        sig
    )
    if m:
        ret['signature_address'] = m.group(1)
        ret['signature'] = m.group(2)
    else:
        return False
    return ret

def strip_armor(sig, dash_space=False):
    """
    Removes ASCII-armor from a signed message by default exlcudes 'dash-space' headers.
    :param sig:
    :param dash_space:
    :return:
    """
    sig = sig.replace('- ----', '-' * 5) if dash_space else sig
    sig = re.sub("-{5}BEGIN BITCOIN SIGNED MESSAGE-{5}", "", sig)
    sig = re.sub(
        "\n+-{5}BEGIN SIGNATURE-{5}[\n\dA-z+=/]+-{5}END BITCOIN SIGNED MESSAGE-{5}\n*",
        "",
        sig
    )
    sig = re.sub("^\n", "", sig)
    sig = re.sub("\n\n", "", sig)
    return sig

def verify(address, message, signature):
    message = BitcoinMessage(message)
    return VerifyMessage(address, message, signature)

def get_block_time(block_hash):
    """
    Query blockexplorer.com for the block time. Receives a large JSON in process, might take time to return.

    :param block_hash: The block hash Blockexplorer should be queried with.
    :return: UNIX time when the block was mined.
    """
    api_url = "https://blockexplorer.com/api/block/{0}"
    block_data = json.loads(requests.get(api_url.format(block_hash)).text)
    block_time = block_data["time"]
    return int(block_time)

def unique(the_array, key=None):
    """
    Filter an array of dicts by key. Only lets through dicts that include key.
    """
    unique = []
    values = []
    for element in the_array:

        if key:
            if key in element and element[key] not in values:
                values.append(element[key])
                unique.append(element)
        else:
            if element not in unique:
                unique.append(element)
    return unique
