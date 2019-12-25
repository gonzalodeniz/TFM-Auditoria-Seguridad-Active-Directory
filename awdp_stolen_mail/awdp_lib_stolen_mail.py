# coding=utf-8

"""
    FILE            awdp_lib_stolen_mail.py
    Version:        1.0
    Date Version:   21/03/2017
    Author:         Gonzalo Déniz Acosta

    Class StolenMail           - Used to connect to the API and show information about stolen mail.
    Exceptions FormatMailError - Throwed if mail syntax incorrect.
"""
import urllib2
import re
import json

class FormatMailError(Exception):
    def __str__(self):
        return 'Mail no validate'


class StolenMail(object):

    API_URL_HSH = 'https://hesidohackeado.com/api?q='


    def __init__(self, mail=None):
        self.str_resp = None
        self.dict_resp = None

        if mail is not None:
            self.load(mail)

    def __str__(self):
        return self.str_resp

    def __request_web(self, mail):
        '''Consults on the internet if the mail has been stolen. Return json response.
        '''
        user_agent = 'Mozilla/5.0'
        hdr = {'User-Agent':user_agent,}
        req = urllib2.Request(self.API_URL_HSH + mail, headers=hdr)
        ur = urllib2.urlopen(req)
        response = ur.read()
        ur.close()
        return response


    def __validate_mail(self, mail):
        '''Verify that the mail is well written. Return True or False
        '''
        if len(mail) > 7 and len(mail) <= 255:
            if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', mail) != None:
                return True
        return False

    def load(self, mail):
        ''' Reinitialize the object with a new mail. If the mail is invalid it throws an exception
        '''
        self.str_resp = None
        self.dict_resp = None
        if self.__validate_mail(mail):
            self.str_resp = self.__request_web(mail)
            self.dict_resp = json.loads(self.str_resp)
        else:
            raise FormatMailError()

    def info_str(self):
        ''' Return json response. Format string
        '''
        return self.str_resp

    def info_dic(self):
        ''' Return json response. Format dictionary'''
        return self.dict_resp

    def has_been_stolen(self):
        ''' Return True if the mail has been stolen. False otherwise.
        '''
        return (self.dict_resp['status'] == 'found')