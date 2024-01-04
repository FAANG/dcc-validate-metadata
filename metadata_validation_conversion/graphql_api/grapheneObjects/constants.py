MAX_FILTER_QUERY_DEPTH = 3

ANALYSIS = 'analysis'
EXPERIMENT = 'experiment'
SPECIMEN = 'specimen'
ORGANISM = 'organism'
ARTICLE = 'article'
DATASET = 'dataset'
FILE = 'file'
PROTOCOL_ANALYSIS = 'protocol_analysis'
PROTOCOL_FILES = 'protocol_files'
PROTOCOL_SAMPLES = 'protocol_samples'

index_mapping = {
    (ANALYSIS, EXPERIMENT): {
        'left_index_key': 'experimentAccessions',
        'right_index_key': 'accession'
    },
    (ANALYSIS, ARTICLE): {
        'type': 2,
        'left_index_key': 'datasetAccession',
        'right_index_key': 'relatedDatasets.accession'
    },
    (ANALYSIS, DATASET): {
        'left_index_key': 'datasetAccession',
        'right_index_key': 'accession'
         },
    (ANALYSIS, SPECIMEN): {
        'left_index_key': 'sampleAccessions',
        'right_index_key': 'biosampleId'
    },

    (ANALYSIS, PROTOCOL_ANALYSIS): {
        'left_index_key': 'analysisProtocol.filename',
        'right_index_key': 'key'
    },

    (ARTICLE, ANALYSIS): {
        'left_index_key': 'relatedDatasets.accession',
        'right_index_key': 'datasetAccession'
    },
    (ARTICLE, DATASET): {
        'left_index_key': 'relatedDatasets.accession',
        'right_index_key': 'accession'
    },
    (ARTICLE, FILE): {
        'left_index_key': '_id',
        'right_index_key': 'publishedArticles.articleId'
    },
    (ARTICLE, SPECIMEN): {
        'left_index_key': '_id',
        'right_index_key': 'publishedArticles.articleId'
    },

    (DATASET, EXPERIMENT): {
        'left_index_key': 'experiment.accession',
        'right_index_key': 'accession'
    },
    (DATASET, ANALYSIS): {
        'left_index_key': 'accession',
        'right_index_key': 'datasetAccession'
    },
    (DATASET, ARTICLE): {
        'left_index_key': 'accession',
        'right_index_key': 'relatedDatasets.accession'
    },
    (DATASET, FILE): {
        'left_index_key': 'file.name',
        'right_index_key': 'name'
    },
    (DATASET, SPECIMEN): {
        'left_index_key': 'specimen.biosampleId',
        'right_index_key': 'biosampleId'
    },

    (EXPERIMENT, ANALYSIS): {
        'left_index_key': 'accession',
        'right_index_key': 'experimentAccessions'
         },
    (EXPERIMENT, DATASET): {
        'left_index_key': 'accession',
        'right_index_key': 'experiment.accession'
    },
    (EXPERIMENT, FILE): {
        'left_index_key': 'accession',
        'right_index_key': 'experiment.accession'
    },

    (FILE, ARTICLE): {
        'left_index_key': 'publishedArticles.articleId',
        'right_index_key': '_id'
    },
    (FILE, DATASET): {
        'left_index_key': 'name',
        'right_index_key': 'file.name'
    },
    (FILE, EXPERIMENT): {
        'left_index_key': 'experiment.accession',
        'right_index_key': 'accession'
    },
    (FILE, ORGANISM): {
        'left_index_key': 'organism',
        'right_index_key': 'biosampleId'
    },
    (FILE, PROTOCOL_FILES): {
        'left_index_key': 'experiment.accession',
        'right_index_key': 'experiments.accession'
    },
    (FILE, PROTOCOL_SAMPLES): {
        'left_index_key': 'specimen',
        'right_index_key': 'specimens.id'
    },
    (FILE, SPECIMEN): {
        'left_index_key': 'specimen',
        'right_index_key': 'biosampleId'
    },

    (SPECIMEN, ANALYSIS): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'sampleAccessions'
    },
    # specimen-organism
    (SPECIMEN, ORGANISM): {
        'left_index_key': 'derivedFrom',
        'right_index_key': 'biosampleId'
    },
    (SPECIMEN, ARTICLE): {
        'left_index_key': 'publishedArticles.articleId',
        'right_index_key': '_id'
    },
    (SPECIMEN, DATASET): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'specimen.biosampleId'
    },
    (SPECIMEN, PROTOCOL_SAMPLES): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'specimens.id'
    },
    (SPECIMEN, FILE): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'specimen'
    },

    (ORGANISM, SPECIMEN): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'derivedFrom'
    },
    (ORGANISM, FILE): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'organism'
    },
    (ORGANISM, PROTOCOL_SAMPLES): {
        'left_index_key': 'biosampleId',
        'right_index_key': 'specimens.derivedFrom'
    },

    (PROTOCOL_ANALYSIS, ANALYSIS): {
        'left_index_key': 'key',
        'right_index_key': 'analysisProtocol.filename'
    },

    (PROTOCOL_FILES, FILE): {
        'left_index_key': 'experiments.accession',
        'right_index_key': 'experiment.accession'
    },

    (PROTOCOL_SAMPLES, FILE): {
        'left_index_key': 'specimens.id',
        'right_index_key': 'specimen'
    },
    (PROTOCOL_SAMPLES, SPECIMEN): {
        'left_index_key': 'specimens.id',
        'right_index_key': 'biosampleId'
    },
    (PROTOCOL_SAMPLES, ORGANISM): {
        'left_index_key': 'specimens.derivedFrom',
        'right_index_key': 'biosampleId'
    },


}

non_keyword_properties = set({'organism.text','organism.biosampleId','libraryPreparationDate.text',"_id"})