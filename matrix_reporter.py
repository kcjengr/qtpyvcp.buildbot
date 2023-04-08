# -*- python3 -*-
# ex: set syntax=python3:


import json
import requests
from buildbot.reporters.base import ReporterBase

from pass_file import matrix_access_token


class MatrixReporter(ReporterBase):
    """
    A Buildbot reporter that sends build results to a Matrix room via HTTP.
    """

    def __init__(self, homeserver, room_id, **kwargs):
        """
        Create a new MatrixReporter instance.

        :param homeserver: The URL of the Matrix homeserver to use.
        :param room_id: The ID of the room to send messages to.
        :param access_token: The access token to use for authentication.
        :param kwargs: Additional arguments to pass to the superclass constructor.
        """
        super().__init__(**kwargs)
        self.homeserver = homeserver
        self.room_id = room_id
        self.access_token = pass_file.matrix_access_token

    def getURL(self, build):
        """
        Get the URL of the build.

        :param build: The build object.
        :return: The URL of the build.
        """
        return build.getURL()

    def getFormattedMessage(self, build):
        """
        Get the formatted message to send to the Matrix room.

        :param build: The build object.
        :return: The formatted message.
        """
        # construct the message body
        body = "**{}**: {} - {}".format(
            build.getBuilder().getName(),
            build.getDisplayName(),
            self.getURL(build)
        )

        # construct the message content
        content = {
            "msgtype": "m.text",
            "body": body
        }

        return content

    def send(self, content):
        """
        Send a message to the Matrix room.

        :param content: The content of the message.
        """
        # construct the URL to send the message to
        url = "{}/_matrix/client/r0/rooms/{}/send/m.room.message".format(
            self.homeserver,
            self.room_id
        )

        # construct the headers for the HTTP request
        headers = {
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }

        # send the HTTP request
        response = requests.post(url, headers=headers, data=json.dumps(content))

        # check the response code
        if response.status_code != 200:
            self.logger.error("Failed to send Matrix message: %s", response.text)

    def buildStarted(self, build):
        """
        Handle a build started event.

        :param build: The build object.
        """
        content = self.getFormattedMessage(build)
        content["body"] += " started"
        self.send(content)

    def buildFinished(self, builderName, build, result):
        """
        Handle a build finished event.

        :param builderName: The name of the builder.
        :param build: The build object.
        :param result: The result of the build.
        """
        content = self.getFormattedMessage(build)
        content["body"] += " {}".format(result)
        self.send(content)
