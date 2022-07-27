# -*- python3 -*-
# ex: set syntax=python3:
#
# Conversational Gcode Debian Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_deb_dev = util.BuildFactory()

# fetch sources
factory_probe_basic_deb_dev.addStep(steps.GitHub(name="get sources",
                                             repourl='git@github.com:kcjengr/qtpyvcp/probe-basic.git',
                                             branch='debian',
                                             mode='full',
                                             submodules=False,
                                             workdir="sources/"))

# build debs
factory_probe_basic_deb_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy qtpyvcp deb to repo
factory_probe_basic_deb_dev.addStep(steps.ShellCommand(
    name="copy probe basic deb to repo",
    command=["cp", "python3-probe-basic_0.4-1_all.deb", "/home/buildbot/repo/probe-basic-deb-dev"],
    workdir="sources/.."))

# copy qtpyvcp deb to repo
factory_probe_basic_deb_dev.addStep(steps.ShellCommand(
    name="copy probe basic doc deb to repo",
    command=["cp", "python-probe-basic-doc_0.4-1_all.deb", "/home/buildbot/repo/probe-basic-deb-dev"],
    workdir="sources/.."))