import unittest
from metadata_validation_conversion.conversion.analysis.convert_to_analysis_xml \
    import process_header, find_key_columns


class MyTestCase(unittest.TestCase):
    def test_find_key_columns_types(self):
        self.assertRaises(TypeError, find_key_columns, 15, 'not list 2')
        self.assertRaises(TypeError, find_key_columns, ['15'], 'not list 2')
        self.assertRaises(TypeError, find_key_columns, 15, ['list 2'])
        self.assertRaises(TypeError, find_key_columns, [15], ['list 2 elem 1', 'list 2 elem 2'])
        self.assertRaises(TypeError, find_key_columns, ['list 1 elem 1'], [True, 'list 2 elem 2'])

    def test_find_key_columns(self):
        headers = ['Title',	'alias', 'Analysis type', 'SAMPLE_DESCRIPTOR', 'SAMPLE_DESCRIPTOR', 'analysis center']
        self.assertListEqual(find_key_columns(headers, ['alias']), [1])
        self.assertListEqual(find_key_columns(headers, ['analysis center', 'alias']), [1, 5])
        # key column appears more than once, raise ValueError
        self.assertRaises(ValueError, find_key_columns, headers, ['alias', 'SAMPLE_DESCRIPTOR'])

    def test_process_header(self):
        input_data = {
            'simple': ['alias', 'Analysis type', 'description', 'RUN_alias', 'analysis center'],
            'multiple': ['alias', 'Analysis type', 'RUN_alias', 'RUN_alias', 'related analyses',
                         'file names', 'file types', 'checksum methods', 'checksums',
                         'file names', 'file types', 'checksum methods', 'checksums',
                         'file names', 'file types', 'checksum methods', 'checksums', 'analysis center'],
            'unit': ['alias', 'analysis date', 'Units'],
            'ontology': ['alias', 'project', 'Material', 'Term Source REF', 'Term Source ID', 'Organism',
                         'Term Source REF', 'Term Source ID'],
            'combined': ['project', 'Organism', 'Term Source REF', 'Term Source ID',
                         'Organism', 'Term Source REF', 'Term Source ID', 'breed', 'Child of', 'Child of']
        }
        expected = {
            'simple': {0: 'alias', 1: 'Analysis type', 2: 'description', 3: 'RUN_alias', 4: 'analysis center'},
            'multiple': {0: 'alias', 1: 'Analysis type', 2: 'RUN_alias', 3: 'RUN_alias', 4: 'related analyses',
                 5: 'file names', 6: 'file types', 7: 'checksum methods', 8: 'checksums',
                 9: 'file names', 10: 'file types', 11: 'checksum methods', 12: 'checksums',
                 13: 'file names', 14: 'file types', 15: 'checksum methods', 16: 'checksums', 17: 'analysis center'},
            'unit': {0: 'alias', 1: 'analysis date', 2: 'analysis date-unit'},
            'ontology': {0: 'alias', 1: 'project', 2: 'Material', 3: 'Material-ontology_library',
                         4: 'Material-ontology_term', 5: 'Organism', 6: 'Organism-ontology_library',
                         7: 'Organism-ontology_term'},
            'combined': {0: 'project', 1: 'Organism', 2: 'Organism-ontology_library', 3: 'Organism-ontology_term',
                         4: 'Organism', 5: 'Organism-ontology_library', 6: 'Organism-ontology_term', 7: 'breed',
                         8: 'Child of', 9: 'Child of'}
        }
        for category in input_data.keys():
            actual = process_header(input_data[category])
            self.assertDictEqual(actual, expected[category])


if __name__ == '__main__':
    unittest.main()
