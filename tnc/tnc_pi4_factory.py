# -*- python3 -*-
# ex: set syntax=python3:
#
# TurBoNC VCP Develop Factory
#

from buildbot.plugins import steps, util
from packaging.version import Version, parse

factory_tnc_pi4 = util.BuildFactory()


# download sources
factory_tnc_pi4.addStep(steps.Git(name="download sources",
                                     repourl='git@github.com:kcjengr/turbonc.git',
                                     mode='full',
                                     method="clean",
                                     tags=True,
                                     shallow=True,
                                     submodules=False,
                                     workdir="sources/"))

# get git tag
factory_tnc_pi4.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# compile resources
factory_tnc_pi4.addStep(steps.ShellCommand(
    name="compile resources",
    command=["qcompile", "."],
    workdir="sources/"))

# create changelog
factory_tnc_pi4.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "lcvette1@gmail.com"},
    command=["dch", "--create", "--distribution", "stable", "--package", "turbonc", "--newversion", util.Interpolate("%(prop:tag)s"), "Stable version."],
    workdir="sources/"))

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
factory_tnc_pi4.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))

# copy files to the http repo
# factory_tnc_pi4.addStep(steps.FileUpload(
#     name="copy files to the http repo",
#     workersrc=util.Interpolate("/home/buildbot/workdir/turbonc-pi4/python3-turbonc_%(prop:tag)s_arm64.deb"),
#      masterdest=util.Interpolate("/home/buildbot/repo/turbonc/python3-turbonc_%(prop:tag)s_arm64.deb")
#     )
# )


# delete old files from apt directory
# factory_tnc_pi4.addStep(steps.ShellCommand(
#     name="delete files from apt directory",
#     command=["sh",
#              "/home/buildbot/buildbot/master/scripts/clean_apt_develop.sh",
#              util.Interpolate("python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")
#             ],
#     workdir="sources/"))

# move new files to the apt repo
factory_tnc_pi4.addStep(steps.FileUpload(
    name="move new files to the apt repo",
    workersrc=util.Interpolate("/home/buildbot/workdir/turbonc-pi4/python3-turbonc_%(prop:tag)s_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/stable/python3-turbonc_%(prop:tag)s_arm64.deb")
    )
)

# delete files from build directory
# factory_tnc_pi4.addStep(steps.ShellCommand(
#     name="delete files from build directory",
#     command=["rm", util.Interpolate("/home/buildbot/buildbot/worker/monokrom-dev/python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")],
#     workdir="sources/"))

# scan new packages in apt repository
factory_tnc_pi4.addStep(steps.MasterShellCommand(
    name="scan new packages in apt repository",
    command="/home/buildbot/buildbot/master/scripts/do_apt_stable.sh"
    )
)



# factory_tnc_pi4.addStep(steps.GitHub(name="downlaod static docs",
#                                              repourl='git@github.com:kcjengr/probe_basic.git',
#                                              origin="origin",
#                                              branch="gh-pages",
#                                              mode='full',
#                                              workdir="docs/"))
#
# factory_tnc_pi4.addStep(steps.ShellCommand(name="reset gh-pages",
#                                                    command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
#                                                    workdir="docs/"))
#
# factory_tnc_pi4.addStep(steps.ShellCommand(name="delete git index",
#                                                    command=["rm", ".git/index"],
#                                                    workdir="docs/"))
#
# factory_tnc_pi4.addStep(steps.ShellCommand(name="clean gh-pages",
#                                                    command=["git", "clean", "-fdx"],
#                                                    workdir="docs/"))
#
# factory_tnc_pi4.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/probe_basic-dev/docs/",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/probe_basic-dev/sources/docs_src/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="docs/"))
#
# factory_monokrom_pi4_dev.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_monokrom_pi4_dev.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_monokrom_pi4_dev.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
