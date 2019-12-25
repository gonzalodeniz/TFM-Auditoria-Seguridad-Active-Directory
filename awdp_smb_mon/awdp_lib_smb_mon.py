import smb
from smb.SMBConnection import SMBConnection
import sys

class ListFiles(object):
    def __init__(self, ip_remote, shared_resource, path, files_lst):
        self.ip_remote = ip_remote
        self.shared_resource = shared_resource
        self.path = path
        self.files_lst = files_lst

    def make_json(self):
        return {'smb_mon': {self.ip_remote + ';' + self.shared_resource + ';' + self.path: self.files_lst}}



class SmbMon(object):
    def __init__(self, ip_remote, hostname, user, pwd):

        self.ip_remote = ip_remote
        self.hostname = hostname
        self.user = user
        self.pwd = pwd
        self.shared_resources = []

        # Connection
        self.__s = SMBConnection(self.user,
                          self.pwd,
                          '',
                          self.hostname,
                          use_ntlm_v2=True,
                          )
        if not self.__s.connect(self.ip_remote, 139):
            print('Error: It was not possible to connect.')
            sys.exit(1)

        # Get shared resources
        self.shared_resources = [sr.name for sr in self.__s.listShares()]




    def get_files_lst(self, shared_resource, path):
        try:
            filenames_lst = []
            lst_file = self.__s.listPath(shared_resource, path)
            for file in lst_file:
                if file.filename not in ['.', '..']:
                    filenames_lst.append(file.filename)

            return filenames_lst
        except smb.smb_structs.OperationFailure:
            print('Error: shared resource or path no found')
            sys.exit(1)

    def get_files_dict(self, shared_resource, path):
        filenames_dict = {self.ip_remote : {shared_resource : self.get_files_lst(shared_resource, path)}}
        return filenames_dict

    def make_json(self, shared_resource, path):
        files_lst = self.list_files(shared_resource, path)
        return  {'smb_mon':{'ip' + ';' + shared_resource + ';' + path:files_lst}}

