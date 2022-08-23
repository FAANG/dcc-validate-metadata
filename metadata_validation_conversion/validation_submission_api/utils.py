from metadata_validation_conversion.constants import ALLOWED_TEMPLATES
from conversion.ReadExcelFile import ReadExcelFile

def convert_template(file, type):
    errors = []
    if type not in ALLOWED_TEMPLATES:
        errors.append('This type is not supported')
        return {'status': 'Error','error': errors}
    read_excel_file_object = ReadExcelFile(
        file_path=file, json_type=type)
    results = read_excel_file_object.start_conversion()
    if 'Error' in results[0]:
        errors.append(results[0])
        return {'status': 'Error', 'error': errors, 'result': results}
    else:
        if results[2]:
            return {'status': 'Success', 'result': results, 'bovreg_submission': True}
        else:
            return {'status': 'Success', 'result': results, 'bovreg_submission': False}
    