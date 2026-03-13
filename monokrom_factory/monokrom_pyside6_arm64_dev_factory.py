# -*- python3 -*-
# ex: set syntax=python3:
#
# MonoKrom VCP Develop arm64 Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_monokrom_pyside6_arm64_dev = util.BuildFactory()


# download sources
factory_monokrom_pyside6_arm64_dev.addStep(steps.GitHub(name="download sources",
                                             repourl='git@github.com:kcjengr/monokrom.git',
                                             branch='pyside6',
                                             mode='full',
                                             method="clean",
                                             tags=True,
                                             submodules=False,
                                             workdir="sources/"))

# get git tag
factory_monokrom_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_monokrom_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# store version file
factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > monokrom_arm64_dev_version.txt')],
    workdir="/home/bb/versions/"))

# delete previous changelog
factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="Delete previous changelog",
    env={},
    command=["rm", "-rf", "debian/changelog"],
    workdir="sources/"))

# create changelog
factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "james@snaggingpixels.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "monokrom", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Develop version."],
    workdir="sources/"))

# build debs
factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))


# upload files to http server
factory_monokrom_pyside6_arm64_dev.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/monokrom-pyside6-arm64-dev/python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/monokrom-pyside6-arm64-dev/python3-qtpyvcp.monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    mode=0o644))

# upload files to apt server
factory_monokrom_pyside6_arm64_dev.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/monokrom-pyside6-arm64-dev/python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/trixie-dev/python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))


# scan new packages in apt repository
factory_monokrom_pyside6_arm64_dev.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie_dev.sh"],
    workdir="/home/buildbot/debian/apt"))


#
# Docs
#

# factory_monokrom_pyside6_arm64_dev.addStep(steps.GitHub(name="downlaod static docs",
#                                              repourl='git@github.com:kcjengr/probe_basic.git',
#                                              origin="origin",
#                                              branch="gh-pages",
#                                              mode='full',
#                                              workdir="docs/"))
#
# factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(name="reset gh-pages",
#                                                    command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
#                                                    workdir="docs/"))
#
# factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(name="delete git index",
#                                                    command=["rm", ".git/index"],
#                                                    workdir="docs/"))
#
# factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(name="clean gh-pages",
#                                                    command=["git", "clean", "-fdx"],
#                                                    workdir="docs/"))
#
# factory_monokrom_pyside6_arm64_dev.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic-dev/docs/",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic-dev/sources/docs_src/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="docs/"))
#
# factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_monokrom_pyside6_arm64_dev.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
