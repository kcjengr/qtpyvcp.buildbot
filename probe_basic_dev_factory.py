# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_dev = util.BuildFactory()


# download sources
factory_probe_basic_dev.addStep(steps.GitHub(name="download sources",
                                             repourl='git@github.com:kcjengr/probe_basic.git',
                                             branch='main',
                                             mode='full',
                                             submodules=False,
                                             workdir="sources/"))
# get git tag
factory_probe_basic_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit ID
factory_probe_basic_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit ID",
    command=["git", "rev-parse", "--short","HEAD"],
    property="commit_id",
    workdir="sources/"))

# compile resources
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="compile resources",
    command=["qcompile", "."],
    command=["dch", "--create", "--distribution", "unstable", "--package", "probe-basic", "--newversion", util.Interpolate("%(prop:tag)s.dev"), "Unstable Release version."],
    workdir="sources/"))

# create changelog
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    workdir="sources/"))

# build debs
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# move files to repo
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="move files to repo",
    command=["mv",
             util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb"),
             "/home/buildbot/repo/probe-basic-dev/"],
    workdir="sources/"))
