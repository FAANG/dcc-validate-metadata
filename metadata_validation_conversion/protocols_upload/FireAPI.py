import json
import subprocess
import sys
import hashlib
import os
from decouple import config
from argparse import ArgumentParser


class FireAPI:
    def __init__(self, username, password, archive_name, api_endpoint,
                 filename=None, path=None):
        self.username = username
        self.password = password
        self.archive_name = archive_name
        self.api_endpoint = api_endpoint
        if filename:
            self.filepath = filename
            self.filename = filename.split('/')[-1]
        if path:
            self.path = path

    def upload_object(self):
        """This function will upload object to Fire database"""
        cmd = f"curl {self.api_endpoint}/objects " \
            f"-F file=@{self.filepath} " \
            f"-H 'x-fire-path: {self.path}/{self.filename}' " \
            f"-H 'x-fire-publish: true' " \
            f"-u {self.username}:{self.password} " \
              f"-H 'x-fire-size: {self.get_file_size()}' " \
              f"-H 'x-fire-md5: {self.get_md5_of_file()}'"
        proc = subprocess.run(cmd, shell=True, capture_output=True)

    def get_public_link(self):
        """This function will return public link to uploaded file"""
        link = f"https://data.faang.org/api/fire_api/" \
               f"{self.path.split('/')[-1]}/{self.filename}"
        print(link)

    def list_objects(self):
        """This function will list all objects in archive"""
        cmd = f"curl {self.api_endpoint}/objects?total=1000000 " \
            f"-u {self.username}:{self.password}"
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        out = json.loads(out.decode('utf-8'))
        print(f"{'File path':150}\t{'Published':10}\t{'FireOId':30}")
        for file in out:
            if file['filesystemEntry']:
                print(f"{file['filesystemEntry']['path']:150}\t"
                      f"{file['filesystemEntry']['published']}\t"
                      f"{file['fireOid']:30}")

    def delete_objects(self, fire_id):
        """This function will delete object from Fire database"""
        cmd = f"curl {self.api_endpoint}/objects/{fire_id} " \
            f"-u {self.username}:{self.password} " \
            f"-X DELETE"
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        self.list_objects()

    def replace_object(self, fire_id):
        """This function will replace existing object in Fire API"""
        self.delete_objects(fire_id)
        self.upload_object()

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