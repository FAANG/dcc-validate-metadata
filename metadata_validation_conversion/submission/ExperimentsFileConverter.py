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
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result

    def generate_study_xml(self):
        """
        This function will generate xml file for study
        :return: study xml file
        """
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result

    def generate_submission_xml(self):
        """
        This function will generate xml file for submission
        :return: submission xml file
        """
        result = '<?xml version="1.0" encoding="UTF-8"?>\n'
        result += '<SUBMISSION_SET>\n\t<SUBMISSION alias=\"analysis\">\n'
        result += '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t' \
                  '</ACTION>\n'
        result += '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t' \
                  '</ACTIONS>\n'
        result += '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
        return result
