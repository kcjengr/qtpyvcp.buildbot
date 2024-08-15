# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Develop Factory

import os

from buildbot.plugins import steps, util

factory_qtpyvcp_pi4_dev = util.BuildFactory()

# download sources
factory_qtpyvcp_pi4_dev.addStep(steps.GitHub(name="download sources",
                                         repourl='git@github.com:kcjengr/qtpyvcp.git',
                                         branch='main',
                                         mode='full',
                                         submodules=False,
                                         workdir="sources/"))

# get git tag
factory_qtpyvcp_pi4_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_qtpyvcp_pi4_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# store version file
factory_qtpyvcp_pi4_dev.addStep(steps.ShellCommand(
    name="store version file",
    command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > qtpyvcp_dev_version.txt')],
    workdir="/home/buildbot/versions/"))

# create changelog
factory_qtpyvcp_pi4_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "qtpyvcp", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Development version."],
    workdir="sources/"))

# build debs
factory_qtpyvcp_pi4_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy files to the http repo on .13 machine
factory_qtpyvcp_pi4_dev.addStep(steps.FileUpload(
    name="copy files to the http repo",
    workersrc=util.Interpolate("/home/buildbot/workdir/qtpyvcp-pi4-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/qtpyvcp-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))


# copy new files to the apt repo on .13 machine
factory_qtpyvcp_pi4_dev.addStep(steps.FileUpload(
    name="copy files to repo",
    workersrc=util.Interpolate("/home/buildbot/workdir/qtpyvcp-pi4-dev/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/develop/python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")
    )
)


# clean up the workdir of old deb files after copying
factory_qtpyvcp_pi4_dev.addStep(steps.ShellCommand(
    name="check for deb files in workdir",
    command=["ls", "-l", util.Interpolate("python3-qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")]
    )
)


factory_qtpyvcp_pi4_dev.addStep(steps.ShellCommand(
    name="check for change files in workdir",
    command=["ls", "-l", util.Interpolate("qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.changes")]
    )
)


factory_qtpyvcp_pi4_dev.addStep(steps.ShellCommand(
    name="check for buildinfo files in workdir",
    command=["ls", "-l", util.Interpolate("qtpyvcp_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.buildinfo")]
    )
)

#scan new packages in apt repository
factory_qtpyvcp_pi4_dev.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command="/home/buildbot/buildbot/master/scripts/do_apt_develop.sh"
    )
)

