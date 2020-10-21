from buildbot.plugins import util

import passwords


class UserAuth(util.CustomAuth):
    def check_credentials(self, user, password):
        if user == b'admin' and str(password) == str(passwords.web_password):
            return True
        else:
            return False
