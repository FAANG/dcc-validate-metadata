class JoinedResults:
    def __init__(self, results):
        self.results = results

    def join_results(self):
        joined_results = dict()
        number_of_results = len(self.results)
        for record_type in self.results[0]:
            if record_type == 'table':
                continue
            joined_results.setdefault(record_type, list())
            for index, first_record in enumerate(self.results[0][record_type]):
                records = list()
                for i in range(0, number_of_results):
                    records.append(self.results[i][record_type][index])
                tmp = self.join_record(*records)
                joined_results[record_type].append(tmp)
        return joined_results

    @staticmethod
    def join_record(*records):
        """
        This function will join all issues into one result structure
        :param records: list of records to join
        :return: merged results
        """
        results_to_return = dict()
        for record in records:
            for name, value in record.items():
                if name == 'samples_core' or name == 'custom':
                    results_to_return.setdefault(name, dict())
                    for k, v in record[name].items():
                        # TODO: check that v is array
                        results_to_return[name].setdefault(k, dict())
                        results_to_return[name][k].update(v)
                else:
                    if isinstance(value, dict):
                        results_to_return.setdefault(name, dict())
                        results_to_return[name].update(value)
                    else:
                        results_to_return.setdefault(name, list())
                        for index, item in enumerate(value):
                            try:
                                results_to_return[name][index].update(item)
                            except IndexError:
                                results_to_return[name].append(item)
        return results_to_return

