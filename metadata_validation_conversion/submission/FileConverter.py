import datetime

from lxml import etree


class FileConverter:
    def __init__(self, json_to_convert, room_id, action="submission"):
        self.json_to_convert = json_to_convert
        self.room_id = room_id
        self.proxy_samples_mappings = dict()
        self.action = action

    def generate_submission_xml(self):
        """
        This function will generate xml file for submission
        :return: submission xml file
        """
        if 'submission' not in self.json_to_convert:
            return 'Error: table should have submission sheet'
        submission_set = etree.Element('SUBMISSION_SET')
        submission_xml = etree.ElementTree(submission_set)
        filename = f"{self.room_id}_submission.xml"
        for record in self.json_to_convert['submission']:
            submission_elt = etree.SubElement(submission_set,
                                              'SUBMISSION',
                                              alias=record['alias'])
            actions_elt = etree.SubElement(submission_elt, 'ACTIONS')
            action_elt = etree.SubElement(actions_elt, 'ACTION')

            if self.action == 'update':
                etree.SubElement(action_elt, 'MODIFY')
            else:
                etree.SubElement(action_elt, 'ADD')
                # Release immediately (public submission)
                action_elt = etree.SubElement(actions_elt, 'ACTION')
                etree.SubElement(action_elt, 'RELEASE')

        submission_xml.write(filename, pretty_print=True,
                             xml_declaration=True, encoding='UTF-8')
        return 'Success'
