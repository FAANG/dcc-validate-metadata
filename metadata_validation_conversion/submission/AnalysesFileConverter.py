from lxml import etree

from .helpers import check_field_existence
from .FileConverter import FileConverter


class AnalysesFileConverter(FileConverter):
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
            analysis_type = self.json_to_convert['ena'][record_number][
                'analysis_type']['value']
            description = check_field_existence(
                'description', self.json_to_convert['ena'][record_number])
            study = self.json_to_convert['ena'][record_number]['study']['value']
            samples = check_field_existence(
                'samples', self.json_to_convert['ena'][record_number])
            experiments = check_field_existence(
                'experiments', self.json_to_convert['ena'][record_number])
            runs = check_field_existence(
                'runs', self.json_to_convert['ena'][record_number])
            related_analyses = check_field_existence(
                'related_analyses', self.json_to_convert['ena'][record_number])
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
                return 'Error: Experiment alias is not consistent between ' \
                       'ENA and FAANG tabs'
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
            if samples is not None:
                for sample in samples:
                    sample_ref = sample['value']
                    etree.SubElement(analysis_elt, 'SAMPLE_REF',
                                     accession=sample_ref)
            if experiments is not None:
                for experiment in experiments:
                    exp_ref = experiment['value']
                    etree.SubElement(analysis_elt, 'EXPERIMENT_REF',
                                     accession=exp_ref)
            if runs is not None:
                for run in runs:
                    run_ref = run['value']
                    etree.SubElement(analysis_elt, 'RUN_REF', accession=run_ref)

            if related_analyses is not None:
                for analysis in related_analyses:
                    analysis_ref = analysis['value']
                    etree.SubElement(analysis_elt, 'ANALYSIS_REF',
                                     accession=analysis_ref)

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
                for item in secondary_project:
                    analysis_attribute_elt = etree.SubElement(
                        analysis_attributes_elt, 'ANALYSIS_ATTRIBUTE')
                    etree.SubElement(analysis_attribute_elt,
                                     'TAG').text = 'Secondary Project'
                    etree.SubElement(analysis_attribute_elt, 'VALUE').text = \
                        item['value']

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
