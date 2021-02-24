from lxml import etree
import json

from .helpers import check_field_existence


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
            title = check_field_existence(
                'title', self.json_to_convert['ena'][record_number])
            alias = self.json_to_convert['ena'][record_number]['alias']['value']
            description = check_field_existence(
                'description', self.json_to_convert['ena'][record_number])
            study = self.json_to_convert['ena'][record_number]['study']['value']
            samples = check_field_existence(
                'samples', self.json_to_convert['ena'][record_number])
            experiments = check_field_existence(
                'experiments', self.json_to_convert['ena'][record_number])
            runs = check_field_existence(
                'runs', self.json_to_convert['ena'][record_number])
            # TODO: add related analyses
            analysis_type = self.json_to_convert['ena'][record_number][
                'analysis_type']['value']
            file_names = self.json_to_convert['ena'][record_number][
                'file_names']
            file_types = self.json_to_convert['ena'][record_number][
                'file_types']
            checksum_methods = self.json_to_convert['ena'][record_number][
                'checksum_methods']
            checksums = self.json_to_convert['ena'][record_number]['checksums']
            analysis_center = check_field_existence(
                'analysis_center', self.json_to_convert['ena'][record_number])
            analysis_date = check_field_existence(
                'analysis_date', self.json_to_convert['ena'][record_number])
            faang_alias = self.json_to_convert['faang'][record_number][
                'alias']['value']
            if faang_alias != alias:
                return 'Error'
            project = self.json_to_convert['faang'][record_number]['project'][
                'value']
            secondary_project = check_field_existence(
                'secondary_project',
                self.json_to_convert['faang'][record_number])
            assay_type = self.json_to_convert['faang'][record_number][
                'assay_type']['value']
            analysis_protocol = self.json_to_convert['faang'][record_number][
                'analysis_protocol']['value']
            analysis_code = check_field_existence(
                'analysis_code', self.json_to_convert['faang'][record_number])
            reference_genome = check_field_existence(
                'reference_genome',
                self.json_to_convert['faang'][record_number])

            analysis_elt = etree.SubElement(analysis_set, 'ANALYSIS',
                                            alias=alias)
            if title is not None:
                etree.SubElement(analysis_elt, 'TITLE').text = title['value']
            if description is not None:
                etree.SubElement(analysis_elt,
                                 'DESCRIPTION').text = description['value']
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

            if secondary_project is not None:
                # TODO: allow multiple secondary projects
                analysis_attribute_elt = etree.SubElement(
                    analysis_attributes_elt, 'ANALYSIS_ATTRIBUTE')
                etree.SubElement(analysis_attribute_elt,
                                 'TAG').text = 'Secondary Project'
                etree.SubElement(analysis_attribute_elt, 'VALUE').text = \
                    secondary_project[0]['value']

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

            if analysis_code is not None:
                analysis_attribute_elt = etree.SubElement(
                    analysis_attributes_elt, 'ANALYSIS_ATTRIBUTE')
                etree.SubElement(analysis_attribute_elt,
                                 'TAG').text = 'Analysis code'
                etree.SubElement(analysis_attribute_elt,
                                 'VALUE').text = analysis_code['value']

            if reference_genome is not None:
                analysis_attribute_elt = etree.SubElement(
                    analysis_attributes_elt, 'ANALYSIS_ATTRIBUTE')
                etree.SubElement(analysis_attribute_elt,
                                 'TAG').text = 'Reference genome'
                etree.SubElement(analysis_attribute_elt,
                                 'VALUE').text = reference_genome['value']

            if analysis_center is not None:
                analysis_attribute_elt = etree.SubElement(
                    analysis_attributes_elt, 'ANALYSIS_ATTRIBUTE')
                etree.SubElement(analysis_attribute_elt,
                                 'TAG').text = 'Analysis center'
                etree.SubElement(analysis_attribute_elt,
                                 'VALUE').text = analysis_center['value']

            if analysis_date is not None:
                analysis_attribute_elt = etree.SubElement(
                    analysis_attributes_elt, 'ANALYSIS_ATTRIBUTE')
                etree.SubElement(analysis_attribute_elt,
                                 'TAG').text = 'Analysis date'
                etree.SubElement(analysis_attribute_elt,
                                 'VALUE').text = analysis_date['value']
                etree.SubElement(analysis_attribute_elt,
                                 'UNITS').text = analysis_date['units']
        analysis_xml.write(f"{self.room_id}_analysis.xml",
                           pretty_print=True, xml_declaration=True,
                           encoding='UTF-8')
        return 'Success'

    def generate_submission_xml(self):
        """
        This function will generate xml file with submission
        :return: xml file for submission
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
