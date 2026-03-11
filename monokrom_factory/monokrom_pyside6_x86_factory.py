# -*- python3 -*-
# ex: set syntax=python3:
#
# Monokrom Stable amd64 Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_monokrom_pyside6_x86 = util.BuildFactory()


# download sources
factory_monokrom_pyside6_x86.addStep(steps.GitHub(name="download sources",
                                             repourl='git@github.com:kcjengr/monokrom.git',
                                             branch='pyside6',
                                             mode='full',
                                             method="clean",
                                             tags=True,
                                             submodules=False,
                                             workdir="sources/"))

# get git tag
factory_monokrom_pyside6_x86.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# checkout the tag
factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(
    name="checkout tag",
    command=["git", "checkout", util.Interpolate("%(prop:tag)s")],
    workdir="sources/"))

# delete previous changelog
factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(
    name="Delete previous changelog",
    env={},
    command=["rm", "-rf", "debian/changelog"],
    workdir="sources/"))

# create changelog
factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "james@snaggingpixels.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "monokrom", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable version."],
    workdir="sources/"))

# build debs
factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# upload files to http server
factory_monokrom_pyside6_x86.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/monokrom-pyside6-x86/python3-monokrom_%(prop:tag)s_amd64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/monokrom-pyside6-x86-dev/python3-monokrom_%(prop:tag)s_amd64.deb"),
    mode=0o644))

# upload files to apt server
factory_monokrom_pyside6_x86.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/monokrom-pyside6-x86/python3-monokrom_%(prop:tag)s_amd64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/trixie/python3-monokrom_%(prop:tag)s_amd64.deb")))


# scan new packages in apt repository
factory_monokrom_pyside6_x86.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie.sh"],
    workdir="/home/buildbot/debian/apt"))


#
# Docs
#

# factory_monokrom_pyside6_x86.addStep(steps.GitHub(name="downlaod static docs",
#                                              repourl='git@github.com:kcjengr/monokrom.git',
#                                              origin="origin",
#                                              branch="gh-pages",
#                                              mode='full',
#                                              workdir="docs/"))
#
# factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(name="reset gh-pages",
#                                                    command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
#                                                    workdir="docs/"))
#
# factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(name="delete git index",
#                                                    command=["rm", ".git/index"],
#                                                    workdir="docs/"))
#
# factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(name="clean gh-pages",
#                                                    command=["git", "clean", "-fdx"],
#                                                    workdir="docs/"))
#
# factory_monokrom_pyside6_x86.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/usr/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/monokrom-dev/docs/",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/monokrom-dev/sources/docs_src/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="docs/"))
#
# factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_monokrom_pyside6_x86.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
