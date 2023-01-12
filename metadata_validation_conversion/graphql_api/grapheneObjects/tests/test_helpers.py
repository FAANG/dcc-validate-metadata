import unittest
from graphql_api.grapheneObjects.tests import index_data

from ..helpers import is_filter_query_depth_valid, generate_es_filters, update_experiment_fieldnames, \
    retrieve_mapping_keys, generate_index_map, get_projected_data



class TestSum(unittest.TestCase):

    def test_query_depth(self):
        filter_query = {'basic': {'accession': ['ERX9379020']}, 'join': {'file': {'basic': {}}}}
        result = is_filter_query_depth_valid(filter_query, 1)
        self.assertTrue(result)

        filter_query = {'basic': {'accession': ['SRX1023686']},
                        'join': {'file': {'basic': {}, 'join': {'article': {'basic': {}}}}}}
        result = is_filter_query_depth_valid(filter_query, 1)
        self.assertTrue(result)

        filter_query = {'basic': {'accession': ['SRX1023686']}, 'join': {
            'file': {'basic': {}, 'join': {'article': {'basic': {}, 'join': {'dataset': {'basic': {}}}}}}}}
        result = is_filter_query_depth_valid(filter_query, 1)
        self.assertFalse(result)

    def test_generate_es_query(self):
        query = {'accession': ['ERX9379020', 'SRX1023686']}
        es_filter_queries = []
        prefix = ''
        generate_es_filters(query, es_filter_queries, prefix)
        self.assertEqual(es_filter_queries,
                         [{'terms': {'accession': ['ERX9379020', 'SRX1023686']}}])

    def test_update_experiment_fieldnames(self):
        right_index_map = {'ERX3645356': [
            {'accession': 'ERX3645356', 'project': 'FAANG', 'secondaryProject': '', 'assayType': 'ChIP-seq',
             'experimentTarget': 'histone_modification', 'libraryName': '001_0241_aC2',
             'ChIP-seq DNA-binding': {
                 'chipProtocol': {
                     'url': 'ftp://ftp.faang.ebi.ac.uk/ftp/protocols/assays/UCD_SOP_ChIP-seq_for_Histone_Marks_20191101.pdf',
                     'filename': 'UCD_SOP_ChIP-seq_for_Histone_Marks_20191101.pdf'},
                 'libraryGenerationMaxFragmentSizeRange': '600', 'libraryGenerationMinFragmentSizeRange': '200',
                 'chipAntibodyProvider': 'Diagenode', 'chipAntibodyCatalog': 'C15410003',
                 'chipAntibodyLot': 'A5051-001P', 'chipTarget': 'H3K4me3', 'controlExperiment': 'ERX3645404'},
             'standardMet': 'FAANG', 'versionLastStandardMet': '3.8', '_id': 'ERX3645356'}]}

        mapping_key = 'ERX3645356'

        update_experiment_fieldnames(right_index_map, mapping_key)

        result = {'ERX3645356': [
            {'accession': 'ERX3645356', 'project': 'FAANG', 'secondaryProject': '', 'assayType': 'ChIP-seq',
             'experimentTarget': 'histone_modification', 'libraryName': '001_0241_aC2',
             'ChIPSeqDnaBinding': {
                 'chipProtocol': {
                     'url': 'ftp://ftp.faang.ebi.ac.uk/ftp/protocols/assays/UCD_SOP_ChIP-seq_for_Histone_Marks_20191101.pdf',
                     'filename': 'UCD_SOP_ChIP-seq_for_Histone_Marks_20191101.pdf'},
                 'libraryGenerationMaxFragmentSizeRange': '600', 'libraryGenerationMinFragmentSizeRange': '200',
                 'chipAntibodyProvider': 'Diagenode', 'chipAntibodyCatalog': 'C15410003',
                 'chipAntibodyLot': 'A5051-001P', 'chipTarget': 'H3K4me3', 'controlExperiment': 'ERX3645404'},
             'standardMet': 'FAANG', 'versionLastStandardMet': '3.8', '_id': 'ERX3645356'}]}
        self.assertEqual(result, right_index_map)

    def test_retrieve_mapping_keys(self):
        record = {'organism': {'text': 'Bos taurus', 'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9913'},
                  'sex': {'text': 'female', 'ontologyTerms': 'PATO_0000383'},
                  'birthDate': {'text': '2008-08-01', 'unit': 'YYYY-MM-DD'},
                  'breed': {'text': 'Holstein', 'ontologyTerms': 'LBO_0000132'}, 'birthLocation': None,
                  'birthLocationLongitude': {'text': None, 'unit': None},
                  'birthLocationLatitude': {'text': None, 'unit': None}, 'birthWeight': {'text': None, 'unit': None},
                  'placentalWeight': {'text': None, 'unit': None}, 'pregnancyLength': {'text': None, 'unit': None},
                  'deliveryTiming': None, 'deliveryEase': None, 'pedigree': None, 'name': 'BTA-DEDJTR-BBM409015438',
                  'biosampleId': 'SAMEA4675147', 'etag': '"0895a68be888fcf4f35dd4693bf5fa558"', 'id_number': '4675147',
                  'description': 'Lactating holstein female', 'releaseDate': '2018-02-27', 'updateDate': '2018-07-19',
                  'material': {'text': 'organism', 'ontologyTerms': 'OBI_0100026'}, 'project': 'FAANG',
                  'availability': 'mailto:amanda.chamberlain@ecodev.vic.gov.au', 'organization': [
                {'name': 'DEDJTR', 'role': 'institution', 'URL': 'http://economicdevelopment.vic.gov.au/'}],
                  'customField': [
                      {'name': 'Submission description', 'value': 'Tissue samples from a lactating holstein cow'},
                      {'name': 'Submission identifier', 'value': 'GSB-9944'},
                      {'name': 'Submission title', 'value': 'DEDJTR-FAANG-Chamberlain-Cattle-171201'},
                      {'name': 'lactation duration', 'value': '65', 'unit': 'day'},
                      {'name': 'parturition trait', 'value': '1st parity', 'ontologyTerms': ['ATOL_0000443']}],
                  'healthStatus': [{'text': 'normal', 'ontologyTerms': 'PATO_0000461'}], 'alternativeId': [],
                  'standardMet': 'FAANG', '_id': 'SAMEA4675147'}
        record_key = 'biosampleId'
        result = retrieve_mapping_keys(record, record_key)
        self.assertEqual(result, ['SAMEA4675147'])

    def test_generate_index_map(self):
        index_map = [{'specimen': 'SAMEA104728837', 'organism': 'SAMEA104728862', 'species': {'text': 'Equus caballus',
                                                                                              'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9796'},
                      'secondaryProject': '',
                      'url': 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR365/004/ERR3653314/ERR3653314.fastq.gz',
                      'name': 'ERR3653314.fastq.gz', 'type': 'fastq', 'size': '3030651365', 'readableSize': '2.82GB',
                      'checksumMethod': 'md5', 'checksum': 'ceac63e157a93996907bc79b2f48be84', 'archive': 'ENA',
                      'baseCount': '4790476250', 'readCount': '95809525', 'releaseDate': '2019-11-10',
                      'updateDate': '2019-11-11', 'submission': 'ERA2204784',
                      'experiment': {'accession': 'ERX3645340', 'assayType': 'ChIP-seq', 'target': 'H3K4me1',
                                     'standardMet': 'FAANG'}, 'paperPublished': 'true',
                      'submitterEmail': 'rbellone@ucdavis.edu, cjfinno@ucdavis.edu, jessica.petersen@unl.edu',
                      '_id': 'ERR3653314'}, {'specimen': 'SAMEA104728736', 'organism': 'SAMEA104728862',
                                             'species': {'text': 'Equus caballus',
                                                         'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9796'},
                                             'secondaryProject': '',
                                             'url': 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR365/002/ERR3653312/ERR3653312.fastq.gz',
                                             'name': 'ERR3653312.fastq.gz', 'type': 'fastq', 'size': '1339313015',
                                             'readableSize': '1.25GB', 'checksumMethod': 'md5',
                                             'checksum': '84384aac7d8d1b33c82bb52574f9aa77', 'archive': 'ENA',
                                             'baseCount': '2123870750', 'readCount': '42477415',
                                             'releaseDate': '2019-11-10', 'updateDate': '2019-11-10',
                                             'submission': 'ERA2204784',
                                             'experiment': {'accession': 'ERX3645338', 'assayType': 'ChIP-seq',
                                                            'paperPublished': 'true',
                                                            'submitterEmail': 'rbellone@ucdavis.edu, cjfinno@ucdavis.edu, jessica.petersen@unl.edu',
                                                            '_id': 'ERR3653312'}},
                     {'specimen': 'SAMEA104728771', 'organism': 'SAMEA104728862', 'species': {'text': 'Equus caballus',
                                                                                              'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9796'},
                      'secondaryProject': '',
                      'url': 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR365/003/ERR3653313/ERR3653313.fastq.gz',
                      'name': 'ERR3653313.fastq.gz', 'type': 'fastq', 'size': '1262009999', 'readableSize': '1.18GB',
                      'checksumMethod': 'md5', 'checksum': '4f75b48a1662d1a0ed9128aa20811426', 'archive': 'ENA',
                      'baseCount': '1991916900', 'readCount': '39838338', 'releaseDate': '2019-11-10',
                      'updateDate': '2019-11-10', 'submission': 'ERA2204784',
                      'experiment': {'accession': 'ERX3645339', 'assayType': 'ChIP-seq', 'target': 'H3K4me1',
                                     'standardMet': 'FAANG'},
                      'paperPublished': 'true',
                      'submitterEmail': 'rbellone@ucdavis.edu, cjfinno@ucdavis.edu, jessica.petersen@unl.edu',
                      '_id': 'ERR3653313'}]
        record_key = 'name'

        result = dict(generate_index_map(index_map, record_key))

        expected_result = {'ERR3653314.fastq.gz': [{'specimen': 'SAMEA104728837', 'organism': 'SAMEA104728862',
                                                    'species': {'text': 'Equus caballus',
                                                                'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9796'},
                                                    'secondaryProject': '',
                                                    'url': 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR365/004/ERR3653314/ERR3653314.fastq.gz',
                                                    'name': 'ERR3653314.fastq.gz', 'type': 'fastq',
                                                    'size': '3030651365', 'readableSize': '2.82GB',
                                                    'checksumMethod': 'md5',
                                                    'checksum': 'ceac63e157a93996907bc79b2f48be84', 'archive': 'ENA',
                                                    'baseCount': '4790476250', 'readCount': '95809525',
                                                    'releaseDate': '2019-11-10', 'updateDate': '2019-11-11',
                                                    'submission': 'ERA2204784',
                                                    'experiment': {'accession': 'ERX3645340', 'assayType': 'ChIP-seq',
                                                                   'target': 'H3K4me1', 'standardMet': 'FAANG'},
                                                    'paperPublished': 'true',
                                                    'submitterEmail': 'rbellone@ucdavis.edu, cjfinno@ucdavis.edu, jessica.petersen@unl.edu',
                                                    '_id': 'ERR3653314'}], 'ERR3653312.fastq.gz': [
            {'specimen': 'SAMEA104728736', 'organism': 'SAMEA104728862',
             'species': {'text': 'Equus caballus', 'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9796'},
             'secondaryProject': '', 'url': 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR365/002/ERR3653312/ERR3653312.fastq.gz',
             'name': 'ERR3653312.fastq.gz', 'type': 'fastq', 'size': '1339313015', 'readableSize': '1.25GB',
             'checksumMethod': 'md5', 'checksum': '84384aac7d8d1b33c82bb52574f9aa77', 'archive': 'ENA',
             'baseCount': '2123870750', 'readCount': '42477415', 'releaseDate': '2019-11-10',
             'updateDate': '2019-11-10', 'submission': 'ERA2204784',
             'experiment': {'accession': 'ERX3645338', 'assayType': 'ChIP-seq', 'paperPublished': 'true',
                            'submitterEmail': 'rbellone@ucdavis.edu, cjfinno@ucdavis.edu, jessica.petersen@unl.edu',
                            '_id': 'ERR3653312'}}], 'ERR3653313.fastq.gz': [
            {'specimen': 'SAMEA104728771', 'organism': 'SAMEA104728862',
             'species': {'text': 'Equus caballus', 'ontologyTerms': 'http://purl.obolibrary.org/obo/NCBITaxon_9796'},
             'secondaryProject': '', 'url': 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR365/003/ERR3653313/ERR3653313.fastq.gz',
             'name': 'ERR3653313.fastq.gz', 'type': 'fastq', 'size': '1262009999', 'readableSize': '1.18GB',
             'checksumMethod': 'md5', 'checksum': '4f75b48a1662d1a0ed9128aa20811426', 'archive': 'ENA',
             'baseCount': '1991916900', 'readCount': '39838338', 'releaseDate': '2019-11-10',
             'updateDate': '2019-11-10', 'submission': 'ERA2204784',
             'experiment': {'accession': 'ERX3645339', 'assayType': 'ChIP-seq', 'target': 'H3K4me1',
                            'standardMet': 'FAANG'}, 'paperPublished': 'true',
             'submitterEmail': 'rbellone@ucdavis.edu, cjfinno@ucdavis.edu, jessica.petersen@unl.edu',
             '_id': 'ERR3653313'}]}

        self.assertEqual(result, expected_result)

    def test_get_projected_data(self):
        left_index = 'dataset'
        right_index = 'file'
        left_index_data = index_data.left_data
        right_index_data = index_data.right_data
        result = dict(get_projected_data(left_index, right_index, left_index_data, right_index_data)[0]['join'])

        self.assertIsInstance(result['file'], list)
