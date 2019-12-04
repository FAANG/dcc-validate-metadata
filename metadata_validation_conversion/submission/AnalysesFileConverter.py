class AnalysesFileConverter:
    def __init__(self, json_to_convert):
        self.json_to_convert = json_to_convert

    def start_conversion(self):
        analysis_xml = self.generate_analysis_xml()
        submission_xml = self.generate_submission_xml()
        return analysis_xml, submission_xml

    def generate_analysis_xml(self):
        """
        This function will generate xml file with analyses
        :return: xml file for analyses
        """
        result = '<?xml version="1.0" encoding="UTF-8"?>\n<ANALYSIS_SET>\n'
        number_of_records = len(self.json_to_convert['ena'])
        for record_number in range(number_of_records):
            title = self.json_to_convert['ena'][record_number]['title']['value']
            alias = self.json_to_convert['ena'][record_number]['alias']['value']
            description = self.json_to_convert['ena'][record_number][
                'description']['value']
            study = self.json_to_convert['ena'][record_number]['study']['value']
            samples = self.json_to_convert['ena'][record_number]['samples']
            experiments = self.json_to_convert['ena'][record_number][
                'experiments']
            runs = self.json_to_convert['ena'][record_number]['runs']
            analysis_type = self.json_to_convert['ena'][record_number][
                'analysis_type']['value']
            file_names = self.json_to_convert['ena'][record_number][
                'file_names']
            file_types = self.json_to_convert['ena'][record_number][
                'file_types']
            checksum_methods = self.json_to_convert['ena'][record_number][
                'checksum_methods']
            checksums = self.json_to_convert['ena'][record_number]['checksums']
            project = self.json_to_convert['faang'][record_number]['project'][
                'value']
            assay_type = self.json_to_convert['faang'][record_number][
                'assay_type']['value']
            analysis_protocol = self.json_to_convert['faang'][record_number][
                'analysis_protocol']['value']
            reference_genome = self.json_to_convert['faang'][record_number][
                'reference_genome']['value']
            analysis_center = self.json_to_convert['ena'][record_number][
                'analysis_center']['value']
            analysis_date_value = self.json_to_convert['ena'][record_number][
                'analysis_date']['value']
            analysis_date_units = self.json_to_convert['ena'][record_number][
                'analysis_date']['units']

            result += f'\t<ANALYSIS alias="{alias}">\n'

            result += f'\t\t<TITLE>{title}</TITLE>\n'

            result += f'\t\t<DESCRIPTION>{description}</DESCRIPTION>\n'

            result += f'\t\t<STUDY_REF accession="{study}"/>\n'

            for sample in samples:
                sample_ref = sample['value']
                result += f'\t\t<SAMPLE_REF accession="{sample_ref}"/>\n'

            for experiment in experiments:
                exp_ref = experiment['value']
                result += f'\t\t<EXPERIMENT_REF accession="{exp_ref}"/>\n'

            for run in runs:
                run_ref = run['value']
                result += f'\t\t<RUN_REF accession="{run_ref}"/>\n'

            result += '\t\t<ANALYSIS_TYPE>\n'
            result += f'\t\t\t<{analysis_type}>\n'
            result += f'\t\t\t</{analysis_type}>\n'
            result += '\t\t</ANALYSIS_TYPE>\n'

            result += '\t\t<FILES>\n'
            for index, file_name in enumerate(file_names):
                filename = file_name['value']
                filetype = file_types[index]['value']
                checksum_method = checksum_methods[index]['value']
                checksum = checksums[index]['value']
                result += f'\t\t\t<FILE filename="{filename}" ' \
                          f'filetype="{filetype}" ' \
                          f'checksum_method="{checksum_method}" ' \
                          f'checksum="{checksum}"/>\n'
            result += '\t\t</FILES>\n'

            result += '\t\t<ANALYSIS_ATTRIBUTES>\n'

            result += '\t\t\t<ANALYSIS_ATTRIBUTE>\n'
            result += '\t\t\t\t<TAG>Project</TAG>\n'
            result += f'\t\t\t\t<VALUE>{project}</VALUE>\n'
            result += '\t\t\t</ANALYSIS_ATTRIBUTE>\n'

            result += '\t\t\t<ANALYSIS_ATTRIBUTE>\n'
            result += '\t\t\t\t<TAG>Assay Type</TAG>\n'
            result += f'\t\t\t\t<VALUE>{assay_type}</VALUE>\n'
            result += '\t\t\t</ANALYSIS_ATTRIBUTE>\n'

            result += '\t\t\t<ANALYSIS_ATTRIBUTE>\n'
            result += '\t\t\t\t<TAG>Analysis Protocol</TAG>\n'
            result += f'\t\t\t\t<VALUE>{analysis_protocol}</VALUE>\n'
            result += '\t\t\t</ANALYSIS_ATTRIBUTE>\n'

            result += '\t\t\t<ANALYSIS_ATTRIBUTE>\n'
            result += '\t\t\t\t<TAG>Reference genome</TAG>\n'
            result += f'\t\t\t\t<VALUE>{reference_genome}</VALUE>\n'
            result += '\t\t\t</ANALYSIS_ATTRIBUTE>\n'

            result += '\t\t\t<ANALYSIS_ATTRIBUTE>\n'
            result += '\t\t\t\t<TAG>Analysis center</TAG>\n'
            result += f'\t\t\t\t<VALUE>{analysis_center}</VALUE>\n'
            result += '\t\t\t</ANALYSIS_ATTRIBUTE>\n'

            result += '\t\t\t<ANALYSIS_ATTRIBUTE>\n'
            result += '\t\t\t\t<TAG>Analysis date</TAG>\n'
            result += f'\t\t\t\t<VALUE>{analysis_date_value}</VALUE>\n'
            result += f'\t\t\t\t<UNITS>{analysis_date_units}</UNITS>\n'
            result += '\t\t\t</ANALYSIS_ATTRIBUTE>\n'

            result += '\t\t</ANALYSIS_ATTRIBUTES>\n'

            result += '\t</ANALYSIS>\n'
        result += '</ANALYSIS_SET>'
        return result

    @staticmethod
    def generate_submission_xml():
        """
        This function will generate xml file with submission
        :return: xml file for submission
        """
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result
