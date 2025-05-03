# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasi Stable Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic = util.BuildFactory()


# download sources
factory_probe_basic.addStep(steps.GitHub(name="download sources",
                                             repourl='git@github.com:kcjengr/probe_basic.git',
                                             branch='main',
                                             mode='full',
                                             submodules=False,
                                             workdir="sources/"))
# git fetch
factory_probe_basic.addStep(steps.ShellCommand(
    name="git fetch",
    command=["/bin/sh", "-c", "git fetch --all"],
    workdir="sources/"))


# git pull
factory_probe_basic.addStep(steps.ShellCommand(
    name="git pull",
    command=["/bin/sh", "-c", "git pull origin main"],
    workdir="sources/"))

# get git tag
factory_probe_basic.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# compile resources
factory_probe_basic.addStep(steps.ShellCommand(
    name="compile resources",
    command=["qcompile", "."],
    workdir="sources/"))

# create changelog
factory_probe_basic.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "lcvette1@gmail.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "probe-basic", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable version."],
    workdir="sources/"))

# build debs
factory_probe_basic.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy new files to the http repo
factory_probe_basic.addStep(steps.ShellCommand(
    name="copy files to http repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/probe_basic/python3-probe-basic_%(prop:tag)s_amd64.deb"),
             "/home/buildbot/repo/probe-basic/"],
    workdir="sources/"))

# copy new files to the apt repo
factory_probe_basic.addStep(steps.ShellCommand(
    name="copy files to apt repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/probe_basic/python3-probe-basic_%(prop:tag)s_amd64.deb"),
             "/home/buildbot/debian/apt/pool/main/stable/"],
    workdir="sources/"))

# more apt things
# scan new packages in apt repository
factory_probe_basic.addStep(steps.ShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_stable.sh"],
    workdir="sources/"))

factory_probe_basic.addStep(steps.GitHub(name="downlaod static docs",
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
        sphinx="/usr/bin/sphinx-build",
        sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic/docs/",
        sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic/sources/docs_src/source/",
        strict_warnings=False,
        env={"LANG": "en_EN.UTF-8"},
        workdir="docs/"))

factory_probe_basic.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
factory_probe_basic.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
factory_probe_basic.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
