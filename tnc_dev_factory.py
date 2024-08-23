# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Develop Factory

import os

from buildbot.plugins import steps, util

factory_tnc_dev = util.BuildFactory()

# download sources
factory_tnc_dev.addStep(steps.GitHub(name="download sources",
                                         repourl='git@github.com:kcjengr/turbonc.git',
                                         branch='main',
                                         mode='full',
                                         submodules=False,
                                         workdir="sources/"))

# get git tag
factory_tnc_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_tnc_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# store version file
factory_tnc_dev.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > tnc_dev_version.txt')],
    workdir="/home/buildbot/versions/"))

# compile resources
# disabled, done in deb build step
# factory_tnc_dev.addStep(steps.ShellCommand(
#     name="compile resources",
#     command=["qcompile", "."],
#     workdir="sources/"))

factory_tnc_dev.addStep(steps.ShellCommand(
        name="build wheel with poetry",
        command=["python3", "-m", "poetry", "build"],
        workdir="sources/"
    )
)

# create changelog
factory_tnc_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "turbonc", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Development version."],
    workdir="sources/"))

# build debs
factory_tnc_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["debuild", "-b", "-uc", "-us"],
    workdir="sources/"))

# copy files to the http repo
factory_tnc_dev.addStep(steps.ShellCommand(
    name="copy files to the http repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/turbonc-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"),
             "/home/buildbot/repo/turbonc-dev/"],
    workdir="sources/"))


# delete old files from apt directory
# factory_tnc_dev.addStep(steps.ShellCommand(
#     name="delete files from apt directory",
#     command=["sh",
#              "/home/buildbot/buildbot/master/scripts/clean_apt_develop.sh",
#              util.Interpolate("python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")
#             ],
#     workdir="sources/"))

# move new files to the apt repo
factory_tnc_dev.addStep(steps.ShellCommand(
    name="move new files to the apt rep",
    command=["mv",
             util.Interpolate("/home/buildbot/buildbot/worker/turbonc-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"),
             "/home/buildbot/debian/apt/pool/main/"],
    workdir="sources/"))

# delete files from build directory
# factory_tnc_dev.addStep(steps.ShellCommand(
#     name="delete files from build directory",
#     command=["rm", util.Interpolate("/home/buildbot/buildbot/worker/turbonc-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")],
#     workdir="sources/"))

# scan new packages in apt repository
factory_tnc_dev.addStep(steps.ShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_develop.sh"],
    workdir="sources/"))



# # delete docs directory
# factory_tnc_dev.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))
#
# factory_tnc_dev.addStep(
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
# factory_tnc_dev.addStep(steps.ShellCommand(name="Initialize docs repository",
#                                                command=["git", "init"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="add remote repository",
#                                                command=["git", "remote", "add", "origin", "git@github.com:kcjengr/qtpyvcp.git"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="switch branch",
#                                                command=["git", "checkout", "-b", "gh-pages"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="add docs",
#                                                command=["git", "add", "."],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="commit docs",
#                                                command=["git", "commit", "-m", "Deploy docs"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="push docs",
#                                                command=["git", "push", "--force", "origin", "gh-pages"],
#                                                workdir="docs/"))
