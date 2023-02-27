# -*- python3 -*-
# ex: set syntax=python3:
#
# QtPyVCP Debian Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_qtpyvcp_deb_dev = util.BuildFactory()

# fetch sources
factory_qtpyvcp_deb_dev.addStep(steps.GitHub(name="get sources",
                                             repourl='git@github.com:kcjengr/qtpyvcp.git',
                                             branch='main',
                                             mode='full',
                                             submodules=False,
                                             workdir="sources/"))

# build debs
factory_qtpyvcp_deb_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy qtpyvcp deb to repo
factory_qtpyvcp_deb_dev.addStep(steps.ShellCommand(
    name="copy qtpyvcp deb to repo",
    command=["cp", "python3-qtpyvcp_0.4-1_all.deb", "/home/buildbot/repo/qtpyvcp-deb-dev"],
    workdir="sources/.."))
