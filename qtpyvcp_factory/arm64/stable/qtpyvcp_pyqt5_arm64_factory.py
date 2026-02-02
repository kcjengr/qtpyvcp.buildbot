# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Stable Factory arm64

import os

from buildbot.plugins import steps, util

factory_qtpyvcp_pyqt5_arm64 = util.BuildFactory()

# download sources
factory_qtpyvcp_pyqt5_arm64.addStep(steps.GitHub(name="download sources",
                                           repourl='git@github.com:kcjengr/qtpyvcp.git',
                                           branch='main',
                                           mode='full',
                                           submodules=False,
                                           workdir="sources/"))
# git fetch
factory_qtpyvcp_pyqt5_arm64.addStep(steps.ShellCommand(
    name="git fetch",
    command=["/bin/sh", "-c", "git fetch --all"],
    workdir="sources/"))

# get git tag
factory_qtpyvcp_pyqt5_arm64.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# store version file
factory_qtpyvcp_pyqt5_arm64.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s > qtpyvcp_stable_version.txt')],
    workdir="/home/bb/versions/"))

# create changelog
factory_qtpyvcp_pyqt5_arm64.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "qtpyvcp", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable Release version."],
    workdir="sources/"))

# build debs
factory_qtpyvcp_pyqt5_arm64.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))


# upload files to http server
factory_qtpyvcp_pyqt5_arm64.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/qtpyvcp-pyqt5-arm64/python3-qtpyvcp_%(prop:tag)s_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/qtpyvcp-pyqt5-arm64/python3-qtpyvcp_%(prop:tag)s_arm64.deb")))

# upload files to apt server
factory_qtpyvcp_pyqt5_arm64.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/qtpyvcp-pyqt5-arm64/python3-qtpyvcp_%(prop:tag)s_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/bookworm/python3-qtpyvcp_%(prop:tag)s_arm64.deb")))


# scan new packages in apt repository
factory_qtpyvcp_pyqt5_arm64.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_bookworm.sh"],
    workdir="/home/buildbot/debian/apt"))

