import re


def check_biosampleid(sample_id, reg_valid_sample_ids, erroneous_sample_ids):
    """
    check if sample name is a valid BiosampleId.
    BioSample accessions always begin with SAM. The next letter is either E or N or D
    After that, there may be an A or a G to denote an Assay sample or a Group of samples.
    Finally there is a numeric component that may or may not be zero-padded.
    :param id: id to verify
    :param reg_valid_sample_ids: list containing valid biosampleIds
    :param erroneous_sample_ids: list containing erroneous biosampleIds
    :return: true or false
    """
    isValid = re.search("^SAM[AED][AG]?\d+$", sample_id)

    if isValid:
        reg_valid_sample_ids.append(sample_id)
    else:
        erroneous_sample_ids.append(sample_id)

    return reg_valid_sample_ids, erroneous_sample_ids



