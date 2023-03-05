# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Develop Factory

import os

from buildbot.plugins import steps, util

factory_qtpyvcp_dev = util.BuildFactory()

# download sources
factory_qtpyvcp_dev.addStep(steps.GitHub(name="download sources",
                                         repourl='git@github.com:kcjengr/qtpyvcp.git',
                                         branch='main',
                                         submodules=False,
                                         workdir="sources/"))

# get git tag
factory_qtpyvcp_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# compile resources
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="compile resources",
    command=["qcompile", "."],
    workdir="sources/"))

# create changelog
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--distribution", "experimental", "--force-distribution", util.Interpolate("%(prop:tag)s"), util.Interpolate("Bump version to %(prop:tag)s")],
    workdir="sources/"))

# build debs
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["debuild", "-us", "-uc" "-S", ">", "/dev/null", "2>&1"],
    workdir="sources/"))

# move files to repo
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="move files to repo",
    command=["mv",
             util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-all.deb"),
             "/home/buildbot/repo/qtpyvcp-dev/"],
    workdir="sources/"))

# factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))
#
# factory_qtpyvcp_dev.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/usr/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/qtpyvcp-dev/docs",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/qtpyvcp-dev/sources/docs/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="sources/docs/source/"
#     )
# )
#
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="Initialize docs repository",
#                                                command=["git", "init"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="add remote repository",
#                                                command=["git", "remote", "add", "origin", "git@github.com:kcjengr/qtpyvcp.git"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="switch branch",
#                                                command=["git", "checkout", "-b", "gh-pages"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="add docs",
#                                                command=["git", "add", "."],
#                                                workdir="docs/"))
#
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="commit docs",
#                                                command=["git", "commit", "-m", "Deploy docs"],
#                                                workdir="docs/"))
#
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="push docs",
#                                                command=["git", "push", "--force", "origin", "gh-pages"],
#                                                workdir="docs/"))
