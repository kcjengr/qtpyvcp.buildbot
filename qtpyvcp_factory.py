# -*- python3 -*-
# ex: set syntax=pytho3:
#
# QtPyVCP Factory
#
from buildbot.plugins import steps, util

factory_qtpyvcp = util.BuildFactory()

# fetch sources
factory_qtpyvcp.addStep(steps.GitHub(name="download qtpyvcp sources",
                                     repourl='git@github.com:kcjengr/qtpyvcp.git',
                                     branch='main',
                                     mode='full',
                                     submodules=False,
                                     workdir="sources/"))

factory_qtpyvcp.addStep(steps.ShellCommand(
    name="compile resources",
    command=["qcompile", "."],
    workdir="sources/"))

# build debs
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

factory_qtpyvcp.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

factory_qtpyvcp.addStep(steps.ShellCommand(
    name="move files to repo",
    command=["mv",
             util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-all.deb"),
             "/home/buildbot/repo/qtpyvcp-dev/"],
    workdir="sources/"))

# publish on github
# factory_qtpyvcp.addStep(steps.ShellCommand(
#     command=["/home/buildbot/buildbot/worker/qtpyvcp/sources/.scripts/publish_github_release.sh",
#              "kcjengr/qtpyvcp", util.Property("branch")],
#     workdir="sources/"))


# factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))
#
# factory_qtpyvcp.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/.local/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/qtpyvcp/docs",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/qtpyvcp/sources/docs/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="sources/docs/source/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="Initialize docs repository",
#                                            command=["git", "init"],
#                                            workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="add remote repository",
#                                            command=["git", "remote", "add", "origin",
#                                                     "git@github.com:kcjengr/qtpyvcp.git"],
#                                            workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="switch branch",
#                                            command=["git", "checkout", "-b", "gh-pages"],
#                                            workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="add docs",
#                                            command=["git", "add", "."],
#                                            workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="commit docs",
#                                            command=["git", "commit", "-m", "Deploy docs"],
#                                            workdir="docs/"))
#
# factory_qtpyvcp.addStep(steps.ShellCommand(name="push docs",
#                                            command=["git", "push", "--force", "origin", "gh-pages"],
#                                            workdir="docs/"))
