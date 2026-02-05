# -*- python3 -*-
# ex: set syntax=python3:

# TNC Develop Factory arm64

from buildbot.plugins import steps, util

factory_tnc_pyqt5_arm64_dev = util.BuildFactory()

# download sources
factory_tnc_pyqt5_arm64_dev.addStep(steps.GitHub(name="download sources",
                                                 repourl='git@github.com:kcjengr/turbonc.git',
                                                 mode='full',
                                                 method="clean",
                                                 tags=True,
                                                 submodules=False,
                                                 workdir="sources/"))
# get git tag
factory_tnc_pyqt5_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_tnc_pyqt5_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# get git tag
# factory_tnc_pyqt5_arm64_dev.addStep(steps.SetPropertyFromCommand(
#     name="get git tag",
#     command=["git", "describe", "--abbrev=0", "--tags"],
#     property="tag",
#     workdir="sources/"))

# get git commit count since last tag
# factory_tnc_pyqt5_arm64_dev.addStep(steps.SetPropertyFromCommand(
#     name="get git commit count since last tag",
#     command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
#     property="minor_version",
#     workdir="sources/"))

# store version file
# factory_tnc_pyqt5_arm64_dev.addStep(steps.ShellCommand(
#     name="store version file",
#     command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > tnc_dev_version.txt')],
#     workdir="/home/bb/versions/"))

# compile resources
# disabled, done in deb build step
# factory_tnc_dev.addStep(steps.ShellCommand(
#     name="compile resources",
#     command=["qcompile", "."],
#     workdir="sources/"))

# factory_tnc_pyqt5_arm64_dev.addStep(steps.ShellCommand(
#         name="build wheel with poetry",
#         command=["/home/bb/.venv/bin/python3", "-m", "poetry", "build"],
#         workdir="sources/"
#     )
# )

# delete previous changelog
factory_tnc_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="Delete previous changelog",
    env={},
    command=["rm", "-rf", "debian/changelog"],
    workdir="sources/"))

# create changelog
factory_tnc_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "turbonc", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Development version."],
    workdir="sources/"))

# build debs
factory_tnc_pyqt5_arm64_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={
        'DEB_BUILD_OPTIONS': "nocheck",
        'PYTHONPATH': "/home/bb/.venv"
    },
    command=["debuild", "-b", "-uc", "-us"],
    workdir="sources/"))

# upload files to http server
factory_tnc_pyqt5_arm64_dev.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/turbonc-pyqt5-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/turbonc-pyqt5-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))

# upload files to apt server
factory_tnc_pyqt5_arm64_dev.addStep(steps.FileUpload(
    name="upload files to apt server",
    workersrc=util.Interpolate("/home/bb/work/turbonc-pyqt5-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/bookworm-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))


# scan new packages in apt repository
factory_tnc_pyqt5_arm64_dev.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_bookworm_dev.sh"],
    workdir="/home/buildbot/debian/apt"))



# # delete docs directory
# factory_tnc_dev.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))
#
# factory_tnc_dev.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/qtpyvcp-dev/docs",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/qtpyvcp-dev/sources/docs/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="sources/docs/source/"
#     )
# )
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="Initialize docs repository",
#                                                command=["git", "init"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="add remote repository",
#                                                command=["git", "remote", "add", "origin", "git@github.com:kcjengr/qtpyvcp.git"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="switch branch",
#                                                command=["git", "checkout", "-b", "gh-pages"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="add docs",
#                                                command=["git", "add", "."],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="commit docs",
#                                                command=["git", "commit", "-m", "Deploy docs"],
#                                                workdir="docs/"))
#
# factory_tnc_dev.addStep(steps.ShellCommand(name="push docs",
#                                                command=["git", "push", "--force", "origin", "gh-pages"],
#                                                workdir="docs/"))
