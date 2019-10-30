import requests
import aiohttp
import asyncio


def parse_biosample_results(results, results_to_return, my_id):
    # Collect relationships
    if 'relationships' in results:
        relationships = list()
        for relation in results['relationships']:
            if relation['source'] == my_id and relation['type'] in \
                    ['child of', 'derived from']:
                relationships.append(relation['target'])
        results_to_return[my_id]['relationships'] = relationships
    # Collect material
    if 'characteristics' in results and 'material' in \
            results['characteristics']:
        results_to_return[my_id]['material'] = \
            results['characteristics']['material'][0]['text']
    # Collect organism
    if 'characteristics' in results and 'organism' in \
            results['characteristics']:
        results_to_return[my_id]['organism'] = \
            results['characteristics']['organism'][0]['text']


def fetch_biosample_data_for_ids(ids):
    results = dict()
    asyncio.new_event_loop().run_until_complete(fetch_all_biosamples(ids,
                                                                     results))
    if len(results) < len(ids):
        for my_id in ids:
            if my_id not in results:
                try:
                    response = requests.get(f"https://www.ebi.ac.uk/biosamples"
                                            f"/samples/{my_id}").json()
                    results.setdefault(my_id, dict())
                    parse_biosample_results(response, results, my_id)
                except ValueError:
                    pass
    return results


async def fetch_all_biosamples(ids, results_to_return):
    """
    This function will create tasks for biosample calls
    :param ids: ids to fetch from biosamples
    :param results_to_return: holder for results
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for my_id in ids:
            task = asyncio.ensure_future(fetch_biosample(session, my_id,
                                                         results_to_return))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


async def fetch_biosample(session, my_id, results_to_return):
    """
    This function will create task to call my_id from biosamples
    :param session: session to work with
    :param my_id: term_id to check
    :param results_to_return: json structure to parse
    """
    url = f"https://www.ebi.ac.uk/biosamples/samples/{my_id}"
    async with session.get(url) as response:
        results = await response.json()
        results_to_return.setdefault(my_id, dict())
        parse_biosample_results(results, results_to_return, my_id)
