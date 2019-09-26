


def get_samples_core_data(input_data):
    """
    This function will fetch information about core sample
    :param input_data: row from template to fetch information from
    :return: dict with required information
    """
    samples_core = dict()

    # get sample_description
    samples_core['sample_description'] = get_data(input_data, **{'value': 1})
    # get material
    samples_core['material'] = get_data(input_data, **{'term': 5, 'text': 3})
    # get project
    samples_core['project'] = get_data(input_data, **{'value': 2})
    # get availability
    samples_core['availability'] = get_data(input_data, **{'value': 6})

    return samples_core


def get_organism_data(input_data):
    """
    This function will fetch information about organism
    :param input_data: row from template to fetch information from
    :return: dict with required information
    """
    organism_to_validate = dict()
    organism_to_validate['samples_core'] = get_samples_core_data(input_data)

    # get organism
    check_existence('organism', organism_to_validate,
                    get_data(input_data, **{'term': 9, 'text': 7}))

    # get sex
    check_existence('sex', organism_to_validate,
                    get_data(input_data, **{'term': 14, 'text': 12}))

    # get birth_date
    check_existence('birth_date', organism_to_validate,
                    get_data(input_data, **{'value': 21, 'units': 22}))

    # get breed
    check_existence('breed', organism_to_validate,
                    get_data(input_data, **{'term': 17, 'text': 15}))

    # get health_status
    check_existence('health_status', organism_to_validate,
                    get_data(input_data, **{'term': 20, 'text': 18}))

    # get birth_location
    check_existence('birth_location', organism_to_validate,
                    get_data(input_data, **{'value': 23}))

    # get birth_location_latitude
    check_existence('birth_location_latitude', organism_to_validate,
                    get_data(input_data, **{'value': 25, 'units': 26}))

    # get birth_location_longitude
    check_existence('birth_location_longitude', organism_to_validate,
                    get_data(input_data, **{'value': 27, 'units': 28}))

    # get birth_weight
    check_existence('birth_weight', organism_to_validate,
                    get_data(input_data, **{'value': 29, 'units': 30}))

    # get placental_weight
    check_existence('placental_weight', organism_to_validate,
                    get_data(input_data, **{'value': 31, 'units': 32}))

    # get pregnancy_length
    check_existence('pregnancy_length', organism_to_validate,
                    get_data(input_data, **{'value': 33, 'units': 34}))

    # get delivery_timing
    check_existence('delivery_timing', organism_to_validate,
                    get_data(input_data, **{'value': 36}))

    # get delivery_ease
    check_existence('delivery_ease', organism_to_validate,
                    get_data(input_data, **{'value': 35}))

    # get child_of
    parent1 = get_data(input_data, **{'value': 10})
    parent2 = get_data(input_data, **{'value': 11})
    parents = list()
    if parent1 is not None:
        parents.append(parent1)
    if parent2 is not None:
        parents.append(parent2)
    if len(parents) > 0:
        organism_to_validate['child_of'] = parents

    # get pedigree
    check_existence('pedigree', organism_to_validate,
                    get_data(input_data, **{'value': 37}))

    return organism_to_validate


def get_data(input_data, **fields):
    """
    This function will create dict with required fields and required information
    :param input_data: row from template
    :param fields: dict with field name as key and field index as value
    :return: dict with required information
    """
    data_to_return = dict()
    for field_name, field_index in fields.items():
        if input_data[field_index] == '':
            return None
        else:
            data_to_return[field_name] = input_data[field_index]
    return data_to_return


def check_existence(field_name, data_to_validate, template_data):
    """
    This function will check whether template_data has required field
    :param field_name: name of field
    :param data_to_validate: data dict for validation
    :param template_data: template data to check
    """
    if template_data is not None:
        data_to_validate[field_name] = template_data
