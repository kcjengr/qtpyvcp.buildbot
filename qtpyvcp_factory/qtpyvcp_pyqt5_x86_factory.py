# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Stable Factory x86

import os

from buildbot.plugins import steps, util

factory_qtpyvcp_pyqt5_x86 = util.BuildFactory()

# download sources
factory_qtpyvcp_pyqt5_x86.addStep(steps.GitHub(name="download sources",
                                               repourl='git@github.com:kcjengr/qtpyvcp.git',
                                               branch='main',
                                               mode='full',
                                               submodules=False,
                                               workdir="sources/"))
# git fetch
factory_qtpyvcp_pyqt5_x86.addStep(steps.ShellCommand(
    name="git fetch",
    command=["/bin/sh", "-c", "git fetch --all"],
    workdir="sources/"))

# get git tag
factory_qtpyvcp_pyqt5_x86.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# not needed by release
# # get git commit count since last tag
# factory_qtpyvcp.addStep(steps.SetPropertyFromCommand(
#     name="get git commit count since last tag",
#     command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
#     property="minor_version",
#     workdir="sources/"))

# store version file
factory_qtpyvcp_pyqt5_x86.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s > qtpyvcp_stable_version.txt')],
    workdir="/home/bb/versions/"))

# create changelog
factory_qtpyvcp_pyqt5_x86.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "qtpyvcp", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable Release version."],
    workdir="sources/"))

# build debs
factory_qtpyvcp_pyqt5_x86.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))


# upload files to http server
factory_qtpyvcp_pyqt5_x86.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/qtpyvcp-pyqt5-x86/python3-qtpyvcp_%(prop:tag)s_amd64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/qtpyvcp-pyqt5-x86/python3-qtpyvcp_%(prop:tag)s_amd64.deb"),
    mode=0o644))

# upload files to apt server
factory_qtpyvcp_pyqt5_x86.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/qtpyvcp-pyqt5-x86/python3-qtpyvcp_%(prop:tag)s_amd64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/bookworm/python3-qtpyvcp_%(prop:tag)s_amd64.deb")))


# scan new packages in apt repository
factory_qtpyvcp_pyqt5_x86.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_bookworm.sh"],
    workdir="/home/buildbot/debian/apt"))

# doc related things
# # delete docs directory
# factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))
#
# factory_qtpyvcp.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/qtpyvcp/docs",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/qtpyvcp/sources/docs/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="sources/docs/source/"
#     )
# )
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="Initialize docs repository",
#                                                command=["git", "init"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="add remote repository",
#                                                command=["git", "remote", "add", "origin", "git@github.com:kcjengr/qtpyvcp.git"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="switch branch",
#                                                command=["git", "checkout", "-b", "gh-pages"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="add docs",
#                                                command=["git", "add", "."],
#                                                workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="commit docs",
#                                                command=["git", "commit", "-m", "Deploy docs"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="push docs",
#                                                command=["git", "push", "--force", "origin", "gh-pages"],
#                                                workdir="docs/"))
