def get_samples_core_data(input_data):
    """
    This function gets samples core data from template file
    :param input_data: row from template
    :return: dictionary with sample core data
    """
    samples_core = dict()

    # get sample_description
    sample_description = dict()
    sample_description['value'] = input_data[1]
    samples_core['sample_description'] = sample_description

    # get material
    material = dict()
    material['term'] = input_data[5]
    material['text'] = input_data[3]
    samples_core['material'] = material

    # get project
    project = dict()
    project['value'] = input_data[2]
    samples_core['project'] = project

    # get availability
    availability = dict()
    availability['value'] = input_data[6]
    samples_core['availability'] = availability

    return samples_core
