import subprocess
import hashlib
import os
import json

from elasticsearch import Elasticsearch

from metadata_validation_conversion.constants import ORGANIZATIONS


class FireAPI:
    def __init__(self, username, password, filepath, firepath, filename):
        self.username = username
        self.password = password
        self.filepath = filepath
        self.filename = filename
        self.firepath = f"ftp/protocols/{firepath}"
        self.protocol_index = self.get_protocol_index(firepath)
        self.fire_api = 'https://hh.fire.sdo.ebi.ac.uk/fire/objects'
        self.es = Elasticsearch(['elasticsearch-master-headless:9200'])

    def upload_object(self):
        """This function will upload object to Fire database"""
        # Check that protocol doesn't exist in es, otherwise return Error
        write_to_es_result = self.write_to_es()
        if write_to_es_result == 'Error':
            return 'Error'
        # curl request to upload protocol to FIRE service
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
            self.delete_from_es()
            return 'Error'

    @staticmethod
    def get_protocol_index(firepath):
        if firepath == 'samples':
            return 'protocols_samples'
        elif firepath == 'experiments':
            return 'protocols_experiments'
        elif firepath == 'analyses':
            return 'protocol_analyses'

    def get_public_link(self):
        """This function will return public link to uploaded file"""
        return f"https://data.faang.org/api/fire_api/" \
               f"{self.firepath.split('/')[-1]}/{self.filename}"

    def write_to_es(self):
        """This function will write new protocol to protocols index in ES"""
        parsed = self.filename.split("_")
        university_name = ORGANIZATIONS[parsed[0]]
        protocol_name = " ".join(parsed[2:-1])
        url = self.get_public_link()
        date = parsed[-1].split(".pdf")[0]
        protocol_data = {
            "specimens": [],
            "universityName": university_name,
            "protocolDate": date,
            "protocolName": protocol_name,
            "key": self.filename,
            "url": url
        }
        if self.es.exists(self.protocol_index, id=self.filename):
            return 'Error'
        else:
            self.es.create(self.protocol_index, id=self.filename,
                           body=protocol_data)

    def delete_from_es(self):
        """This function will delete protocol from ES"""
        self.es.delete(self.protocol_index, id=self.filename)

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
