from metadata_validation_conversion.constants import MODULE_SHEET_NAMES
from .helpers import get_validation_results_structure


class JoinedResults:
    def __init__(self, results):
        self.results = results

    def join_results(self):
        joined_results = dict()
        number_of_results = len(self.results)
        for record_type in self.results[0]:
            joined_results.setdefault(record_type, list())
            for index, first_record in enumerate(self.results[0][record_type]):
                records = list()
                for i in range(0, number_of_results):
                    records.append(self.results[i][record_type][index])
                tmp = get_validation_results_structure(first_record['name'],
                                                       record_type in
                                                       MODULE_SHEET_NAMES)
                tmp = self.join_issues(tmp, *records)
                joined_results[record_type].append(tmp)
        return joined_results

    @staticmethod
    def join_issues(to_join_to, *records):
        """
        This function will join all issues into one result structure
        :param to_join_to: holder that will store merged issues
        :param records: list of records to join
        :return: merged results
        """
        for issue_type in ['core', 'type', 'custom', 'module']:
            for issue in ['errors', 'warnings']:
                for record in records:
                    if issue_type in to_join_to and issue_type in record:
                        to_join_to[issue_type][issue].extend(
                            record[issue_type][issue])
        return to_join_to
