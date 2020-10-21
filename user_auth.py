from buildbot.plugins import util

from .pass_file import web_password


class UserAuth(util.CustomAuth):
    def check_credentials(self, user, password):
        if user == b'admin' and password == web_password:
            return True
        else:
            return False
