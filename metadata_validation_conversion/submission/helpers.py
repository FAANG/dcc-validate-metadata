import io
import zipfile


def zip_files(files, output_type):
    """
    This function will extract files from tuple and zip it in one archive
    :param files: files to extract and zip
    :param output_type: type of conversion
    :return: zip archive
    """
    analysis_files = ['analysis.xml', 'submission.xml']
    experiments_files = ['experiment.xml', 'run.xml', 'study.xml',
                         'submission.xml']
    if output_type == 'analysis':
        file_names = analysis_files
    else:
        file_names = experiments_files
    outfile = io.BytesIO()
    with zipfile.ZipFile(outfile, 'w') as zf:
        for n, f in enumerate(files):
            zf.writestr(file_names[n], f)
    return outfile.getvalue()


def check_field_existence(field_to_check, record_to_check):
    """
    This function will check for existence of field in record
    :param field_to_check: field to search for
    :param record_to_check: record to search field in
    :return:
    """
    if field_to_check in record_to_check:
        return record_to_check[field_to_check]
    else:
        return None


def remove_underscores(value_to_convert):
    """
    This function will return value without underscores
    :param value_to_convert: value to convert
    :return: value with spaces instead of underscores
    """
    return " ".join(value_to_convert.split("_"))


def convert_to_uppercase(value_to_convert):
    """
    This function will convert column names to uppercase
    :param value_to_convert: value to be converted
    :return: value in uppercase
    """
    return ' '.join([word.capitalize() for word in value_to_convert.split('_')])
