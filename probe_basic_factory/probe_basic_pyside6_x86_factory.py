# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasic Stable Factory pyside6 x86
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_pyside6_x86 = util.BuildFactory()

# download sources
factory_probe_basic_pyside6_x86.addStep(
    steps.GitHub(
        name="download sources",
        repourl="git@github.com:kcjengr/probe_basic.git",
        branch="pyside6",
        mode="full",
        submodules=False,
        workdir="sources/",
    )
)

# git fetch
factory_probe_basic_pyside6_x86.addStep(
    steps.ShellCommand(
        name="git fetch",
        command=["/bin/sh", "-c", "git fetch --all"],
        workdir="sources/",
    )
)

# get git tag
factory_probe_basic_pyside6_x86.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# checkout the tag
factory_probe_basic_pyside6_x86.addStep(
    steps.ShellCommand(
        name="checkout tag",
        command=["git", "checkout", util.Interpolate("%(prop:tag)s")],
        workdir="sources/",
    )
)

# store version file
factory_probe_basic_pyside6_x86.addStep(
    steps.ShellCommand(
        name="store version file",
        command=[
            "/bin/sh",
            "-c",
            util.Interpolate("echo %(prop:tag)s > pb_stable_version.txt"),
        ],
        workdir="/home/bb/versions/",
    )
)

# create changelog
factory_probe_basic_pyside6_x86.addStep(
    steps.ShellCommand(
        name="create changelog",
        env={"EMAIL": "lcvette1@gmail.com"},
        command=[
            "dch",
            "--create",
            "--distribution",
            "trixie",
            "--package",
            "probe-basic",
            "--newversion",
            util.Interpolate("%(prop:tag)s"),
            "Trixie version.",
        ],
        workdir="sources/",
    )
)

# build debs
factory_probe_basic_pyside6_x86.addStep(
    steps.ShellCommand(
        name="build debs",
        env={"DEB_BUILD_OPTIONS": "nocheck"},
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources/",
    )
)

# upload files to http server
factory_probe_basic_pyside6_x86.addStep(
    steps.FileUpload(
        name="upload files to http server",
        workersrc=util.Interpolate(
            "/home/bb/work/probe_basic-pyside6-x86/python3-probe-basic_%(prop:tag)s_amd64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/repo/probe_basic-pyside6-x86/python3-probe-basic_%(prop:tag)s_amd64.deb"
        ),
        mode=0o644,
    )
)

# upload files to apt server
factory_probe_basic_pyside6_x86.addStep(
    steps.FileUpload(
        name="upload files to apt server",
        workersrc=util.Interpolate(
            "/home/bb/work/probe_basic-pyside6-x86/python3-probe-basic_%(prop:tag)s_amd64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/debian/apt/pool/main/trixie/python3-probe-basic_%(prop:tag)s_amd64.deb"
        ),
    )
)

# scan new packages in apt repository
factory_probe_basic_pyside6_x86.addStep(
    steps.MasterShellCommand(
        name="scan new packages in apt repository",
        command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie.sh"],
        workdir="/home/buildbot/debian/apt",
    )
)
