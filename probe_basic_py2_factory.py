# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_py2 = util.BuildFactory()

# fetch sources
factory_probe_basic_py2.addStep(steps.GitHub(name="download probe_basic sources",
                                             repourl='git@github.com:kcjengr/probe_basic.git',
                                             branch='master',
                                             mode='full',
                                             submodules=True,
                                             workdir="sources/"))

# install qtpyvcp
factory_probe_basic_py2.addStep(steps.ShellCommand(
    name="install qtpyvcp from pip",
    command=["python2.7", "-m", "pip", "install", "--upgrade", "git+https://github.com/kcjengr/qtpyvcp@python2_maintenance"],
    workdir="sources/"))

# git pull just in case
factory_probe_basic_py2.addStep(steps.ShellCommand(
    name="git pull probe basic",
    command=["git", "pull"],
    workdir="sources/"))

# git pull submodules
factory_probe_basic_py2.addStep(steps.ShellCommand(
    name="git pull probe basic",
    command=["git", "git" "submodule" "update" "--init" "--recursive"],
    workdir="sources/"))

# install sources
factory_probe_basic_py2.addStep(steps.ShellCommand(
    name="install probe basic from sources",
    command=["python2.7", "-m", "pip", "install", "--upgrade", "."],
    workdir="sources/"))

# build binaries and wheel for distribution
factory_probe_basic_py2.addStep(steps.ShellCommand(
    name="build binaries and wheel for distribution",
    command=["python2.7", "setup.py", "bdist_wheel"],
    workdir="sources/"))

# build source for distribution
factory_probe_basic_py2.addStep(steps.ShellCommand(
    name="build source for distribution",
    command=["python2.7", "setup.py", "sdist"],
    workdir="sources/"))

# get version from installed probe_basic package
factory_probe_basic_py2.addStep(
    steps.SetPropertyFromCommand(
        name="obtain probe_basic version number",
        command=["python2.7",
                 "pb-installer/scripts/check_probe_basic_version.py"],
        property="probe_basic_dev_version",
        workdir="sources/"))

# add version and date to installer package file
factory_probe_basic_py2.addStep(
    steps.ShellCommand(name="add version and date to installer package file",
                       command=["python2.7",
                                "pb-installer/scripts/create_probe_basic_package_config.py",
                                "pb-installer/templates/probe_basic_package_template.xml",
                                "pb-installer/packages/com.probebasic.core/meta/package.xml",
                                util.Property("probe_basic_dev_version")],
                       workdir="sources/"))

# add version and date to installer config file
factory_probe_basic_py2.addStep(
    steps.ShellCommand(name="add version, date and repo to installer config file",
                       command=["python2.7",
                                "pb-installer/scripts/create_config.py",
                                "pb-installer/templates/config_template.xml",
                                "pb-installer/config/config.xml",
                                "http://repository.qtpyvcp.com/repo/pb-py2/repo",
                                util.Property("probe_basic_dev_version")],
                       workdir="sources/"))

# copy files to installer directories
factory_probe_basic_py2.addStep(steps.CopyDirectory(name="copy probebasic builds to the installer core package",
                                                    src="sources/dist",
                                                    dest="sources/pb-installer/packages/com.probebasic.core/data/"))

# sim files to installer directories
factory_probe_basic_py2.addStep(steps.CopyDirectory(name="copy probebasic configs to the installer sim package",
                                                    src="sources/config",
                                                    dest="sources/pb-installer/packages/com.probebasic.sim/data/"))

# configure the installer
factory_probe_basic_py2.addStep(steps.ShellCommand(name="configure the installer",
                                                   command=["qmake"],
                                                   workdir="sources/pb-installer",
                                                   env={"QT_SELECT": "qt5",
                                                        "PB_VERSION": util.Property("probe_basic_dev_version")}))

# build the installer
factory_probe_basic_py2.addStep(steps.Compile(name="compile the installer",
                                              command=["make"],
                                              workdir="sources/pb-installer",
                                              env={"QT_SELECT": "qt5"}))

# copy the packages to repository
factory_probe_basic_py2.addStep(steps.CopyDirectory(name="copy the packages to repository",
                                                    src="sources/pb-installer/repo",
                                                    dest="/home/turboss/repo/pb-py2"))


# copy the installer to repository
factory_probe_basic_py2.addStep(steps.CopyDirectory(name="copy the installer to repository",
                                                    src="sources/pb-installer/bin",
                                                    dest="/home/turboss/repo/pb-py2"))


factory_probe_basic_py2.addStep(steps.RemoveDirectory(name="delete copy of the local repo", dir="sources/pb-installer/repo"))
factory_probe_basic_py2.addStep(steps.RemoveDirectory(name="delete build directory", dir="sources/build/"))
factory_probe_basic_py2.addStep(steps.RemoveDirectory(name="delete dist directory", dir="sources/dist/"))
#
#
# factory_probe_basic_py2.addStep(steps.GitHub(name="downlaod static docs",
#                                              repourl='git@github.com:kcjengr/probe_basic.git',
#                                              origin="origin",
#                                              branch="gh-pages",
#                                              mode='full',
#                                              workdir="docs/"))
#
# factory_probe_basic_py2.addStep(steps.ShellCommand(name="reset gh-pages",
#                                                    command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
#                                                    workdir="docs/"))
#
# factory_probe_basic_py2.addStep(steps.ShellCommand(name="delete git index",
#                                                    command=["rm", ".git/index"],
#                                                    workdir="docs/"))
#
# factory_probe_basic_py2.addStep(steps.ShellCommand(name="clean gh-pages",
#                                                    command=["git", "clean", "-fdx"],
#                                                    workdir="docs/"))
#
# factory_probe_basic_py2.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/usr/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic-dev/docs/",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic-dev/sources/docs_src/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="docs/"))
#
# factory_probe_basic_py2.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_probe_basic_py2.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_probe_basic_py2.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
