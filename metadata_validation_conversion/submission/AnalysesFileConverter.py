from lxml import etree


class AnalysesFileConverter:
    def __init__(self, json_to_convert, room_id):
        self.json_to_convert = json_to_convert
        self.room_id = room_id

    def start_conversion(self):
        analysis_xml = self.generate_analysis_xml()
        submission_xml = self.generate_submission_xml()
        return analysis_xml, submission_xml

    def generate_analysis_xml(self):
        """
        This function will generate xml file with analyses
        :return: xml file for analyses
        """
        analysis_set = etree.Element('ANALYSIS_SET')
        analysis_xml = etree.ElementTree(analysis_set)
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

            analysis_elt = etree.SubElement(analysis_set, 'ANALYSIS',
                                            alias=alias)
            etree.SubElement(analysis_elt, 'TITLE').text = title
            etree.SubElement(analysis_elt, 'DESCRIPTION').text = description
            etree.SubElement(analysis_elt, 'STUDY_REF', accession=study)
            for sample in samples:
                sample_ref = sample['value']
                etree.SubElement(analysis_elt, 'SAMPLE_REF',
                                 accession=sample_ref)
            for experiment in experiments:
                exp_ref = experiment['value']
                etree.SubElement(analysis_elt, 'EXPERIMENT_REF',
                                 accession=exp_ref)
            for run in runs:
                run_ref = run['value']
                etree.SubElement(analysis_elt, 'RUN_REF', accession=run_ref)
            analysis_type_elt = etree.SubElement(analysis_elt, 'ANALYSIS_TYPE')
            etree.SubElement(analysis_type_elt, analysis_type)
            files_elt = etree.SubElement(analysis_elt, 'FILES')
            for index, file_name in enumerate(file_names):
                filename = file_name['value']
                filetype = file_types[index]['value']
                checksum_method = checksum_methods[index]['value']
                checksum = checksums[index]['value']
                etree.SubElement(files_elt, 'FILE', filename=filename,
                                 filetype=filetype,
                                 checksum_method=checksum_method,
                                 checksum=checksum)
            analysis_attributes_elt = etree.SubElement(analysis_elt,
                                                       'ANALYSIS_ATTRIBUTES')
            analysis_attribute_elt = etree.SubElement(analysis_attributes_elt,
                                                      'ANALYSIS_ATTRIBUTE')
            etree.SubElement(analysis_attribute_elt, 'TAG').text = 'Project'
            etree.SubElement(analysis_attribute_elt, 'VALUE').text = project

            analysis_attribute_elt = etree.SubElement(analysis_attributes_elt,
                                                      'ANALYSIS_ATTRIBUTE')
            etree.SubElement(analysis_attribute_elt, 'TAG').text = 'Assay Type'
            etree.SubElement(analysis_attribute_elt, 'VALUE').text = assay_type

            analysis_attribute_elt = etree.SubElement(analysis_attributes_elt,
                                                      'ANALYSIS_ATTRIBUTE')
            etree.SubElement(analysis_attribute_elt,
                             'TAG').text = 'Analysis Protocol'
            etree.SubElement(analysis_attribute_elt,
                             'VALUE').text = analysis_protocol

            analysis_attribute_elt = etree.SubElement(analysis_attributes_elt,
                                                      'ANALYSIS_ATTRIBUTE')
            etree.SubElement(analysis_attribute_elt,
                             'TAG').text = 'Reference genome'
            etree.SubElement(analysis_attribute_elt,
                             'VALUE').text = reference_genome

            analysis_attribute_elt = etree.SubElement(analysis_attributes_elt,
                                                      'ANALYSIS_ATTRIBUTE')
            etree.SubElement(analysis_attribute_elt,
                             'TAG').text = 'Analysis center'
            etree.SubElement(analysis_attribute_elt,
                             'VALUE').text = analysis_center

            analysis_attribute_elt = etree.SubElement(analysis_attributes_elt,
                                                      'ANALYSIS_ATTRIBUTE')
            etree.SubElement(analysis_attribute_elt,
                             'TAG').text = 'Analysis date'
            etree.SubElement(analysis_attribute_elt,
                             'VALUE').text = analysis_date_value
            etree.SubElement(analysis_attribute_elt,
                             'UNITS').text = analysis_date_units
        analysis_xml.write(f"{self.room_id}_analysis.xml",
                           pretty_print=True, xml_declaration=True,
                           encoding='UTF-8')
        return 'Success'

    def generate_submission_xml(self):
        """
        This function will generate xml file with submission
        :return: xml file for submission
        """
        submission_set = etree.Element('SUBMISSION_SET')
        submission_xml = etree.ElementTree(submission_set)
        submission_elt = etree.SubElement(submission_set, 'SUBMISSION',
                                          alias="analysis")
        actions_elt = etree.SubElement(submission_elt, 'ACTIONS')
        action_elt = etree.SubElement(actions_elt, 'ACTION')
        etree.SubElement(action_elt, 'ADD')
        action_elt = etree.SubElement(actions_elt, 'ACTION')
        etree.SubElement(action_elt, 'RELEASE')
        submission_xml.write(f"{self.room_id}_submission.xml",
                             pretty_print=True, xml_declaration=True,
                             encoding='UTF-8')
        return 'Success'
