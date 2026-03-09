# -*- python3 -*-
# ex: set syntax=python3:

# TNC Develop Factory pyside6 arm64

from buildbot.plugins import steps, util

factory_tnc_pyside6_arm64_dev = util.BuildFactory()

# download sources
factory_tnc_pyside6_arm64_dev.addStep(
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
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="git fetch",
        command=["/bin/sh", "-c", "git fetch --all"],
        workdir="sources/",
    )
)

# git pull
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="git pull",
        command=["/bin/sh", "-c", "git pull origin pyside6"],
        workdir="sources/",
    )
)

# update venv
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="update venv",
        command=[
            "/home/bb/.venv_dev/bin/python",
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

# get git tag
factory_tnc_pyside6_arm64_dev.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# get git commit count since last tag
factory_tnc_pyside6_arm64_dev.addStep(
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
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="store version file",
        command=[
            "/bin/sh",
            "-c",
            util.Interpolate(
                "echo %(prop:tag)s-%(prop:minor_version)s > tnc_dev_version.txt"
            ),
        ],
        workdir="/home/bb/versions/",
    )
)

# delete previous changelog
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="Delete previous changelog",
        env={},
        command=["rm", "-rf", "debian/changelog"],
        workdir="sources/",
    )
)

# create changelog
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="create changelog",
        env={"EMAIL": "j.l.toledano.l@gmail.com"},
        command=[
            "dch",
            "--create",
            "--distribution",
            "trixie-dev",
            "--package",
            "turbonc",
            "--newversion",
            util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"),
            "Development version.",
        ],
        workdir="sources/",
    )
)

# build debs
factory_tnc_pyside6_arm64_dev.addStep(
    steps.ShellCommand(
        name="build debs",
        env={"DEB_BUILD_OPTIONS": "nocheck"},
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources/",
    )
)

# upload files to http server
factory_tnc_pyside6_arm64_dev.addStep(
    steps.FileUpload(
        name="upload files to http server",
        workersrc=util.Interpolate(
            "/home/bb/work/turbonc-pyside6-arm64-dev/"
            "python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/repo/turbonc-pyside6-arm64-dev/"
            "python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"
        ),
        mode=0o644,
    )
)

# upload files to apt server
factory_tnc_pyside6_arm64_dev.addStep(
    steps.FileUpload(
        name="upload files to apt server",
        workersrc=util.Interpolate(
            "/home/bb/work/turbonc-pyside6-arm64-dev/"
            "python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/debian/apt/pool/main/trixie-dev/"
            "python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"
        ),
    )
)

# scan new packages in apt repository
factory_tnc_pyside6_arm64_dev.addStep(
    steps.MasterShellCommand(
        name="scan new packages in apt repository",
        command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie_dev.sh"],
        workdir="/home/buildbot/debian/apt",
    )
)
