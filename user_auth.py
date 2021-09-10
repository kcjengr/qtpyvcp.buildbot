# -*- python3 -*-
# ex: set syntax=python3:

from buildbot.plugins import util
import pass_file


class UserAuth(util.CustomAuth):
    def check_credentials(self, user, password):

        if user == bytes("admin", encoding='utf-8') and password == bytes(pass_file.web_password, encoding='utf-8'):
            return True
        else:
            return False
