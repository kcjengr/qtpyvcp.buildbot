# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Develop Factory pyside6 arm64

import os

from buildbot.plugins import steps, util

factory_qtpyvcp_pyside6_arm64_dev = util.BuildFactory()

# download sources
factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.GitHub(name="download sources",
                                                       repourl='https://github.com/kcjengr/qtpyvcp.git',
                                                       branch='main',
                                                       mode='full',
                                                       submodules=False,
                                                       workdir="sources/"))

# get git tag
factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))


# create changelog
factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "qtpyvcp", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Development version."],
    workdir="sources/"))

# build debs
factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# upload files to http server
factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/qtpyvcp-pyside6-arm64-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/qtpyvcp-pyside6-arm64-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))

# upload files to apt server
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.FileUpload(
#     name="upload files to apt server",
#     workersrc=util.Interpolate("/home/bb/work/turbonc-pyside6-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/develop/python3-turbonc-arm_64_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))



# # copy files to the http repo on .13 machine
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.FileUpload(
#     name="copy files to the http repo",
#     workersrc=util.Interpolate("/home/buildbot/workdir/qtpyvcp-pi4-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/repo/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))
#
#
# # copy new files to the apt repo on .13 machine
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.FileUpload(
#     name="copy files to repo",
#     workersrc=util.Interpolate("/home/buildbot/workdir/qtpyvcp-pi4-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/develop/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")
#     )
# )
#
#
# # clean up the workdir of old deb files after copying
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.ShellCommand(
#     name="remove deb files from workdir",
#     command=["rm", util.Interpolate("python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")],
#     workdir="./"
#     )
# )
#
#
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.ShellCommand(
#     name="remove changes files from workdir",
#     command=["rm", util.Interpolate("qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.changes")],
#     workdir="./"
#     )
# )
#
#
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.ShellCommand(
#     name="rmove buildinfo files from workdir",
#     command=["rm", util.Interpolate("qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.buildinfo")],
#     workdir="./"
#     )
# )
#
# #scan new packages in apt repository
# factory_qtpyvcp_pyside6_arm64_dev.addStep(steps.MasterShellCommand(
#     name="scan new packages in apt repository",
#     command="/home/buildbot/buildbot/master/scripts/do_apt_develop.sh"
#     )
# )

