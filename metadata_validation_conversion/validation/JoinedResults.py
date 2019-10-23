from .helpers import get_validation_results_structure


class JoinedResults:
    def __init__(self, results):
        self.results = results

    def join_results(self):
        joined_results = dict()
        for record_type in self.results[0]:
            joined_results.setdefault(record_type, list())
            for index, first_record in enumerate(self.results[0][record_type]):
                second_record = self.results[1][record_type][index]
                third_record = self.results[2][record_type][index]
                tmp = get_validation_results_structure(first_record['name'])
                tmp = self.join_issues(tmp, first_record, second_record,
                                       third_record)
                joined_results[record_type].append(tmp)
        return joined_results

    @staticmethod
    def join_issues(to_join_to, first_record, second_record, third_record):
        """
        This function will join all issues from first and second record into one
        place
        :param to_join_to: holder that will store merged issues
        :param first_record: first record to get issues from
        :param second_record: second record to get issues from
        :param third_record: third record to get issues from
        :return: merged results
        """
        for issue_type in ['core', 'type', 'custom']:
            for issue in ['errors', 'warnings']:
                to_join_to[issue_type][issue].extend(
                    first_record[issue_type][issue])
                to_join_to[issue_type][issue].extend(
                    second_record[issue_type][issue])
                to_join_to[issue_type][issue].extend(
                    third_record[issue_type][issue])
        return to_join_to
