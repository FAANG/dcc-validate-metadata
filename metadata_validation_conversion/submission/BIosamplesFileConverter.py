from datetime import datetime


class BiosamplesFileConverter:
    def __init__(self, json_to_convert):
        self.json_to_convert = json_to_convert

    def start_conversion(self):
        data_to_send = list()
        taxon_ids = self.get_all_taxon_ids()
        current_date = datetime.now().strftime("%Y-%m-%d")
        for record_type, records in self.json_to_convert.items():
            for record in records:
                # TODO get name from function
                record_name = record['custom']['sample_name']['value']
                data_to_send.append(
                    {
                        "alias": record_name,
                        "title": record_name,
                        "releaseDate": current_date,
                        "taxonId": taxon_ids[record_name],
                        "attributes": self.get_sample_attributes(record),
                        "samplesRelationships": self.get_sample_relationships(
                            record)
                    }
                )
        return data_to_send

    def get_all_taxon_ids(self):
        """
        This function will parse whole json to get all taxon ids
        :return: dict with id as key and taxon id as value
        """
        taxon_ids = dict()
        missing_ids = dict()
        for record_type, records in self.json_to_convert.items():
            for record in records:
                # TODO get name from function
                record_name = record['custom']['sample_name']['value']
                if 'organism' in record:
                    taxon_ids[record_name] = \
                        record['organism']['term'].split(":")[1]
                elif 'derived_from' in record:
                    if isinstance(record['derived_from'], dict):
                        missing_ids[record_name] = \
                            record['derived_from']['value']
                    elif isinstance(record['derived_from'], list):
                        missing_ids[record_name] = \
                            record['derived_from'][0]['value']
                    else:
                        # TODO return an error
                        pass
                else:
                    # TODO return an error
                    pass
        for id_to_fetch in missing_ids:
            taxon_ids[id_to_fetch] = self.fetch_id(id_to_fetch, taxon_ids,
                                                   missing_ids)
        return taxon_ids

    def fetch_id(self, id_to_fetch, taxon_ids, missing_ids):
        """
        This function will find taxon id for particular record
        :param id_to_fetch: id to check
        :param taxon_ids: existing taxon ids
        :param missing_ids: missing taxon ids
        :return:
        """
        # TODO add biosamples check
        if id_to_fetch in taxon_ids:
            return taxon_ids[id_to_fetch]
        else:
            return self.fetch_id(missing_ids[id_to_fetch], taxon_ids,
                                 missing_ids)

    @staticmethod
    def get_sample_relationships(record):
        """
        This function will parse record and find all relationships
        :param record: record to parse
        :return: list of all relationships
        """
        sample_relationships = list()
        if 'same_as' in record:
            sample_relationships.append(
                {
                    "alias": record['same_as']['value'],
                    "relationshipNature": "same as"
                }
            )
        if 'child_of' in record:
            for child in record['child_of']:
                sample_relationships.append(
                    {
                        "alias": child['value'],
                        "relationshipNature": "child of"
                    }
                )
        if 'derived_from' in record:
            if isinstance(record['derived_from'], list):
                for child in record['derived_from']:
                    sample_relationships.append(
                        {
                            "alias": child['value'],
                            "relationshipNature": "derived from"
                        }
                    )
            elif isinstance(record['derived_from'], dict):
                sample_relationships.append(
                    {
                        "alias": record['derived_from']['value'],
                        "relationshipNature": "derived from"
                    }
                )
        return sample_relationships

    def get_sample_attributes(self, record):
        """
        This function will return biosample attributes
        :param record: record to parse
        :return: attributes for this record in biosample format
        """
        sample_attributes = dict()
        for attribute_name, attribute_value in record.items():
            if attribute_name == 'samples_core':
                for sc_attribute_name, sc_attribute_value in \
                        record['samples_core'].items():
                    sample_attributes[sc_attribute_name] = \
                        self.parse_attribute(sc_attribute_value)
            elif attribute_name == 'custom':
                for sc_attribute_name, sc_attribute_value in \
                        record['custom'].items():
                    sample_attributes[sc_attribute_name] = \
                        self.parse_attribute(sc_attribute_value)
            else:
                sample_attributes[attribute_name] = self.parse_attribute(
                    attribute_value)
        return sample_attributes

    def parse_attribute(self, value_to_parse):
        attributes = list()

        if isinstance(value_to_parse, list):
            for sc_value_to_parse in value_to_parse:
                attributes.append(
                    self.parse_value_in_attribute(sc_value_to_parse)
                )
        elif isinstance(value_to_parse, dict):
            attributes.append(
                self.parse_value_in_attribute(value_to_parse)
            )
        return attributes

    @staticmethod
    def parse_value_in_attribute(value_to_parse):
        attribute = dict()
        if 'text' in value_to_parse:
            attribute['value'] = value_to_parse['text']
        elif 'value' in value_to_parse:
            attribute['value'] = value_to_parse['value']

        if 'term' in value_to_parse:
            ontology_url = "_".join(value_to_parse['term'].split(":"))
            attribute['terms'] = [
                {
                    "url": f"http://purl.obolibrary.org/obo/{ontology_url}"
                }
            ]

        if 'units' in value_to_parse:
            attribute['units'] = value_to_parse['units']
        return attribute
