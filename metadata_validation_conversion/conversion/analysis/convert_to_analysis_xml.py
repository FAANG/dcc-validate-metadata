import xlrd
from typing import Dict, List
import pprint
'''
Convert Analysis template file into XML files which are ready to be submitted
Ideally the following steps are going to be taken
1. read in the ruleset in JSON
2. read in the XLS file according to the the ruleset and save as a Dict
3. validate the data against ruleset
4. validate the data against extra ENA rules which are not included in the FAANG ruleset
5. convert into analysis.xml and generate the submission file
Now skip step 1, 3 and 4 and write in the routine style, not OO style
'''
RECORD_KEY_COLUMNS = {
    'FAANG': ['Analysis alias'],
    'ENA': ['Analysis alias'],
    'EVA': ['Analysis alias']
}

SKIP_SHEETS = ['Readme']


def read_xls_file(filename: str):
    wb = xlrd.open_workbook(filename)
    data = dict()
    data.setdefault('values', dict())
    for sh in wb.sheets():
        sheet_name = sh.name
        # the sheets do not need to be processed
        if sheet_name in SKIP_SHEETS:
            continue
        print(f"processing sheet {sh.name}")
        data.setdefault(sheet_name, dict())
        data[sheet_name].setdefault('headers', dict())
        data[sheet_name].setdefault('keys', list())

        header_row = sh.row_values(0)
        headers = process_header(header_row)
        data[sh.name]['headers'] = headers
        data[sh.name]['keys'] = find_key_columns(header_row, RECORD_KEY_COLUMNS[sheet_name])
        print(f"{sheet_name} has {sh.nrows} rows")
        for row_number in range(1, sh.nrows):
            record = sh.row_values(row_number)
            key_value: str = ''
            record_value = dict()
            for idx, value in enumerate(record):
                if idx in data[sh.name]['keys']:
                    if value and len(value) > 0:
                        key_value = f"{key_value}|{value}"
                    else:
                        raise KeyError(f"Row {row_number} in {sheet_name} sheet has empty value "
                                       f"for key column {header_row[idx]}")
                # empty value gets skipped
                if value and len(value) > 0:
                    column_name = headers[idx]
                    record_value.setdefault(column_name, list())
                    record_value[column_name].append(value)
            key_value = key_value[1:]
            data['values'].setdefault(key_value, dict())
            data['values'][key_value].setdefault(sheet_name, dict())
            data['values'][key_value][sheet_name] = record_value
    # end of iteration all sheets in the xls file
    return data

def find_key_columns(raw_headers: List, key_list: List) -> List:
    if type(raw_headers) is not list:
        raise TypeError("raw headers parameter is not a list of strings")
    if type(key_list) is not list:
        raise TypeError("key_list is not a list of strings")
    for col in raw_headers+key_list:
        if type(col) is not str:
            raise TypeError(f"The element of either raw header list or key list must be a string {col}")
    key_indices = list()
    for idx, value in enumerate(raw_headers):
        if value in key_list:
            key_indices.append(idx)
    if len(key_list) > len(key_indices):
        raise ValueError('Not all listed keys have been located')
    elif len(key_list) < len(key_indices):
        raise ValueError('At least one of the key columns have been duplicated')
    else:
        return key_indices


def process_header(raw_headers: List) -> Dict:
    processed_headers: Dict[int, str]= dict()
    for idx, value in enumerate(raw_headers):
        if value == 'Unit' or value == 'Units':
            value = f"{raw_headers[idx-1]}-unit"
        elif value == 'Term Source REF':
            value = f"{raw_headers[idx-1]}-ontology_library"
        elif value == 'Term Source ID':
            value = f"{raw_headers[idx-2]}-ontology_term"
        processed_headers[idx] = value
    return processed_headers


def process_data(data):
    pass


def convert_to_analysis_xml(data: Dict):
    result = '<?xml version="1.0" encoding="UTF-8"?>\n<ANALYSIS_SET>\n'
    for record_id in data['values'].keys():
        result = result + f'\t<ANALYSIS alias="{record_id}">\n'
        result = result + f'\t\t<TITLE>{data["values"][record_id]["ENA"]["Title"][0]}</TITLE>\n'
        result = result + f'\t\t<DESCRIPTION>{data["values"][record_id]["ENA"]["description"][0]}</DESCRIPTION>\n'
        result = result + f'\t\t<STUDY_REF accession=\"{data["values"][record_id]["ENA"]["STUDY_REF"][0]}\"/>\n'
        for sample in data["values"][record_id]["ENA"]["SAMPLE_DESCRIPTOR"]:
            result = result + f'\t\t<SAMPLE_REF accession=\"{sample}\"/>\n'
        for exp in data["values"][record_id]["ENA"]["EXPERIMENT_alias"]:
            result = result + f'\t\t<EXPERIMENT_REF accession=\"{exp}\"/>\n'
        for run in data["values"][record_id]["ENA"]["RUN_alias"]:
            result = result + f'\t\t<RUN_REF accession=\"{run}\"/>\n'
        analysis_type = data["values"][record_id]["ENA"]["Analysis type"][0]
        # TODO: check EVA sheet, extra columns
        # if analysis_type == 'SEQUENCE_VARIATION':
        # TODO no ruleset for sequence assembly, genome map types yet, extra mandatory fields required
        # elif analysis_type == 'SEQUENCE_ASSEMBLY':
        result = result + f'\t\t<ANALYSIS_TYPE>\n' \
                          f'\t\t\t<{analysis_type}>\n' \
                          f'\t\t\t</{analysis_type}>\n' \
                          f'\t\t</ANALYSIS_TYPE>\n'
        result = result + '\t\t<FILES>\n'
        for idx, file_name in enumerate(data["values"][record_id]["ENA"]["file names"]):
            result = result + f'\t\t\t<FILE filename=\"{file_name}\" ' \
                              f'filetype=\"{data["values"][record_id]["ENA"]["file types"][idx]}\" ' \
                              f'checksum_method=\"{data["values"][record_id]["ENA"]["checksum methods"][idx]}\" ' \
                              f'checksum=\"{data["values"][record_id]["ENA"]["checksums"][idx]}\"/>\n'
        result = result + '\t\t</FILES>\n'

        result = result + '\t\t<ANALYSIS_ATTRIBUTES>\n'
        for idx, col_name in enumerate(data["values"][record_id]["FAANG"].keys()):
            if idx in data['FAANG']['keys']:
                continue
            result = result + f'\t\t\t<ANALYSIS_ATTRIBUTE>\n\t\t\t\t<TAG>{col_name}</TAG>\n' \
                              f'\t\t\t\t<VALUE>{data["values"][record_id]["FAANG"][col_name][0]}</VALUE>' \
                              f'\n\t\t\t</ANALYSIS_ATTRIBUTE>\n'
        # optional, no multiple allowed
        if 'analysis center' in data["values"][record_id]["ENA"]:
            result = result + f'\t\t\t<ANALYSIS_ATTRIBUTE>\n\t\t\t\t<TAG>Analysis center</TAG>\n' \
                          f'\t\t\t\t<VALUE>{data["values"][record_id]["ENA"]["analysis center"][0]}</VALUE>' \
                          f'\n\t\t\t</ANALYSIS_ATTRIBUTE>\n'
        if 'analysis date' in data["values"][record_id]["ENA"]:
            result = result + f'\t\t\t<ANALYSIS_ATTRIBUTE>\n\t\t\t\t<TAG>Analysis date</TAG>\n' \
                          f'\t\t\t\t<VALUE>{data["values"][record_id]["ENA"]["analysis date"][0]}</VALUE>\n' \
                          f'\t\t\t\t<UNITS>{data["values"][record_id]["ENA"]["analysis date-unit"][0]}</UNITS>\n' \
                              f'\t\t\t</ANALYSIS_ATTRIBUTE>\n'

        result = result + '\t\t</ANALYSIS_ATTRIBUTES>\n'
        result = result + '\t</ANALYSIS>\n'
    result = result + '</ANALYSIS_SET>'
    return result


def generate_submission_xml(alias):
    result = '<?xml version="1.0" encoding="UTF-8"?>\n'
    result = result + f'<SUBMISSION_SET>\n\t<SUBMISSION alias=\"{alias}\">\n'
    result = result + '\t\t<ACTIONS>\n\t\t\t<ACTION>\n\t\t\t\t<ADD/>\n\t\t\t</ACTION>\n'
    result = result + '\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n\t\t</ACTIONS>\n'
    result = result + '\t</SUBMISSION>\n</SUBMISSION_SET>\n'
    return result


if __name__ == '__main__':
    filename = 'faang_analysis_metadata_equine_UCD_20191109.xlsx'
    suffix_loc = filename.lower().rindex('.xls')
    filename_base = filename[:suffix_loc]
    data = read_xls_file(filename)
    # processed_data = process_data(data)
    # convert_to_analysis_xml(processed_data)
    analysis_xml = convert_to_analysis_xml(data)
    submission_xml = generate_submission_xml(filename_base)
    with open(f"{filename}.analysis.xml", 'w') as w:
        w.write(analysis_xml)
    with open(f"{filename}.submission.xml", 'w') as w:
        w.write(submission_xml)
