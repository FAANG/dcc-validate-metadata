import subprocess
import hashlib
import os
import json

class FireAPI:
    def __init__(self, username, password, filepath, firepath, filename):
        self.username = username
        self.password = password
        self.filepath = filepath
        self.filename = filename
        self.firepath = f"ftp/trackhubregistry/{firepath}"
        self.fire_api = 'https://hh.fire.sdo.ebi.ac.uk/fire/objects'

    def upload_object(self):
        """This function will upload object to Fire database"""
        cmd = f"curl {self.fire_api} -F file=@{self.filepath} " \
            f"-u {self.username}:{self.password} " \
              f"-H 'x-fire-size: {self.get_file_size()}' " \
              f"-H 'x-fire-md5: {self.get_md5_of_file()}'"
        upload_file_process = subprocess.run(cmd, shell=True,
                                             capture_output=True)
        try:
            fire_id = json.loads(
                upload_file_process.stdout.decode('utf-8'))['fireOid']
            cmd = f"curl {self.fire_api}/{fire_id}/firePath " \
                  f"-u {self.username}:{self.password} " \
                  f"-H 'x-fire-path: {self.firepath}/{self.filename}' -X PUT"
            fire_path_process = subprocess.run(cmd, shell=True,
                                               capture_output=True)
            _ = json.loads(
                fire_path_process.stdout.decode('utf-8')
            )['filesystemEntry']['path']
            cmd = f"curl {self.fire_api}/{fire_id}/publish " \
                  f"-u {self.username}:{self.password} -X PUT"
            publish_process = subprocess.run(cmd, shell=True,
                                             capture_output=True)
            published = json.loads(
                publish_process.stdout.decode('utf-8')
            )['filesystemEntry']['published']
            if published:
                return self.get_public_link()
            else:
                raise KeyError
        except KeyError:
            return 'Error'

    def get_public_link(self):
        """This function will return public link to uploaded file"""
        return f"https://data.faang.org/api/fire_api/trackhubregistry/" \
            f"{self.firepath.split('/')[-2]}/{self.firepath.split('/')[-1]}/{self.filename}"

    def get_md5_of_file(self):
        """
        This function will return md5 hash of a file
        :return: md5 hash value
        """
        return hashlib.md5(self.file_as_bytes(
            open(self.filepath, 'rb'))).hexdigest()

    @staticmethod
    def file_as_bytes(file):
        """This function returns file as bits"""
        with file:
            return file.read()

    def get_file_size(self):
        """
        This function return file size in bytes
        :return: file size in bytes
        """
        return os.path.getsize(self.filepath)
