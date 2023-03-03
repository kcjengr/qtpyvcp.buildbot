# -*- python3 -*-
# ex: set syntax=python3:
#
# QtPyVCP Develop Factory
#
import os

from buildbot.plugins import steps, util

factory_qtpyvcp_dev = util.BuildFactory()

# fetch sources
factory_qtpyvcp_dev.addStep(steps.GitHub(name="download qtpyvcp sources",
                                         repourl='git@github.com:kcjengr/qtpyvcp.git',
                                         branch='main',
                                         mode='full',
                                         submodules=True,
                                         workdir="sources/"))

factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="compile resources",
    command=["qcompile", "."],
    workdir="sources/"))

# build debs
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))


# util.Interpolate('string before ' + '%(prop:artifact.output)s' + ' string after')

factory_qtpyvcp_dev.addStep(steps.ShellCommand(
              env={'PYTHONPATH': "/home/buildbot/lib/python"},
              command=["cp", util.Property("qtpyvcp_dev_version"), "/home/buildbot/repo/qtpyvcp-dev/"],
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
