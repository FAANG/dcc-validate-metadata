import json
import requests
import pandas as pd
from collections import Counter
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.constants import \
    BE_SVC, PROJECTS

es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, \
                    http_auth=(settings.ES_USER, settings.ES_PASSWORD), \
                    use_ssl=True, verify_certs=True)

def type_count(data):
    data = data.split(', ')
    data = dict(Counter(data))
    return data

def convertToListOfDict(data):
    l = []
    for k in data:
        obj = {
            'type': k,
            'count': data[k]
        }
        l.append(obj)
    return l

def comma_separated_combine(data):
    values = []
    for i in data:
        i_list = i.split(', ')
        values = values + i_list
    return ', '.join(values)

def get_species_for_project(project):
    project_filter = json.dumps({
        'secondaryProject': [project]
    })
    url = f'{BE_SVC}/data/organism/_search/?size=10000&filters={project_filter}'
    data = requests.get(url).json()['hits']['hits']
    species = filter(lambda y: y, set(map(lambda x: x['_source']['organism']['text'], data)))
    species = ', '.join(species)
    return species

@app.task
def update_ontology_summary():
    url = f'{BE_SVC}/data/ontologies_test/_search/?size=10000'
    resultset = requests.get(url).json()['hits']['hits']
    ontologies = map(lambda ontology: ontology['_source'], resultset)
    df = pd.DataFrame.from_dict(ontologies)[['projects', 'type', 'term']]
    df['type'] = [', '.join(map(str, l)) for l in df['type']]
    df = df.explode('projects')
    df = df.loc[df['projects'].isin(PROJECTS)]
    df = df.groupby(['projects']).agg({
        'type': comma_separated_combine,
        'term': 'count'
    }).reset_index()
    df['type'] = df['type'].apply(type_count)
    # get project-specific species from organisms index
    species = {}
    for project in PROJECTS:
        if project in df['projects'].values:
            species[get_species_for_project(project)] = project
    df['species'] = species
    # get existing summary statistics
    url = f"{BE_SVC}/data/summary_ontologies_test/_search/?size=10"
    res_data = requests.get(url).json()['hits']['hits']
    validated_counts = {}
    for record in res_data:
        validated_counts[record['_id']] = record['_source']['activity']['validated_count']
    # generate update payload
    for index, row in df.iterrows():
        updated_project_stats = {
            'project': row['projects'],
            'species': row['species'],
            'type_counts': convertToListOfDict(row['type']),
            'activity': {
                'created_edited_count': row['term'],
                'validated_count': validated_counts[row['projects']] if row['projects'] in validated_counts else 0
            }
        }
        es.index(index='summary_ontologies_test', id=updated_project_stats['project'], body=updated_project_stats)
    return "Success"