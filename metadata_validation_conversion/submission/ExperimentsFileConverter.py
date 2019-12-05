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
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result

    def generate_run_xml(self):
        """
        This function will generate xml file for run
        :return: run xml file
        """
        # TODO: generate an Error
        if 'run' not in self.json_to_convert:
            return 'Error'
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
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<STUDY_SET ' \
                  'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                  'xsi:noNamespaceSchemaLocation=' \
                  '"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.study.xsd">\n'
        result += '</STUDY_SET>'
        return result

    def generate_submission_xml(self):
        """
        This function will generate xml file for submission
        :return: submission xml file
        """
        # TODO: generate an Error
        if 'submission' not in self.json_to_convert:
            return 'Error'
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
