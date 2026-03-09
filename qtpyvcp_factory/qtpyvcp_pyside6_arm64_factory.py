# -*- python3 -*-
# ex: set syntax=python3:

# QtPyVCP Stable Factory pyside6 arm64

import os

from buildbot.plugins import steps, util

factory_qtpyvcp_pyside6_arm64 = util.BuildFactory()

# download sources
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.GitHub(
        name="download sources",
        repourl="git@github.com:kcjengr/qtpyvcp.git",
        branch="pyside6",
        mode="full",
        submodules=False,
        workdir="sources/",
    )
)
# git fetch
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="git fetch",
        command=["/bin/sh", "-c", "git fetch --all"],
        workdir="sources/",
    )
)

# git pull
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="git pull",
        command=["/bin/sh", "-c", "git pull --no-rebase origin pyside6"],
        workdir="sources/",
    )
)

# get git tag
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# checkout the tag
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="checkout tag",
        command=["git", "checkout", util.Interpolate("%(prop:tag)s")],
        workdir="sources/",
    )
)

# update venv
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="update venv",
        command=["/home/bb/.venv/bin/python", "-m", "pip", "install", "-U", "-e", "."],
        workdir="sources/",
    )
)

# not needed by release
# # get git commit count since last tag
# factory_qtpyvcp_pyside6_arm64.addStep(
#     steps.SetPropertyFromCommand(
#         name="get git commit count since last tag",
#         command=[
#             "git",
#             "rev-list",
#             "--count",
#             "--branches",
#             util.Interpolate("^refs/tags/%(prop:tag)s"),
#         ],
#         property="minor_version",
#         workdir="sources/",
#     )
# )

# store version file
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="store version file",
        command=[
            "/bin/sh",
            "-c",
            util.Interpolate("echo %(prop:tag)s > qtpyvcp_version.txt"),
        ],
        workdir="/home/bb/versions/",
    )
)

# create changelog
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="create changelog",
        env={"EMAIL": "j.l.toledano.l@gmail.com"},
        command=[
            "dch",
            "--create",
            "--distribution",
            "trixie",
            "--package",
            "qtpyvcp",
            "--newversion",
            util.Interpolate("%(prop:tag)s"),
            "Trixie version.",
        ],
        workdir="sources/",
    )
)

# build debs
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="clean stale native artifacts",
        command=[
            "/bin/sh",
            "-c",
            "find src/qtpyvcp/native -type f \\( "
            "-name '*x86_64-linux-gnu.so' -o -name '*amd64*.so' \\) -delete",
        ],
        workdir="sources/",
    )
)

# build debs
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="build debs",
        env={"DEB_BUILD_OPTIONS": "nocheck"},
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources/",
    )
)

# upload files to http server
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.FileUpload(
        name="upload files to http server",
        workersrc=util.Interpolate(
            "/home/bb/work/qtpyvcp-pyside6-arm64/python3-qtpyvcp_%(prop:tag)s_arm64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/repo/qtpyvcp-pyside6-arm64/python3-qtpyvcp_%(prop:tag)s_arm64.deb"
        ),
        mode=0o644,
    )
)

# upload files to apt server
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.FileUpload(
        name="upload files to apt server",
        workersrc=util.Interpolate(
            "/home/bb/work/qtpyvcp-pyside6-arm64/python3-qtpyvcp_%(prop:tag)s_arm64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/debian/apt/pool/main/trixie/python3-qtpyvcp_%(prop:tag)s_arm64.deb"
        ),
    )
)


# scan new packages in apt repository
factory_qtpyvcp_pyside6_arm64.addStep(
    steps.MasterShellCommand(
        name="scan new packages in apt repository",
        command=["sh", "/home/buildbot/buildbot/master/scripts/do_apt_trixie.sh"],
        workdir="/home/buildbot/debian/apt",
    )
)
