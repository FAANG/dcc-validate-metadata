import datetime
import requests
from metadata_validation_conversion.constants import \
    SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES, ADDITIONAL_INFO_MAPPING
from validation.helpers import get_record_name
from submission.helpers import remove_underscores
from .helpers import get_header


class BiosamplesFileConverter:
    def __init__(self, json_to_convert, private):
        self.json_to_convert = json_to_convert
        self.private_submission = private

    def start_conversion(self):
        data_to_send = list()
        taxon_ids, taxons = self.get_taxon_information()
        # If private submission move date for two years in the future
        if self.private_submission:
            two_years = datetime.timedelta(days=365) * 2
            date = (datetime.datetime.now() + two_years).isoformat()
        else:
            date = datetime.datetime.now().isoformat()
        # Collect additional data, submission information
        additional_fields = dict()
        for additional_field in SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES:
            if additional_field in ['person', 'organization']:
                continue
            for item in self.json_to_convert[additional_field]:
                for existing_field, existing_value in item.items():
                    additional_fields.setdefault(
                        remove_underscores(existing_field), list())
                    additional_fields[remove_underscores(
                        existing_field)].append({'text': existing_value})
        organization_info = self.get_additional_data('organization')
        person_info = self.get_additional_data('person')
        for record_type, records in self.json_to_convert.items():
            if record_type in SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES:
                continue
            for record_index, record in enumerate(records):
                record_name = get_record_name(record, record_index, record_type)
                data_to_send.append(
                    {
                        "name": record_name,
                        "release": date,
                        "contact": person_info,
                        "organization": organization_info,
                        "characteristics": self.get_sample_attributes(
                            record, additional_fields, taxon_ids, taxons,
                            record_name),
                        "relationships": self.get_sample_relationships(
                            record, record_name)
                    }
                )
        return data_to_send

    def get_taxon_information(self):
        """
        This function will parse whole json to get all taxon ids
        :return: dict with id as key and taxon id as value
        """
        taxon_ids = dict()
        taxons = dict()
        missing_ids = dict()
        for record_type, records in self.json_to_convert.items():
            if record_type in SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES:
                continue
            for record_index, record in enumerate(records):
                record_name = get_record_name(record, record_index, record_type)
                if 'organism' in record:
                    taxon_ids[record_name] = \
                        record['organism']['term']
                    taxons[record_name] = record['organism']['text']
                elif 'derived_from' in record:
                    if isinstance(record['derived_from'], dict):
                        missing_ids[record_name] = \
                            record['derived_from']['value']
                    elif isinstance(record['derived_from'], list):
                        missing_ids[record_name] = \
                            record['derived_from'][0]['value']
        for id_to_fetch in missing_ids:
            taxon_ids[id_to_fetch], taxons[id_to_fetch] = \
                self.fetch_taxon_information(id_to_fetch, taxon_ids,
                                             taxons, missing_ids)
        return taxon_ids, taxons

    def fetch_taxon_information(self, id_to_fetch, taxon_ids, taxons,
                                missing_ids):
        """
        This function will find taxon id for particular record
        :param id_to_fetch: id to check
        :param taxon_ids: existing taxon ids
        :param taxons: existing taxons
        :param missing_ids: missing taxon ids
        :return:
        """
        if id_to_fetch in taxon_ids and id_to_fetch in taxons:
            return taxon_ids[id_to_fetch], taxons[id_to_fetch]
        else:
            # TODO: return error in taxon is not in biosamples
            # check that id is Biosample id
            if 'SAM' in id_to_fetch and '_' not in id_to_fetch:
                try:
                    results = requests.get(
                        f"https://www.ebi.ac.uk/biosamples/samples/"
                        f"{id_to_fetch}").json()
                    return results['taxId'], results['characteristics'][
                        'organism'][0]['text']
                except ValueError:
                    pass
                except KeyError:
                    results = requests.get(
                        f"https://www.ebi.ac.uk/biosamples/samples/"
                        f"{id_to_fetch}", headers=get_header()).json()
                    return results['taxId'], results['characteristics'][
                        'organism'][0]['text']
            else:
                return self.fetch_taxon_information(missing_ids[id_to_fetch],
                                                    taxon_ids,
                                                    taxons,
                                                    missing_ids)

    def get_additional_data(self, key):
        additional_data = list()
        for item in self.json_to_convert[key]:
            tmp = dict()
            for existing_field, existing_value in item.items():
                tmp[ADDITIONAL_INFO_MAPPING[existing_field]] = existing_value
            additional_data.append(tmp)
        return additional_data

    @staticmethod
    def get_sample_relationships(record, record_name):
        """
        This function will parse record and find all relationships
        :param record: record to parse
        :param record_name: name of the current record
        :return: list of all relationships
        """
        sample_relationships = list()
        if 'same_as' in record:
            sample_relationships.append(
                {
                    "source": record_name,
                    "type": "same as",
                    "target": record['same_as']['value']
                }
            )
        if 'child_of' in record:
            for child in record['child_of']:
                sample_relationships.append(
                    {
                        "source": record_name,
                        "type": "child of",
                        "target": child['value']
                    }
                )
        if 'derived_from' in record:
            if isinstance(record['derived_from'], list):
                for child in record['derived_from']:
                    sample_relationships.append(
                        {
                            "source": record_name,
                            "type": "derived from",
                            "target": child['value']
                        }
                    )
            elif isinstance(record['derived_from'], dict):
                sample_relationships.append(
                    {
                        "source": record_name,
                        "type": "derived from",
                        "target": record['derived_from']['value']
                    }
                )
        return sample_relationships

    def get_sample_attributes(self, record, additional_fields, taxon_ids,
                              taxons, record_name):
        """
        This function will return biosample attributes
        :param record: record to parse
        :param additional_fields: additional fields to add to dict
        :param taxon_ids: dict with taxon ids
        :param taxons: dict with taxon names
        :param record_name: name of the current record
        :return: attributes for this record in biosample format
        """
        sample_attributes = dict()
        for attribute_name, attribute_value in record.items():
            if attribute_name == 'samples_core':
                for sc_attribute_name, sc_attribute_value in \
                        record['samples_core'].items():
                    sample_attributes[remove_underscores(sc_attribute_name)] = \
                        self.parse_attribute(sc_attribute_value)
            elif attribute_name == 'custom':
                for sc_attribute_name, sc_attribute_value in \
                        record['custom'].items():
                    sample_attributes[remove_underscores(sc_attribute_name)] = \
                        self.parse_attribute(sc_attribute_value)
            elif attribute_name == 'teleostei_post-hatching':
                for sc_attribute_name, sc_attribute_value in \
                        record['teleostei_post-hatching'].items():
                    sample_attributes[remove_underscores(sc_attribute_name)] = \
                        self.parse_attribute(sc_attribute_value)
            elif attribute_name == 'teleostei_embryo':
                for sc_attribute_name, sc_attribute_value in \
                        record['teleostei_embryo'].items():
                    sample_attributes[remove_underscores(sc_attribute_name)] = \
                        self.parse_attribute(sc_attribute_value)
            else:
                sample_attributes[remove_underscores(attribute_name)] = \
                    self.parse_attribute(attribute_value)
        sample_attributes.update(additional_fields)
        # BioSamples require for every sample to have organism object
        if 'organism' not in sample_attributes:
            if ':' in str(taxon_ids[record_name]):
                taxon_id = "_".join(taxon_ids[record_name].split(":"))
            else:
                # Need this to create appropriate taxon id from BioSamples id
                taxon_id = f"NCBITaxon_{taxon_ids[record_name]}"
            organism_object = {
                'text': taxons[record_name],
                'ontologyTerms': [f"http://purl.obolibrary.org/obo/{taxon_id}"]
            }
            sample_attributes['organism'] = [organism_object]
        if self.private_submission:
            sample_attributes['BovReg private submission'] = [{'text': 'TRUE'}]
        return sample_attributes

    def parse_attribute(self, value_to_parse):
        """
        This function will parse single attribute from data
        :param value_to_parse: data to parse
        :return: attributes list
        """
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
        """
        This function will parse single fields
        :param value_to_parse: field to parse
        :return: dict of attributes
        """
        attribute = dict()
        if 'text' in value_to_parse:
            attribute['text'] = value_to_parse['text']
        elif 'value' in value_to_parse:
            attribute['text'] = value_to_parse['value']

        if 'term' in value_to_parse:
            ontology_url = "_".join(value_to_parse['term'].split(":"))
            attribute['ontologyTerms'] = [
                f"http://purl.obolibrary.org/obo/{ontology_url}"]

        if 'units' in value_to_parse:
            attribute['unit'] = value_to_parse['units']
        return attribute
