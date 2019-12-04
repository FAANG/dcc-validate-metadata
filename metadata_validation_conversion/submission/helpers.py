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
    experiments_files = ['test.xml']
    if output_type == 'analysis':
        file_names = analysis_files
    else:
        file_names = experiments_files
    outfile = io.BytesIO()
    with zipfile.ZipFile(outfile, 'w') as zf:
        for n, f in enumerate(files):
            zf.writestr(file_names[n], f)
    return outfile.getvalue()
