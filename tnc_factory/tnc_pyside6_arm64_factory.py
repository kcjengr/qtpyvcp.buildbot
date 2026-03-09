# -*- python3 -*-
# ex: set syntax=python3:

# TNC Stable Factory pyside6 arm64

from buildbot.plugins import steps, util

factory_tnc_pyside6_arm64 = util.BuildFactory()


# download sources
factory_tnc_pyside6_arm64.addStep(
    steps.Git(
        name="download sources",
        repourl="git@github.com:kcjengr/turbonc.git",
        mode="full",
        method="clean",
        tags=True,
        submodules=False,
        workdir="sources/",
    )
)
# get git tag
factory_tnc_pyside6_arm64.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# update venv
#
factory_tnc_pyside6_arm64.addStep(
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
# checkout the tag
factory_tnc_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="checkout tag",
        command=["git", "checkout", util.Interpolate("%(prop:tag)s")],
        workdir="sources/",
    )
)

# get git commit count since last tag
factory_tnc_pyside6_arm64.addStep(
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

# get git tag
factory_tnc_pyside6_arm64.addStep(
    steps.SetPropertyFromCommand(
        name="get git tag",
        command=["git", "describe", "--abbrev=0", "--tags"],
        property="tag",
        workdir="sources/",
    )
)

# compile resources
factory_tnc_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="compile resources", command=["qcompile", "."], workdir="sources/"
    )
)

# delete previous changelog
factory_tnc_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="Delete previous changelog",
        env={},
        command=["rm", "-rf", "debian/changelog"],
        workdir="sources/",
    )
)

# create changelog
factory_tnc_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="create changelog",
        env={"EMAIL": "j.l.toledano.l@gmail.com"},
        command=[
            "dch",
            "--create",
            "--distribution",
            "stable",
            "--package",
            "turbonc",
            "--newversion",
            util.Interpolate("%(prop:tag)s"),
            "Stable version.",
        ],
        workdir="sources/",
    )
)

# ~ # set poetry version number for wheel build
# ~ factory_tnc_pi4.addStep(steps.ShellCommand(
# ~ name="set poetry ver number",
# ~ command=["python3", "-m", "poetry", "config", "version", util.Interpolate("%(prop:tag)s")],
# ~ workdir="sources/"))

# ~ # build pypi
# ~ factory_tnc_pi4.addStep(steps.ShellCommand(
# ~ name="build tar.gz and wheel",
# ~ command=["python3", "-m", "poetry", "build"],
# ~ workdir="sources/"))

# ~ # upload them to pypi.org
# ~ factory_tnc_pi4.addStep(steps.ShellCommand(
# ~ name="upload tar.gz to pypi",
# ~ command=["twine", "upload", "--repository", "pypi", util.Interpolate("dist/turbonc-%(prop:tag)s-py3-none-any.whl"), util.Interpolate("dist/turbonc-%(prop:tag)s.tar.gz")],
# ~ workdir="sources/"))

# build debs
factory_tnc_pyside6_arm64.addStep(
    steps.ShellCommand(
        name="build debs",
        env={"DEB_BUILD_OPTIONS": "nocheck"},
        command=["dpkg-buildpackage", "-b", "-uc"],
        workdir="sources/",
    )
)
# upload files to http server
factory_tnc_pyside6_arm64.addStep(
    steps.FileUpload(
        name="upload files to http server",
        workersrc=util.Interpolate(
            "/home/bb/work/turbonc-pyside6-arm64/python3-turbonc_%(prop:tag)s_arm64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/repo/tnc-pyside6-arm64/python3-turbonc_%(prop:tag)s_arm64.deb"
        ),
        mode=0o644,
    )
)

# upload files to apt server
factory_tnc_pyside6_arm64.addStep(
    steps.FileUpload(
        name="upload files to apt server",
        workersrc=util.Interpolate(
            "/home/bb/work/turbonc-pyside6-arm64/python3-turbonc_%(prop:tag)s_arm64.deb"
        ),
        masterdest=util.Interpolate(
            "/home/buildbot/debian/apt/pool/main/trixie/python3-turbonc_%(prop:tag)s_arm64.deb"
        ),
    )
)


# scan new packages in apt repository
factory_tnc_pyside6_arm64.addStep(
    steps.MasterShellCommand(
        name="scan new packages in apt repository",
        command="/home/buildbot/buildbot/master/scripts/do_apt_trixie.sh",
    )
)
