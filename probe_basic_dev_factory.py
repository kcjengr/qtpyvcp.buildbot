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

# store version file
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="store version file",
    command=["echo", util.Interpolate("%(prop:tag)s-%(prop:commit_id)s"), ">", "pb_verstion.txt"],
    workdir="sources/"))

# compile resources
# disabled, done in deb build step
# factory_probe_basic_dev.addStep(steps.ShellCommand(
#     name="compile resources",
#     command=["qcompile", "."],
#     workdir="sources/"))

# create changelog
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "lcvette1@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "probe-basic", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:commit_id)s.dev"), "Unstable Release version."],
    workdir="sources/"))

# build debs
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy files to the http repo
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="copy files to the http repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb"),
             "/home/buildbot/repo/probe-basic-dev/"],
    workdir="sources/"))


# delete old files from apt directory
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="delete files apt apt directory",
    command=["sh", "clean_apt_develop.sh"],
    workdir="sources/.scripts/"))

# copy new files to the apt repo
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="copy files to repo",
    command=["cp",
             util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb"),
             "/home/buildbot/debian/apt/pool/main/"],
    workdir="sources/"))

# delete files from build directory
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="delete files from build directory",
    command=["rm", util.Interpolate("/home/buildbot/buildbot/worker/probe_basic-dev/python3-probe-basic_%(prop:tag)s-%(prop:commit_id)s.dev_all.deb")],
    workdir="sources/"))

# scan new packages in apt repository
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "do_apt_develop.sh"],
    workdir="sources/.scripts/"))

factory_probe_basic_dev.addStep(steps.GitHub(name="downlaod static docs",
                                             repourl='git@github.com:kcjengr/probe_basic.git',
                                             origin="origin",
                                             branch="gh-pages",
                                             mode='full',
                                             workdir="docs/"))

factory_probe_basic_dev.addStep(steps.ShellCommand(name="reset gh-pages",
                                                   command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
                                                   workdir="docs/"))

factory_probe_basic_dev.addStep(steps.ShellCommand(name="delete git index",
                                                   command=["rm", ".git/index"],
                                                   workdir="docs/"))

factory_probe_basic_dev.addStep(steps.ShellCommand(name="clean gh-pages",
                                                   command=["git", "clean", "-fdx"],
                                                   workdir="docs/"))

factory_probe_basic_dev.addStep(
    steps.Sphinx(
        name="compile sphinx docs",
        haltOnFailure=True,
        sphinx="/home/buildbot/venv/bin/sphinx-build",
        sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic-dev/docs/",
        sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic-dev/sources/docs_src/source/",
        strict_warnings=False,
        env={"LANG": "en_EN.UTF-8"},
        workdir="docs/"))

factory_probe_basic_dev.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
factory_probe_basic_dev.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
factory_probe_basic_dev.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
