# -*- python -*-
# ex: set syntax=python:
#
# ProbeBasic Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic = util.BuildFactory()
# fetch sources
factory_probe_basic.addStep(steps.GitHub(name="download probe_basic sources",
                                         repourl='git@github.com:kcjengr/probe_basic.git',
                                         mode='full',
                                         submodules=True,
                                         workdir="sources/"))


# install qtpyvcp
factory_probe_basic.addStep(steps.ShellCommand(
    name="install qtpyvcp from pip",
    command=["python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    workdir="sources/"))


# install sources
factory_probe_basic.addStep(steps.ShellCommand(
    name="install probe basic from sources",
    command=["python", "-m", "pip", "install", "--upgrade", "."],
    workdir="sources/"))

# build binaries and wheel for distribution
factory_probe_basic.addStep(steps.ShellCommand(
    name="build binaries and wheel for distribution",
    command=["python", "setup.py", "bdist_wheel"],
    workdir="sources/"))

# build source for distribution
factory_probe_basic.addStep(steps.ShellCommand(
    name="build source for distribution",
    command=["python", "setup.py", "sdist"],
    workdir="sources/"))


# publish on pypi
factory_probe_basic.addStep(steps.ShellCommand(
    command=["pip", "install", "--upgrade", "twine"],
    workdir="sources/"))

factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/buildbot/.local/bin/twine",
             "upload",
             "--repository",
             "probebasicpypi",
             "dist/probe_basic*.tar.gz"],
    workdir="sources/"))

# publish on github
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/buildbot/buildbot/worker/probe_basic/sources/.scripts/publish_github_release.sh",
             "kcjengr/probe_basic", util.Property("branch")],
    workdir="sources/"))


# add version and date to installer package file
factory_probe_basic.addStep(
    steps.ShellCommand(workdir="sources/",
                       command=["python",
                                "pb-installer/scripts/create_probe_basic_package_config.py",
                                "pb-installer/templates/probe_basic_package_template.xml",
                                "pb-installer/packages/com.probebasic.core/meta/package.xml",
                                util.Property("branch")]
                       ))

# add version and date to installer config file
factory_probe_basic.addStep(
    steps.ShellCommand(workdir="sources/",
                       command=["python",
                                "pb-installer/scripts/create_config.py",
                                "pb-installer/templates/config_template.xml",
                                "pb-installer/config/config.xml",
                                "http://repository.qtpyvcp.com/repo/pb/repo",
                                util.Property("branch")]
                       ))

# copy files to installer directories
factory_probe_basic.addStep(steps.CopyDirectory(name="copy probebasic builds to the installer core package",
                                                src="sources/dist",
                                                dest="sources/pb-installer/packages/com.probebasic.core/data/"))

# sim files to installer directories
factory_probe_basic.addStep(steps.CopyDirectory(name="copy probebasic configs to the installer sim package",
                                                src="sources/config",
                                                dest="sources/pb-installer/packages/com.probebasic.sim/data/probe_basic/"))



# configure the installer
factory_probe_basic.addStep(steps.ShellCommand(name="configure the installer",
                                               command=["qmake"],
                                               workdir="sources/pb-installer",
                                               env={"QT_SELECT": "qt5",
                                                    "PB_VERSION": util.Property("branch")}))

# build the installer
factory_probe_basic.addStep(steps.Compile(name="compile the installer",
                                          command=["make"],
                                          workdir="sources/pb-installer",
                                          env={"QT_SELECT": "qt5"}))

# copy the packages to repository
factory_probe_basic.addStep(steps.CopyDirectory(name="copy the packages to repository",
                                                src="sources/pb-installer/repo",
                                                dest="/home/buildbot/repo/pb"))

# copy the installer to repository
factory_probe_basic.addStep(steps.CopyDirectory(name="copy the installer to repository",
                                                src="sources/pb-installer/bin",
                                                dest="/home/buildbot/repo/pb"))


factory_probe_basic.addStep(steps.RemoveDirectory(name="delete copy of the local repo", dir="sources/pb-installer/repo"))
factory_probe_basic.addStep(steps.RemoveDirectory(name="delete build directory", dir="sources/build/"))
factory_probe_basic.addStep(steps.RemoveDirectory(name="delete dist directory", dir="sources/dist/"))


factory_probe_basic.addStep(steps.GitHub(name="download static docs",
                                         repourl='git@github.com:kcjengr/probe_basic.git',
                                         origin="origin",
                                         branch="gh-pages",
                                         mode='full',
                                         workdir="docs/"))

factory_probe_basic.addStep(steps.ShellCommand(name="reset gh-pages",
                                               command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
                                               workdir="docs/"))
                                                   
factory_probe_basic.addStep(steps.ShellCommand(name="delete git index",
                                               command=["rm", ".git/index"],
                                               workdir="docs/"))
                                                   
factory_probe_basic.addStep(steps.ShellCommand(name="clean gh-pages",
                                               command=["git", "clean", "-fdx"],
                                               workdir="docs/"))

factory_probe_basic.addStep(
    steps.Sphinx(
        name="compile sphinx docs",
        haltOnFailure=True,
        sphinx="/home/buildbot/.local/bin/sphinx-build",
        sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic/docs/",
        sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic/sources/docs_src/source/",
        strict_warnings=False,
        env={"LANG": "en_EN.UTF-8"},
        workdir="docs/"))
 
factory_probe_basic.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
factory_probe_basic.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
factory_probe_basic.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
