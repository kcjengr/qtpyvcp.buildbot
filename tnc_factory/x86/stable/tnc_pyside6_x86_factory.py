# -*- python3 -*-
# ex: set syntax=python3:

# TNC Stable Factory pyside6 x86

from buildbot.plugins import steps, util

factory_tnc_pyside6_x86 = util.BuildFactory()


# download sources
factory_tnc_pyside6_x86.addStep(steps.GitHub(name="download sources",
                                             repourl='https://github.com/kcjengr/turbonc.git',
                                             mode='full',
                                             method="clean",
                                             tags=True,
                                             submodules=False,
                                             workdir="sources/"))

# get git tag
factory_tnc_pyside6_x86.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_tnc_pyside6_x86.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# get git tag
# factory_tnc_pyside6_x86.addStep(steps.SetPropertyFromCommand(
#     name="get git tag",
#     command=["git", "describe", "--abbrev=0", "--tags"],
#     property="tag",
#     workdir="sources/"))

# factory_tnc_pyside6_x86.addStep(steps.ShellCommand(
#         name="build wheel with poetry",
#         command=["python3", "-m", "poetry", "build"],
#         workdir="sources/"
#     )
# )

# compile resources
# disabled, done in deb build step
# factory_tnc.addStep(steps.ShellCommand(
#     name="compile resources",
#     command=["qcompile", "."],
#     workdir="sources/"))

# delete previous changelog
factory_tnc_pyside6_x86.addStep(steps.ShellCommand(
    name="Delete previous changelog",
    env={},
    command=["rm", "-rf", "debian/changelog"],
    workdir="sources/"))

# create changelog
factory_tnc_pyside6_x86.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "turbonc", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable version."],
    workdir="sources/"))

# build pypi
# factory_tnc.addStep(steps.ShellCommand(
#     name="build tar.gz and wheel",
#     command=["python3", "-m", "poetry", "build"],
#     workdir="sources/"))
#
# # upload them to pypi.org
# factory_tnc.addStep(steps.ShellCommand(
#     name="upload tar.gz to pypi",
#     command=["twine", "upload", "--repository", "pypi", util.Interpolate("dist/turbonc-%(prop:tag)s-py3-none-any.whl"), util.Interpolate("dist/turbonc-%(prop:tag)s.tar.gz")],
#     workdir="sources/"))

# build debs
factory_tnc_pyside6_x86.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# # move new files to the apt repo
# factory_tnc_pyside6_x86.addStep(steps.FileUpload(
#     name="move new files to the apt repo",
#     workersrc=util.Interpolate("/home/buildbot/buildbot/worker/turbonc/python3-turbonc_%(prop:tag)s_amd64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/trixie/python3-turbonc_%(prop:tag)s_amd64.deb")
#     )
# )
#
# # scan new packages in apt repository
# factory_tnc_pyside6_x86.addStep(steps.ShellCommand(
#     name="scan new packages in apt repository",
#     command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie.sh"],
#     workdir="sources/"))

#
# factory_tnc.addStep(steps.GitHub(name="downlaod static docs",
#                                              repourl='git@github.com:kcjengr/probe_basic.git',
#                                              origin="origin",
#                                              branch="gh-pages",
#                                              mode='full',
#                                              workdir="docs/"))
#
# factory_tnc.addStep(steps.ShellCommand(name="reset gh-pages",
#                                                    command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
#                                                    workdir="docs/"))
#
# factory_tnc.addStep(steps.ShellCommand(name="delete git index",
#                                                    command=["rm", ".git/index"],
#                                                    workdir="docs/"))
#
# factory_tnc.addStep(steps.ShellCommand(name="clean gh-pages",
#                                                    command=["git", "clean", "-fdx"],
#                                                    workdir="docs/"))
#
# factory_tnc.addStep(
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
# factory_tnc.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_tnc.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_tnc.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
