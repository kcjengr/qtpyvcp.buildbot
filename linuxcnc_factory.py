#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util

factory_linuxcnc = util.BuildFactory()

# fetch sources
factory_linuxcnc.addStep(
    steps.GitHub(
        name="download linuxcnc sources",
        repourl='https://github.com/linuxcnc/linuxcnc.git',
        branch='master',
        mode='full',
        submodules=True,
        workdir="sources/"
    )
)

factory_linuxcnc.addStep(
    steps.ShellCommand(
        name="source autogen.sh",
        command=["./autogen.sh"],
        workdir="sources/"
    )
)

factory_linuxcnc.addStep(
    steps.ShellCommand(
        name="configure",
        command=["./configure", "--with-python=python3.7"],
        workdir="sources/"
    )
)

factory_linuxcnc.addStep(
    steps.Compile(
        name="compile",
        command=["make"],
        workdir="sources/pb-installer",
        env={"QT_SELECT": "qt5"}
    )
)