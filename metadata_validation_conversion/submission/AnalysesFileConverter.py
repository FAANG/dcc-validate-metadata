class AnalysesFileConverter:
    def __init__(self, json_to_convert):
        self.json_to_convert = json_to_convert

    def start_conversion(self):
        analysis_xml = self.generate_analysis_xml()
        submission_xml = self.generate_submission_xml()
        return analysis_xml, submission_xml

    @staticmethod
    def generate_analysis_xml():
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result

    @staticmethod
    def generate_submission_xml():
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result
