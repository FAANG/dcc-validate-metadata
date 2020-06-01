import requests
import aiohttp
import asyncio


def parse_record(record):
    """
    This function will fetch term_ids from records
    :param record: record to parse
    :return: term_id
    """
    if isinstance(record, dict):
        if 'text' in record and 'term' in record:
            return record['term']
    elif isinstance(record, list):
        for sub_record in record:
            if 'text' in sub_record and 'term' in sub_record:
                return sub_record['term']


def collect_ids(records, core_name=None, module_name=None):
    """
    Main function that will collect all ids and start ids fetching
    :param records: records to fetch
    :param core_name: name of the core fields
    :param module_name: name of the module fields
    :return: dict with term_ids as keys and ols results as values
    """
    ids = set()
    for record in records:
        if core_name is not None:
            for _, value in record[core_name].items():
                ids.add(parse_record(value))
        if module_name is not None:
            for _, value in record[module_name].items():
                ids.add(parse_record(value))
        for _, value in record.items():
            ids.add(parse_record(value))
        for _, value in record['custom'].items():
            ids.add(parse_record(value))
    results = fetch_text_for_ids(ids)
    return results


def fetch_text_for_ids(ids):
    """
    This function will start async calls to OLS to get results for term_ids
    :param ids: ids to call
    :return: dict with term_ids as keys and ols results as values
    """
    results = dict()
    asyncio.new_event_loop().run_until_complete(fetch_all_terms(ids, results))
    # Not all ids can get through OLS because of bandwidth, so do sync calls
    if len(results) < len(ids):
        for my_id in ids:
            if my_id not in results:
                results[my_id] = requests.get(
                    f"http://www.ebi.ac.uk/ols/api/search?q={my_id}"
                ).json()['response']['docs']
    return results


async def fetch_all_terms(ids, results_to_return):
    """
    This function will create tasks for ols calls
    :param ids: ids to fetch from ols
    :param results_to_return: holder for results
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for my_id in ids:
            task = asyncio.ensure_future(fetch_term(session, my_id,
                                                    results_to_return))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


async def fetch_term(session, my_id, results_to_return):
    """
    This function will create task to call my_id from OLS
    :param session: session to work with
    :param my_id: term_id to check
    :param results_to_return: json structure to parse
    """
    url = f"http://www.ebi.ac.uk/ols/api/search?q={my_id}&rows=100"
    async with session.get(url) as response:
        results = await response.json()
        if results and 'response' in results and 'docs' in results['response']:
            results_to_return[my_id] = results['response']['docs']
