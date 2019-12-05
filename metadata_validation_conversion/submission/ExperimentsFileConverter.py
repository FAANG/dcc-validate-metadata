from .helpers import check_field_existence, remove_underscores


class ExperimentFileConverter:
    def __init__(self, json_to_convert):
        self.json_to_convert = json_to_convert

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
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<EXPERIMENT_SET xmlns:xsi=' \
                  '"http://www.w3.org/2001/XMLSchema-instance" ' \
                  'xsi:noNamespaceSchemaLocation=' \
                  '"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/' \
                  'SRA.experiment.xsd">\n'
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
            # TODO check for this value
            nominal_length = record['nominal_length']
            library_construction_protocol = check_field_existence(
                'library_construction_protocol', record)
            platform = record['platform']
            instrument_model = check_field_existence('instrument_model', record)

            result += f'\t<EXPERIMENT alias="{alias}">\n'

            if title is not None:
                result += f'\t\t<TITLE>{title}</TITLE>\n'

            result += f'\t\t<STUDY_REF refname="{study_ref}"/>\n'

            result += '\t\t<DESIGN>\n'
            result += f'\t\t\t<DESIGN_DESCRIPTION>' \
                      f'{design_description}</DESIGN_DESCRIPTION>\n'
            result += f'\t\t\t<SAMPLE_DESCRIPTOR ' \
                      f'refname="{sample_descriptor}"/>\n'
            result += '\t\t\t<LIBRARY_DESCRIPTOR>\n'
            if library_name is not None:
                result += f'\t\t\t\t<LIBRARY_NAME>' \
                          f'{library_name}</LIBRARY_NAME>\n'
            result += f'\t\t\t\t<LIBRARY_STRATEGY>' \
                      f'{library_strategy}</LIBRARY_STRATEGY>\n'
            result += f'\t\t\t\t<LIBRARY_SOURCE>' \
                      f'{library_source}</LIBRARY_SOURCE>\n'
            result += f'\t\t\t\t<LIBRARY_SELECTION>' \
                      f'{library_selection}</LIBRARY_SELECTION>\n'
            result += f'\t\t\t\t<LIBRARY_LAYOUT>\n'
            result += f'\t\t\t\t\t<{library_layout} ' \
                      f'NOMINAL_LENGTH="{nominal_length}"/>\n'
            result += '\t\t\t\t</LIBRARY_LAYOUT>\n'
            if library_construction_protocol is not None:
                result += f'\t\t\t\t<LIBRARY_CONSTRUCTION_PROTOCOL>' \
                          f'{library_construction_protocol}' \
                          f'</LIBRARY_CONSTRUCTION_PROTOCOL>\n'
            result += '\t\t\t</LIBRARY_DESCRIPTOR>\n'
            result += '\t\t</DESIGN>\n'

            result += '\t\t<PLATFORM>\n'
            result += f'\t\t\t<{platform}>\n'
            if instrument_model is not None:
                result += f'\t\t\t\t<INSTRUMENT_MODEL>' \
                          f'{instrument_model}</INSTRUMENT_MODEL>\n'
            result += f'\t\t\t<{platform}>\n'
            result += '\t\t<PLATFORM>\n'

            result += '\t\t<EXPERIMENT_ATTRIBUTES>\n'
            faang_experiment = self.find_faang_experiment(sample_descriptor)
            for attr_name, attr_value in \
                    faang_experiment['experiments_core'].items():
                result += '\t\t\t<EXPERIMENT_ATTRIBUTE>\n'
                result += f'\t\t\t\t<TAG>{remove_underscores(attr_name)}' \
                          f'</TAG>\n'
                if 'value' in attr_value:
                    value = attr_value['value']
                elif 'text' in attr_value:
                    value = attr_value['text']
                result += f'\t\t\t\t<VALUE>{value}</VALUE>\n'
                if 'units' in attr_value:
                    units = attr_value['units']
                    result += f'\t\t\t\t<UNITS>{units}</UNITS>\n'
                result += '\t\t\t</EXPERIMENT_ATTRIBUTE>\n'
            for attribute in faang_experiment:
                if attribute == 'experiments_core':
                    continue
                pass
            result += '\t\t</EXPERIMENT_ATTRIBUTES>\n'

            result += '\t</EXPERIMENT>\n'
        result += '</EXPERIMENT_SET>'
        return result

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
                    record_id = record['custom']['sample_descriptor']['value']
                    if sample_descriptor == record_id:
                        return record

    def generate_run_xml(self):
        """
        This function will generate xml file for run
        :return: run xml file
        """
        if 'run' not in self.json_to_convert:
            return 'Error: table should have run sheet'
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<RUN_SET xmlns:xsi=' \
                  '"http://www.w3.org/2001/XMLSchema-instance" ' \
                  'xsi:noNamespaceSchemaLocation=' \
                  '"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.run.xsd">\n'
        for record in self.json_to_convert['run']:
            run_alias = record['alias']
            run_center = record['run_center']
            run_date = record['run_date']
            experiment_ref = record['experiment_ref']
            filename = record['filename']
            filetype = record['filetype']
            checksum_method = record['checksum_method']
            checksum = record['checksum']
            paired = False
            if 'filename_pair' in record and 'filetype_pair' in record \
                    and 'checksum_method_pair' in record \
                    and 'checksum_pair' in record:
                paired = True
                filename_pair = record['filename_pair']
                filetype_pair = record['filetype_pair']
                checksum_method_pair = record['checksum_method_pair']
                checksum_pair = record['checksum_pair']

            result += f'\t<RUN alias="{run_alias}" run_center="{run_center}" ' \
                      f'run_date="{run_date}">\n'

            result += f'\t\t<EXPERIMENT_REF refname="{experiment_ref}"/>\n'

            result += '\t\t<DATA_BLOCK>\n'
            result += '\t\t\t<FILES>\n'

            result += f'\t\t\t\t<FILE filename="{filename}" ' \
                      f'filetype="{filetype}" ' \
                      f'checksum_method="{checksum_method}" ' \
                      f'checksum="{checksum}"/>\n'
            if paired:
                result += f'\t\t\t\t<FILE filename="{filename_pair}" ' \
                          f'filetype="{filetype_pair}" ' \
                          f'checksum_method="{checksum_method_pair}" ' \
                          f'checksum="{checksum_pair}"/>\n'

            result += '\t\t\t</FILES>\n'
            result += '\t\t</DATA_BLOCK>\n'

            result += '\t</RUN>\n'
        result += '</RUN_SET>'
        return result

    def generate_study_xml(self):
        """
        This function will generate xml file for study
        :return: study xml file
        """
        if 'study' not in self.json_to_convert:
            return 'Error: table should have study sheet'
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<STUDY_SET xmlns:xsi=' \
                  '"http://www.w3.org/2001/XMLSchema-instance" ' \
                  'xsi:noNamespaceSchemaLocation=' \
                  '"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.study.xsd">\n'
        for record in self.json_to_convert['study']:
            study_alias = record['study_alias']
            study_title = record['study_title']
            study_type = record['study_type']
            study_abstract = record['study_abstract'] \
                if 'study_abstract' in record else None
            result += f'\t<STUDY alias="{study_alias}">\n'

            result += '\t\t<DESCRIPTOR>\n'

            result += f'\t\t\t<STUDY_TITLE>{study_title}</STUDY_TITLE>\n'
            result += f'\t\t\t<STUDY_TYPE existing_study_type=' \
                      f'"{study_type}"/>\n'
            if study_abstract is not None:
                result += f'\t\t\t<STUDY_ABSTRACT>' \
                          f'{study_abstract}</STUDY_ABSTRACT>\n'

            result += '\t\t</DESCRIPTOR>\n'

            result += '\t</STUDY>\n'
        result += '</STUDY_SET>'
        return result

    def generate_submission_xml(self):
        """
        This function will generate xml file for submission
        :return: submission xml file
        """
        if 'submission' not in self.json_to_convert:
            return 'Error: table should have submission sheet'
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET xmlns:xsi=' \
                  '"http://www.w3.org/2001/XMLSchema-instance" ' \
                  'xsi:noNamespaceSchemaLocation=' \
                  '"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/' \
                  'SRA.submission.xsd">\n'
        for record in self.json_to_convert['submission']:
            alias = record['alias']
            result += f'\t<SUBMISSION alias="{alias}">\n'

            result += '\t\t<ACTIONS>\n'

            result += '\t\t\t<ACTION>\n'
            result += '\t\t\t\t<ADD/>\n'
            result += '\t\t\t</ACTION>\n'

            result += '\t\t\t<ACTION>\n'
            result += '\t\t\t\t<RELEASE/>\n'
            result += '\t\t\t</ACTION>\n'

            result += '\t\t</ACTIONS>\n'

            result += '\t</SUBMISSION>\n'
        result += '</SUBMISSION_SET>'
        return result
