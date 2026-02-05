# -*- python3 -*-
# ex: set syntax=python3:

# TNC Stable Factory x86

from buildbot.plugins import steps, util

factory_tnc_pyqt5_x86 = util.BuildFactory()

# download sources
factory_tnc_pyqt5_x86.addStep(steps.GitHub(name="download sources",
                                           repourl='git@github.com:kcjengr/turbonc.git',
                                           branch='pyqt5',
                                           mode='full',
                                           method="clean",
                                           tags=True,
                                           submodules=False,
                                           workdir="sources/"))
# get git tag
factory_tnc_pyqt5_x86.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# store version file
factory_tnc_pyqt5_x86.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s > tnc_stable_version.txt')],
    workdir="/home/bb/versions/"))

# factory_tnc_pyqt5_x86.addStep(steps.ShellCommand(
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
factory_tnc_pyqt5_x86.addStep(steps.ShellCommand(
    name="Delete previous changelog",
    env={},
    command=["rm", "-rf", "debian/changelog"],
    workdir="sources/"))

# create changelog
factory_tnc_pyqt5_x86.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "turbonc", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable Release version."],
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
factory_tnc_pyqt5_x86.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck",
        'PYTHONPATH': "/home/bb/.venv"
    },
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))


# upload files to http server
factory_tnc_pyqt5_x86.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/turbonc-pyqt5-x86/python3-turbonc_%(prop:tag)s_amd64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/turbonc-pyqt5-x86/python3-turbonc_%(prop:tag)s_amd64.deb"),
    mode=0o644))

# upload files to apt server
factory_tnc_pyqt5_x86.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/turbonc-pyqt5-x86/python3-turbonc_%(prop:tag)s_amd64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/bookworm/python3-turbonc_%(prop:tag)s_amd64.deb")))


# scan new packages in apt repository
factory_tnc_pyqt5_x86.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_bookworm.sh"],
    workdir="/home/buildbot/debian/apt"))

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
