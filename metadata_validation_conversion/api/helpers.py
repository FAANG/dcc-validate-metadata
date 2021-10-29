import pandas as pd


def generate_df(field_name, column_name, data):
    """
    This function will generate tables with summary
    :param field_name: field name to parse
    :param column_name: column name to use in result table
    :param data: data to parse
    :return: results in pandas format as tables
    """
    data_all = dict()
    data_faang_only = dict()
    for name in [field_name, "{}FAANGOnly".format(field_name)]:
        tmp = data_all if name == field_name else data_faang_only
        for item in data[name]:
            tmp.setdefault(column_name, list())
            tmp.setdefault('Number', list())
            tmp[column_name].append(item['name'])
            tmp['Number'].append(item['value'])
    df = pd.DataFrame(data_all, columns=[column_name, 'Number'])
    df_faang_only = pd.DataFrame(data_faang_only, columns=[column_name,
                                                           'Number'])
    return df, df_faang_only


def generate_df_for_breeds(field_name, column_name, data):
    """
    This function will generate tables with summary (specific for breeds data)
    :param field_name: field name to parse
    :param column_name: column name to use in result table
    :param data: data to parse
    :return: results in pandas format as tables
    """
    data_all = dict()
    data_faang_only = dict()
    for name in [field_name, "{}FAANGOnly".format(field_name)]:
        tmp = data_all if name == field_name else data_faang_only
        for item in data[name]:
            for sc_item in item['speciesValue']:
                tmp.setdefault(column_name, list())
                tmp.setdefault('Number', list())
                tmp[column_name].append(sc_item['breedsName'])
                tmp['Number'].append(sc_item['breedsValue'])
    df = pd.DataFrame(data_all, columns=[column_name, 'Number'])
    df_faang_only = pd.DataFrame(data_faang_only, columns=[column_name,
                                                           'Number'])
    return df, df_faang_only
