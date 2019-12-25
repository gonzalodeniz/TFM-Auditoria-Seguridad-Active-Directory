from datetime import datetime
import sys
try:
    import ldap
except ImportError:
    print('Module ldap no found. To install run "sudo apt-get install python-ldap"')
    sys.exit(1)


class AdError(Exception):
    pass

class AdObjects(object):
    NEVER_EXPIRES = 9223372036854775807
    ENABLED_ACCOUNT = 0x0200
    DISABLED_ACCOUNT = 0x0202
    PASSWORD_NOT_REQUIRED = 0x0020
    PASSWORD_NOT_EXPIRE = 0x010000

    def __init__(self, log=None):
        self.log = log


    def timestamp_to_str(self, timestamp):
        MagicNumber = 11644473600
        return datetime.fromtimestamp((timestamp / 10000000) - MagicNumber).strftime('%Y-%m-%d')

class AdComputer(AdObjects):
    def __init__(self, comp_raw, log=None):
        try:
            super(AdComputer, self).__init__(log)
            self.dn = comp_raw[0]
            try:
                self.service_pack = comp_raw[1]['operatingSystemServicePack'][0]
            except KeyError as e:
                self.service_pack = ''

            self.name = comp_raw[1]['name'][0]
            self.lastLogon = int(comp_raw[1]['lastLogon'][0])
            self.userAccountControl = int(comp_raw[1]['userAccountControl'][0])
            self.badPasswordTime = int(comp_raw[1]['badPasswordTime'][0])
            self.badPwdCount = int(comp_raw[1]['badPwdCount'][0])
            self.memberOf = comp_raw[1].get('memberOf', None)

        except TypeError:
            raise AdError('computer_raw incorrect structure')
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def date_last_logon(self):
        timestamp = self.lastLogon
        if timestamp > 0:
            return self.timestamp_to_str(timestamp)
        else:
            return 'Never Login'

    def date_last_bad_logon(self):
        if self.badPasswordTime > 0:
            return self.timestamp_to_str(self.badPasswordTime)
        else:
            return '0'

    def count_bad_logon(self):
        return str(self.badPwdCount)

    def is_enabled(self):
        return not ((self.userAccountControl & self.DISABLED_ACCOUNT)==self.DISABLED_ACCOUNT)

    def is_password_required(self):
        return not ((self.userAccountControl & self.PASSWORD_NOT_REQUIRED) == self.PASSWORD_NOT_REQUIRED)

    def is_password_expire(self):
        return not ((self.userAccountControl & self.PASSWORD_NOT_EXPIRE) == self.PASSWORD_NOT_EXPIRE)



class AdUser(AdObjects):


    def __init__(self, user_raw, log=None):
        try:
            super(AdUser, self).__init__(log)
            self.dn = user_raw[0]
            self.accountExpires = int(user_raw[1]['accountExpires'][0])
            self.name = user_raw[1]['sAMAccountName'][0]
            self.lastLogon = int(user_raw[1]['lastLogon'][0])
            self.userAccountControl = int(user_raw[1]['userAccountControl'][0])
            self.badPasswordTime = int(user_raw[1]['badPasswordTime'][0])
            self.badPwdCount = int(user_raw[1]['badPwdCount'][0])
            self.memberOf = user_raw[1].get('memberOf', None)

            # Debug mode
            if self.log is not None:
                self.log.debug('AdUser(' + self.dn + ') Successfully built' )


        except TypeError as e:
            if self.log is not None:
                self.log.exception('Error incorrect structure in ' + str(user_raw) +': ' + e.message )
            raise AdError('user_raw incorrect structure')
        except:
            if self.log is not None:
                self.log.exception('Unexpected error in ' + str(user_raw))
            print "Unexpected error:", sys.exc_info()[0]
            raise


    def date_expires(self):
        timestamp = self.accountExpires
        if timestamp == self.NEVER_EXPIRES or timestamp == 0:
            return 'Never Expires'
        else:
            return self.timestamp_to_str(timestamp)

    def date_last_logon(self):
        timestamp = self.lastLogon
        if timestamp > 0:
            return self.timestamp_to_str(timestamp)
        else:
            return 'Never Login'

    def date_last_bad_logon(self):
        if self.badPasswordTime > 0:
            return self.timestamp_to_str(self.badPasswordTime)
        else:
            return '0'

    def count_bad_logon(self):
        return str(self.badPwdCount)

    def is_enabled(self):
        return not ((self.userAccountControl & self.DISABLED_ACCOUNT)==self.DISABLED_ACCOUNT)

    def is_password_required(self):
        return not ((self.userAccountControl & self.PASSWORD_NOT_REQUIRED) == self.PASSWORD_NOT_REQUIRED)

    def is_password_expire(self):
        return not ((self.userAccountControl & self.PASSWORD_NOT_EXPIRE) == self.PASSWORD_NOT_EXPIRE)


class AdGroup(AdObjects):


    def __init__(self, group_raw, log=None):
        try:
            super(AdGroup, self).__init__(log)
            self.dn = group_raw[0]
            self.sAMAccountName = group_raw[1]['sAMAccountName'][0]
            self.adminCount = group_raw[1].get('adminCount',['0'])[0]
            self.isCriticalSystemObject = group_raw[1].get('isCriticalSystemObject',0)
            self.description = group_raw[1].get('description','')
            self.member = group_raw[1].get('member', [])
            self.memberOf = group_raw[1].get('memberOf', [])
        except TypeError:
            raise AdError('group_raw incorrect structure')
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise



class ADLib:
    def __init__(self, server, user, psw, log=None):
        try:
            # connection
            self.__con = ldap.initialize(server)
            self.__con.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            self.__con.simple_bind_s(user, psw)
            self.log = log

            # Debug mode
            if log is not None:
                log.debug('Connection ' + server + ' successful')

        except ldap.SERVER_DOWN:
            print('Error: LDAP Server no found.')
            if log is not None:
                log.exception('Error: LDAP Server no found.')

        except ldap.INVALID_CREDENTIALS:
            self.__con.unbind()
            print('Error: Your username or password is incorrect.')
            if log is not None:
                log.exception('Error: LDAP Server no found.')
        except:
            if log is not None:
                log.exception('Unexpected error')
            raise


    def load_users(self, basedn):
        ''' Search all user of basedn.
            Return a list of all users'''
        filter = "(&(objectClass=user)(name=*))"
        attributes = ['dn', 'sAMAccountName', 'accountExpires', 'lastLogon', 'UserAccountControl',
                      'badPasswordTime', 'badPwdCount', 'memberOf']
        lst_users_raw = self.__con.search_s(basedn, ldap.SCOPE_SUBTREE, filter, attributes)

        # Debug mode
        if self.log is not None:
            lst_all_attr = self.__con.search_s(basedn, ldap.SCOPE_SUBTREE, filter)
            self.log.debug('USERS RAW (all attributes): \n' + str(lst_all_attr) +'\n')
            self.log.debug('USERS RAW (summary attributes): \n' + str(lst_users_raw) + '\n')

        return lst_users_raw

    def to_adusers(self, usersraw):
        if self.log is not None:
            self.log.debug('Converting raw users to AdUsers objects:')
        lst_adusers = []
        for user in usersraw:
            try:
                # Debug mode
                if self.log is not None:
                    self.log.debug('Converting ' + str(user) + ' to AdUser')

                lst_adusers.append(AdUser(user, self.log))
            except AdError as e:
                if self.log is not None:
                    self.log.exception('Error ignored: ' + str(user) + ' -> ' + e.message)
                pass

        return lst_adusers

    def load_computer(self, basedn):
            ''' Search all user of basedn.
                Return a list of all users'''
            filter = "(&(objectClass=computer)(name=*))"
            attributes = ['dn', 'name', 'operatingSystemServicePack', 'whenCreated', 'badPasswordTime', 'badPwdCount','accountExpires', 'userAccountControl', 'lastLogon', 'operatingSystem', 'memberOf']
            lst_comp_raw = self.__con.search_s(basedn, ldap.SCOPE_SUBTREE, filter, attributes)
            return lst_comp_raw


    def to_adcomputers(self, computersraw):
        lst_adcomputers = []
        for comp in computersraw:
            try:
                lst_adcomputers.append(AdComputer(comp))
            except AdError as e:
                print(str(comp) + ' -> ' + e.message)
                pass

        return lst_adcomputers

    def load_groups(self, basedn):
        ''' Search all user of basedn.
            Return a list of all users'''
        filter = "(&(objectClass=group)(name=*))"
        attributes = ['dn', 'sAMAccountName', 'adminCount', 'isCriticalSystemObject', 'description', 'member', 'memberOf']
        lst_groups_raw = self.__con.search_s(basedn, ldap.SCOPE_SUBTREE, filter, attributes)
        return lst_groups_raw


    def to_adgroups(self, groupsraw):
        lst_adgroups = []
        for comp in groupsraw:
            try:
                lst_adgroups.append(AdGroup(comp))
            except AdError as e:
                pass

        return lst_adgroups


