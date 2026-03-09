# -*- python3 -*-
# ex: set syntax=python3:

# TNC Stable Factory pyside6 x86

from buildbot.plugins import steps, util

factory_tnc_pyside6_x86 = util.BuildFactory()

# download sources
factory_tnc_pyside6_x86.addStep(
    steps.GitHub(
        name="download sources",
        repourl="git@github.com:kcjengr/turbonc.git",
        branch="pyside6",
        mode="full",
        submodules=False,
        workdir="sources/",
    )
)

# git fetch
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="git fetch",
        command=["/bin/sh", "-c", "git fetch --all"],
        workdir="sources/",
    )
)

# git pull
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="git pull",
        command=["/bin/sh", "-c", "git pull --no-rebase origin pyside6"],
        workdir="sources/",
    )
)

# get git tag
factory_tnc_pyside6_x86.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# checkout the tag
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="checkout tag",
        command=["git", "checkout", util.Interpolate("%(prop:tag)s")],
        workdir="sources/",
    )
)

# update venv
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="update venv",
        command=[
            "/home/bb/.venv/bin/python",
            "-m",
            "pip",
            "install",
            "-U",
            "-e",
            ".",
        ],
        workdir="sources/",
    )
)

# store version file
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="store version file",
        command=[
            "/bin/sh",
            "-c",
            util.Interpolate("echo %(prop:tag)s > tnc_stable_version.txt"),
        ],
        workdir="/home/bb/versions/",
    )
)

# create changelog
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="create changelog",
        env={"EMAIL": "j.l.toledano.l@gmail.com"},
        command=[
            "dch",
            "--create",
            "--distribution",
            "trixie",
            "--package",
            "turbonc",
            "--newversion",
            util.Interpolate("%(prop:tag)s"),
            "Trixie version.",
        ],
        workdir="sources/",
    )
)

# build debs
factory_tnc_pyside6_x86.addStep(
    steps.ShellCommand(
        name="build debs",
        env={"DEB_BUILD_OPTIONS": "nocheck"},
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources/",
    )
)

# upload files to http server
factory_tnc_pyside6_x86.addStep(
    steps.FileUpload(
        name="upload files to http server",
        workersrc=util.Interpolate(
            "/home/bb/work/turbonc-pyside6-x86/"
            "python3-turbonc_%(prop:tag)s_amd64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/repo/tnc-pyside6-x86/"
            "python3-turbonc_%(prop:tag)s_amd64.deb"
        ),
        mode=0o644,
    )
)

# upload files to apt server
factory_tnc_pyside6_x86.addStep(
    steps.FileUpload(
        name="upload files to apt server",
        workersrc=util.Interpolate(
            "/home/bb/work/turbonc-pyside6-x86/"
            "python3-turbonc_%(prop:tag)s_amd64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/debian/apt/pool/main/trixie/"
            "python3-turbonc_%(prop:tag)s_amd64.deb"
        ),
    )
)

# scan new packages in apt repository
factory_tnc_pyside6_x86.addStep(
    steps.MasterShellCommand(
        name="scan new packages in apt repository",
        command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie.sh"],
        workdir="/home/buildbot/debian/apt",
    )
)
