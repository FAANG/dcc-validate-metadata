import subprocess
import hashlib
import os


class FireAPI:
    def __init__(self, username, password, filepath, firepath):
        self.username = username
        self.password = password
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.firepath = f"ftp/protocols/{firepath}"

    def upload_object(self):
        """This function will upload object to Fire database"""
        cmd = f"curl https://hh.fire.sdo.ebi.ac.uk/fire/objects " \
            f"-F file=@{self.filepath} " \
            f"-H 'x-fire-path: {self.firepath}/{self.filename}' " \
            f"-H 'x-fire-publish: true' " \
            f"-u {self.username}:{self.password} " \
              f"-H 'x-fire-size: {self.get_file_size()}' " \
              f"-H 'x-fire-md5: {self.get_md5_of_file()}'"
        proc = subprocess.run(cmd, shell=True, capture_output=True)
        if proc.returncode != 0:
            return "Error"
        else:
            self.write_to_es()
            return self.get_public_link()

    def get_public_link(self):
        """This function will return public link to uploaded file"""
        return f"https://data.faang.org/api/fire_api/" \
               f"{self.firepath.split('/')[-1]}/{self.filename}"

    def write_to_es(self):
        """This function will write new protocol to protocols index in ES"""
        pass

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
