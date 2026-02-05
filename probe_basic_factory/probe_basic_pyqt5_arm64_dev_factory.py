# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_pyqt5_arm64_dev = util.BuildFactory()


# download sources
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.GitHub(name="download sources",
                                             repourl='git@github.com:kcjengr/probe_basic.git',
                                             branch='main',
                                             mode='full',
                                             submodules=False,
                                             workdir="sources/"))

# git fetch
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="git fetch",
    command=["/bin/sh", "-c", "git fetch --all"],
    workdir="sources/"))

# get git tag
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# store version file
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > pb_dev_version.txt')],
    workdir="/home/bb/versions/"))

# create changelog
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "lcvette1@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "probe-basic", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Unstable Release version."],
    workdir="sources/"))

# build debs
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))


# upload files to http server
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/probe_basic-pyqt5-arm64-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/probe-basic-pyqt5-arm64-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb"),
    mode=0o644))

# upload files to apt server
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/probe_basic-pyqt5-arm64-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/bookworm-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))

# scan new packages in apt repository
factory_probe_basic_pyqt5_arm64_dev.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_bookworm_dev.sh"],
    workdir="/home/buildbot/debian/apt"))
