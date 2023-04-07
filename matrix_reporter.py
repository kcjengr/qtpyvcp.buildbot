import logging
import requests

from buildbot.reporters.base import ReporterBase
from buildbot.util import httpclientservice
from pass_file import matrix_access_token

MATRIX_API_PATH = "_matrix/client/r0"
MATRIX_CONTENT_TYPE = "application/json"
MATRIX_EVENT_TYPE = "m.room.message"

class MatrixReporter(ReporterBase):
    name = "MatrixReporter"

    def __init__(self, homeserver, room_id, server_name=None, httpClient=None, **kwargs):
        ReporterBase.__init__(self, **kwargs)
        self.homeserver = homeserver
        self.room_id = room_id
        self.server_name = server_name
        self.httpClient = httpClient

    @staticmethod
    def get_client_url(homeserver, server_name=None):
        client_url = f"https://{homeserver}/{MATRIX_API_PATH}"
        if server_name:
            client_url += f"?server_name={server_name}"
        return client_url

    @httpclientservice.useHttpClients
    def sendMessage(self, message):
        client_url = self.get_client_url(self.homeserver, self.server_name)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": MATRIX_CONTENT_TYPE,
        }
        body = {
            "msgtype": MATRIX_EVENT_TYPE,
            "body": message,
        }
        url = f"{client_url}/rooms/{self.room_id}/send/{MATRIX_EVENT_TYPE}"
        d = self.httpClient.post(url, headers=headers, json=body)
        d.addCallback(requests.Response.raise_for_status)
        return d

    def send(self, builder_name, build_status, build):
        if build_status == "started":
            message = f"{builder_name} build started: {build['url']}"
        elif build_status == "success":
            message = f"{builder_name} build succeeded: {build['url']}"
        else:
            message = f"{builder_name} build failed: {build['url']}"
        try:
            self.sendMessage(message)
        except requests.exceptions.RequestException as e:
            logging.warning(f"MatrixReporter: Failed to send message: {e}")

    def setOptions(self, **kwargs):
        self.homeserver = os.environ.get("MATRIX_HOMESERVER", self.homeserver)
        self.room_id = os.environ.get("MATRIX_ROOM_ID", self.room_id)
        self.server_name = os.environ.get("MATRIX_SERVER_NAME", self.server_name)
        ReporterBase.setOptions(self, **kwargs)