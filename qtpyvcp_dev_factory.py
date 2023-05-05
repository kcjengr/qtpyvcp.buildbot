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
                                         mode='full',
                                         submodules=False,
                                         workdir="sources/"))

# get git tag
factory_qtpyvcp_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit ID
factory_qtpyvcp_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit ID",
    command=["git", "rev-parse", "--short","HEAD"],
    property="commit_id",
    workdir="sources/"))

# compile resources
# disabled, done in deb build step
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(
#     name="compile resources",
#     command=["qcompile", "."],
#     workdir="sources/"))

# create changelog
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "qtpyvcp", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:commit_id)s.dev"), "Development version."],
    workdir="sources/"))

# build debs
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy files to the http repo
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="copy files to the http repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb"),
             "/home/buildbot/repo/qtpyvcp-dev/"],
    workdir="sources/"))

# copy files to the apt repo
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="copy files to repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb"),
             "/home/buildbot/debian/apt/pool/main/"],
    workdir="sources/"))

# delete files from build directory
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="delete files from build directory",
    command=["rm", util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb")],
    workdir="sources/"))

# scan new packages in apt repository
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="scan new packages in apt repository",
    command=["dpkg-scanpackages", "--arch", "amd64", "pool", ">", "dists/develop/main/binary-amd64/Packages"],
    workdir="/home/buildbot/debian/apt/"))

# gzip package list
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="gzip package list",
    command=["cat", "dists/develop/main/binary-amd64/Packages", "|", "gzip", "-9", ">", "dists/develop/main/binary-amd64/Packages.gz"],
    workdir="/home/buildbot/debian/apt/"))






# delete docs directory
# factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))
#
# factory_qtpyvcp_dev.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
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
