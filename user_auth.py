from buildbot.plugins import util
import pass_file


class UserAuth(util.CustomAuth):
    def check_credentials(self, user, password):
        
        if user == "admin".encode("utf-8") and password == pass_file.web_password.encode("utf-8"):
            return True
        else:
            return False
