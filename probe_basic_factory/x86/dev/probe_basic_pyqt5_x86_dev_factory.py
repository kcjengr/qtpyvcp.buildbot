# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_pyqt5_x86_dev = util.BuildFactory()


# download sources
factory_probe_basic_pyqt5_x86_dev.addStep(steps.GitHub(name="download sources",
                                             repourl='https://github.com/kcjengr/probe_basic.git',
                                             branch='main',
                                             mode='full',
                                             submodules=False,
                                             workdir="sources/"))

# git fetch
factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
    name="git fetch",
    command=["/bin/sh", "-c", "git fetch --all"],
    workdir="sources/"))

# get git tag
factory_probe_basic_pyqt5_x86_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))


# get git commit count since last tag
factory_probe_basic_pyqt5_x86_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# # store version file
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
#     name="store version file",
#     command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > pb_dev_version.txt')],
#     workdir="/home/buildbot/versions/"))

# compile resources
# disabled, done in deb build step
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
#     name="compile resources",
#     command=["qcompile", "."],
#     workdir="sources/"))

# create changelog
factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "lcvette1@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "probe-basic", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Unstable Release version."],
    workdir="sources/"))

# build debs
factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy files to the http repo
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
#     name="copy files to the http repo",
#     command=["cp",
#              util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"),
#              "/home/buildbot/repo/probe-basic-dev/"],
#     workdir="sources/"))
#
#
# # delete old files from apt directory
# # factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
# #     name="delete files from apt directory",
# #     command=["sh",
# #              "/home/buildbot/buildbot/master/scripts/clean_apt_develop.sh",
# #              util.Interpolate("python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")
# #             ],
# #     workdir="sources/"))
#
# # copy new files to the apt repo
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
#     name="copy files to repo",
#     command=["cp",
#              util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"),
#              "/home/buildbot/debian/apt/pool/main/develop/"],
#     workdir="sources/"))
#
# # delete files from build directory
# # factory_probe_basic_dev.addStep(steps.ShellCommand(
# #     name="delete files from build directory",
# #     command=["rm", util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")],
# #     workdir="sources/"))
#
# # scan new packages in apt repository
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(
#     name="scan new packages in apt repository",
#     command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_develop.sh"],
#     workdir="sources/"))
#
# # delete docs directory
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs_src/"))
#
# factory_probe_basic_pyqt5_x86_dev.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic-dev/docs_src",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic-dev/sources/docs_src/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="sources/docs_src/source/"
#     )
# )
#
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(name="Initialize docs repository",
#                                                command=["git", "init"],
#                                                workdir="docs_src/"))
#
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(name="add remote repository",
#                                                command=["git", "remote", "add", "origin", "git@github.com:kcjengr/probe_basic.git"],
#                                                workdir="docs_src/"))
#
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(name="switch branch",
#                                                command=["git", "checkout", "-b", "gh-pages"],
#                                                workdir="docs_src/"))
#
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(name="add docs",
#                                                command=["git", "add", "."],
#                                                workdir="docs_src/"))
#
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(name="commit docs",
#                                                command=["git", "commit", "-m", "Deploy docs"],
#                                                workdir="docs_src/"))
#
# factory_probe_basic_pyqt5_x86_dev.addStep(steps.ShellCommand(name="push docs",
#                                                command=["git", "push", "--force", "origin", "gh-pages"],
#                                                workdir="docs_src/"))
