from buildbot.plugins import util
import pass_file


class UserAuth(util.CustomAuth):
    def check_credentials(self, user, password):
        if user == b'admin' and password.encode("utf-8") == pass_file.web_password.encode("utf-8"):
            return True
        else:
            return False
