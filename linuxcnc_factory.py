# -*- python -*-
# ex: set syntax=python:
#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util

factory_linuxcnc = util.BuildFactory()

# fetch sources
factory_linuxcnc.addStep(
    steps.GitHub(
        name="download linuxcnc sources",
        repourl='https://github.com/turboss/linuxcnc.git',
        branch='python3_debs',
        mode='full',
        submodules=True,
        workdir="sources"
    )
)

factory_linuxcnc.addStep(
    steps.ShellCommand(
        name="source autogen.sh",
        command=["./autogen.sh"],
        workdir="sources/src"
    )
)

factory_linuxcnc.addStep(
    steps.ShellCommand(
        name="configure for debian",
        command=["./configure", "uspace"],
        workdir="sources/debian"
    )
)

factory_linuxcnc.addStep(
    steps.ShellCommand(
        name="check build deps",
        command=["dpkg-checkbuilddeps"],
        workdir="sources"
    )
)

factory_linuxcnc.addStep(
    steps.ShellCommand(
        name="build debian package",
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources"
    )
)
