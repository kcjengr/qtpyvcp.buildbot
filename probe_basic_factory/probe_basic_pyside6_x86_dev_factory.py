# -*- python3 -*-
# ex: set syntax=python3:
#
# ProbeBasic Develop Factory pyside6 x86
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_probe_basic_pyside6_x86_dev = util.BuildFactory()

# download sources
factory_probe_basic_pyside6_x86_dev.addStep(
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
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.ShellCommand(
        name="git fetch",
        command=["/bin/sh", "-c", "git fetch --all"],
        workdir="sources/",
    )
)

# git pull
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.ShellCommand(
        name="git pull",
        command=["/bin/sh", "-c", "git pull origin pyside6"],
        workdir="sources/",
    )
)

# update venv
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.ShellCommand(
        name="update venv",
        command=["/home/bb/.venv/bin/python", "-m", "pip", "install", "-U", "-e", "."],
        workdir="sources/",
    )
)

# get git tag
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# get git commit count since last tag
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.SetPropertyFromCommand(
        name="get git commit count since last tag",
        command=[
            "git",
            "rev-list",
            "--count",
            "--branches",
            util.Interpolate("^refs/tags/%(prop:tag)s"),
        ],
        property="minor_version",
        workdir="sources/",
    )
)

# store version file
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.ShellCommand(
        name="store version file",
        command=[
            "/bin/sh",
            "-c",
            util.Interpolate(
                "echo %(prop:tag)s-%(prop:minor_version)s > pb_dev_version.txt"
            ),
        ],
        workdir="/home/bb/versions/",
    )
)

# create changelog
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.ShellCommand(
        name="create changelog",
        env={"EMAIL": "lcvette1@gmail.com"},
        command=[
            "dch",
            "--create",
            "--distribution",
            "unstable",
            "--package",
            "probe-basic",
            "--newversion",
            util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"),
            "Unstable Release version.",
        ],
        workdir="sources/",
    )
)

# build debs
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.ShellCommand(
        name="build debs",
        env={"DEB_BUILD_OPTIONS": "nocheck"},
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources/",
    )
)

# upload files to http server
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.FileUpload(
        name="upload files to http server",
        workersrc=util.Interpolate(
            "/home/bb/work/probe_basic-pyside6-x86-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/repo/probe_basic-pyside6-x86-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"
        ),
        mode=0o644,
    )
)

# upload files to apt server
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.FileUpload(
        name="upload files to apt server",
        workersrc=util.Interpolate(
            "/home/bb/work/probe_basic-pyside6-x86-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/debian/apt/pool/main/trixie-dev/python3-probe-basic_%(prop:tag)s-%(prop:minor_version)s.dev_amd64.deb"
        ),
    )
)

# scan new packages in apt repository
factory_probe_basic_pyside6_x86_dev.addStep(
    steps.MasterShellCommand(
        name="scan new packages in apt repository",
        command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie_dev.sh"],
        workdir="/home/buildbot/debian/apt",
    )
)
