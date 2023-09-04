# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Release Factory

import os

from buildbot.plugins import steps, util

factory_qtpyvcp = util.BuildFactory()

# download sources
factory_qtpyvcp.addStep(steps.GitHub(name="download sources",
                                     repourl='git@github.com:kcjengr/qtpyvcp.git',
                                     branch='main',
                                     mode='full',
                                     submodules=False,
                                     workdir="sources/"))

# get git tag
factory_qtpyvcp.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_qtpyvcp.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# store version file
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > qtpyvcp_version.txt')],
    workdir="/home/buildbot/versions/"))

# create changelog
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "qtpyvcp", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s"), "Release version."],
    workdir="sources/"))

# build debs
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy files to the http repo
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="copy files to the http repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.all.deb"),
             "/home/buildbot/repo/qtpyvcp/"],
    workdir="sources/"))

# copy new files to the apt repo
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="copy files to repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-all.deb"),
             "/home/buildbot/repo/qtpyvcp-dev/"],
    workdir="sources/"))

# publish on github
# factory_qtpyvcp.addStep(steps.ShellCommand(
#     command=["/home/buildbot/buildbot/worker/qtpyvcp/sources/.scripts/publish_github_release.sh",
#              "kcjengr/qtpyvcp", util.Property("branch")],
#     workdir="sources/"))

# scan new packages in apt repository
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_develop.sh"],
    workdir="sources/"))

# delete docs directory
factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))

factory_qtpyvcp.addStep(
    steps.Sphinx(
        name="compile sphinx docs",
        haltOnFailure=True,
        sphinx="/home/buildbot/venv/bin/sphinx-build",
        sphinx_builddir="/home/buildbot/buildbot/worker/qtpyvcp/docs",
        sphinx_sourcedir="/home/buildbot/buildbot/worker/qtpyvcp/sources/docs/source/",
        strict_warnings=False,
        env={"LANG": "en_EN.UTF-8"},
        workdir="sources/docs/source/"
    )
)

factory_qtpyvcp.addStep(steps.ShellCommand(name="Initialize docs repository",
                                               command=["git", "init"],
                                               workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="add remote repository",
                                               command=["git", "remote", "add", "origin", "git@github.com:kcjengr/qtpyvcp.git"],
                                               workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="switch branch",
                                               command=["git", "checkout", "-b", "gh-pages"],
                                               workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="add docs",
                                               command=["git", "add", "."],
                                               workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="commit docs",
                                               command=["git", "commit", "-m", "Deploy docs"],
                                               workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="push docs",
                                               command=["git", "push", "--force", "origin", "gh-pages"],
                                               workdir="docs/"))
