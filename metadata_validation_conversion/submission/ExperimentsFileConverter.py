from lxml import etree

import datetime

from .helpers import check_field_existence, remove_underscores


class ExperimentFileConverter:
    def __init__(self, json_to_convert, room_id):
        self.json_to_convert = json_to_convert
        self.room_id = room_id

    def start_conversion(self):
        experiment_xml = self.generate_experiment_xml()
        run_xml = self.generate_run_xml()
        study_xml = self.generate_study_xml()
        submission_xml = self.generate_submission_xml()
        return experiment_xml, run_xml, study_xml, submission_xml

    def generate_experiment_xml(self):
        """
        This function will generate xml file for experiment
        :return: experiment xml file
        """
        if 'experiment_ena' not in self.json_to_convert:
            return 'Error: table should have experiment_ena sheet'
        experiment_set = etree.Element('EXPERIMENT_SET')
        experiment_xml = etree.ElementTree(experiment_set)
        for record in self.json_to_convert['experiment_ena']:
            alias = record['experiment_alias']
            title = check_field_existence('title', record)
            study_ref = record['study_ref']
            design_description = record['design_description']
            sample_descriptor = record['sample_descriptor']
            library_name = check_field_existence('library_name', record)
            library_strategy = record['library_strategy']
            library_source = record['library_source']
            library_selection = record['library_selection']
            library_layout = record['library_layout']
            nominal_length = check_field_existence('nominal_length', record)
            library_construction_protocol = check_field_existence(
                'library_construction_protocol', record)
            platform = record['platform']
            instrument_model = check_field_existence('instrument_model', record)
            experiment_elt = etree.SubElement(experiment_set, 'EXPERIMENT',
                                              alias=alias)
            if title is not None:
                etree.SubElement(experiment_elt, 'TITLE').text = title
            etree.SubElement(experiment_elt, 'STUDY_REF', refname=study_ref)
            design_elt = etree.SubElement(experiment_elt, 'DESIGN')
            etree.SubElement(design_elt,
                             'DESIGN_DESCRIPTION').text = design_description
            etree.SubElement(design_elt, 'SAMPLE_DESCRIPTOR',
                             refname=sample_descriptor)
            library_descriptor_elt = etree.SubElement(design_elt,
                                                      'LIBRARY_DESCRIPTOR')
            if library_name is not None:
                etree.SubElement(library_descriptor_elt,
                                 'LIBRARY_NAME').text = library_name
            etree.SubElement(library_descriptor_elt,
                             'LIBRARY_STRATEGY').text = library_strategy
            etree.SubElement(library_descriptor_elt,
                             'LIBRARY_SOURCE').text = library_source
            etree.SubElement(library_descriptor_elt,
                             'LIBRARY_SELECTION').text = library_selection
            library_layout_elt = etree.SubElement(library_descriptor_elt,
                                                  'LIBRARY_LAYOUT')
            if nominal_length is not None:
                etree.SubElement(library_layout_elt, library_layout,
                                 NOMINAL_LENGTH=str(int(nominal_length)))
            else:
                etree.SubElement(library_layout_elt, library_layout)
            if library_construction_protocol is not None:
                etree.SubElement(library_descriptor_elt,
                                 'LIBRARY_CONSTRUCTION_PROTOCOL').text = \
                    library_construction_protocol
            platform_elt = etree.SubElement(experiment_elt, 'PLATFORM')
            platform_desc_elt = etree.SubElement(platform_elt, platform)
            if instrument_model is not None:
                etree.SubElement(platform_desc_elt,
                                 'INSTRUMENT_MODEL').text = instrument_model
            experiment_attributes_elt = etree.SubElement(
                experiment_elt, 'EXPERIMENT_ATTRIBUTES')
            faang_experiment = self.find_faang_experiment(alias)
            self.parse_faang_experiment(faang_experiment['experiments_core'],
                                        experiment_attributes_elt)
            if 'dna-binding_proteins' in faang_experiment:
                self.parse_faang_experiment(
                    faang_experiment['dna-binding_proteins'],
                    experiment_attributes_elt)
            if 'input_dna' in faang_experiment:
                self.parse_faang_experiment(faang_experiment['input_dna'],
                                            experiment_attributes_elt)
            self.parse_faang_experiment(faang_experiment,
                                        experiment_attributes_elt)
        experiment_xml.write(f"{self.room_id}_experiment.xml",
                             pretty_print=True, xml_declaration=True,
                             encoding='UTF-8')
        return 'Success'

    def find_faang_experiment(self, sample_descriptor):
        """
        This function will return faang experiment record
        :param sample_descriptor: id to search for
        :return: faang experiment record
        """
        for exp_type, exp_value in self.json_to_convert.items():
            if exp_type not in ['submission', 'study', 'run',
                                'experiment_ena']:
                for record in exp_value:
                    record_id = record['custom']['experiment_alias']['value']
                    if sample_descriptor == record_id:
                        return record

    @staticmethod
    def parse_faang_experiment(faang_experiment, experiment_attributes_elt):
        for attr_name, attr_value in faang_experiment.items():
            if attr_name in ['experiments_core', 'dna-binding_proteins',
                             'input_dna', 'custom']:
                continue
            experiment_attribute_elt = etree.SubElement(
                experiment_attributes_elt, 'EXPERIMENT_ATTRIBUTE')
            etree.SubElement(experiment_attribute_elt,
                             'TAG').text = remove_underscores(attr_name)
            if 'value' in attr_value:
                value = attr_value['value']
            elif 'text' in attr_value:
                value = attr_value['text']
            etree.SubElement(experiment_attribute_elt,
                             'VALUE').text = str(value)
            if 'units' in attr_value:
                etree.SubElement(experiment_attribute_elt,
                                 'UNITS').text = attr_value['units']

    def generate_run_xml(self):
        """
        This function will generate xml file for run
        :return: run xml file
        """
        if 'run' not in self.json_to_convert:
            return 'Error: table should have run sheet'
        run_set = etree.Element('RUN_SET')
        run_xml = etree.ElementTree(run_set)
        for record in self.json_to_convert['run']:
            run_alias = record['alias']
            run_center = record['run_center']
            run_date = datetime.datetime.strptime(record['run_date'],
                                                  '%Y-%m-%d').isoformat()
            experiment_ref = record['experiment_ref']
            filename = record['filename']
            filetype = record['filetype']
            checksum_method = record['checksum_method']
            checksum = record['checksum']
            paired = False
            if check_field_existence('filename_pair', record) \
                    and check_field_existence('filetype_pair', record) \
                    and check_field_existence('checksum_method_pair', record) \
                    and check_field_existence('checksum_pair', record):
                paired = True
                filename_pair = record['filename_pair']
                filetype_pair = record['filetype_pair']
                checksum_method_pair = record['checksum_method_pair']
                checksum_pair = record['checksum_pair']
            run_elt = etree.SubElement(run_set, 'RUN', alias=run_alias,
                                       run_center=run_center, run_date=run_date)
            etree.SubElement(run_elt, 'EXPERIMENT_REF', refname=experiment_ref)
            data_block_elt = etree.SubElement(run_elt, 'DATA_BLOCK')
            files_elt = etree.SubElement(data_block_elt, 'FILES')
            etree.SubElement(files_elt, 'FILE', filename=filename,
                             filetype=filetype,
                             checksum_method=checksum_method, checksum=checksum)
            if paired:
                etree.SubElement(files_elt, 'FILE', filename=filename_pair,
                                 filetype=filetype_pair,
                                 checksum_method=checksum_method_pair,
                                 checksum=checksum_pair)
        run_xml.write(f"{self.room_id}_run.xml", pretty_print=True,
                      xml_declaration=True, encoding='UTF-8')
        return 'Success'

    def generate_study_xml(self):
        """
        This function will generate xml file for study
        :return: study xml file
        """
        if 'study' not in self.json_to_convert:
            return 'Error: table should have study sheet'
        study_set = etree.Element('STUDY_SET')
        study_xml = etree.ElementTree(study_set)
        for record in self.json_to_convert['study']:
            study_alias = record['study_alias']
            study_title = record['study_title']
            study_type = record['study_type']
            study_abstract = record['study_abstract'] \
                if 'study_abstract' in record else None
            study_elt = etree.SubElement(study_set, 'STUDY', alias=study_alias)
            descriptor_elt = etree.SubElement(study_elt, 'DESCRIPTOR')
            etree.SubElement(descriptor_elt, 'STUDY_TITLE').text = study_title
            etree.SubElement(descriptor_elt, 'STUDY_TYPE',
                             existing_study_type=study_type)
            if study_abstract is not None:
                etree.SubElement(descriptor_elt,
                                 'STUDY_ABSTRACT').text = study_abstract
        study_xml.write(f"{self.room_id}_study.xml", pretty_print=True,
                        xml_declaration=True, encoding='UTF-8')
        return 'Success'

    def generate_submission_xml(self):
        """
        This function will generate xml file for submission
        :return: submission xml file
        """
        if 'submission' not in self.json_to_convert:
            return 'Error: table should have submission sheet'
        submission_set = etree.Element('SUBMISSION_SET')
        submission_xml = etree.ElementTree(submission_set)
        for record in self.json_to_convert['submission']:
            submission_elt = etree.SubElement(submission_set, 'SUBMISSION',
                                              alias=record['alias'])
            actions_elt = etree.SubElement(submission_elt, 'ACTIONS')
            action_elt = etree.SubElement(actions_elt, 'ACTION')
            etree.SubElement(action_elt, 'ADD')
            action_elt = etree.SubElement(actions_elt, 'ACTION')
            etree.SubElement(action_elt, 'RELEASE')

        submission_xml.write(f"{self.room_id}_submission.xml",
                             pretty_print=True, xml_declaration=True,
                             encoding='UTF-8')
        return 'Success'
