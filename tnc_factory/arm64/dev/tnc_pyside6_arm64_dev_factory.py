# -*- python3 -*-
# ex: set syntax=python3:

# TNC Develop Factory pyside6 arm64

from buildbot.plugins import steps, util

factory_tnc_pyside6_arm64_dev = util.BuildFactory()

# download sources
factory_tnc_pyside6_arm64_dev.addStep(steps.GitHub(name="download sources",
                                           repourl='git@github.com:kcjengr/turbonc.git',
                                           mode='full',
                                           method="clean",
                                           tags=True,
                                           submodules=False,
                                           workdir="sources/"))
# get git tag
factory_tnc_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git tag",
    command=["git", "describe", "--abbrev=0", "--tags"],
    property="tag",
    workdir="sources/"))

# get git commit count since last tag
factory_tnc_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
    name="get git commit count since last tag",
    command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
    property="minor_version",
    workdir="sources/"))

# get git tag
# factory_tnc_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
#     name="get git tag",
#     command=["git", "describe", "--abbrev=0", "--tags"],
#     property="tag",
#     workdir="sources/"))

# get git commit count since last tag
# factory_tnc_pyside6_arm64_dev.addStep(steps.SetPropertyFromCommand(
#     name="get git commit count since last tag",
#     command=["git", "rev-list", "--count", "--branches", util.Interpolate("^refs/tags/%(prop:tag)s")],
#     property="minor_version",
#     workdir="sources/"))

# # store version file
# factory_tnc_pyside6_arm64_dev.addStep(steps.ShellCommand(
#     name="store version file",
#     command=["/bin/sh", "-c", util.Interpolate('echo %(prop:tag)s-%(prop:minor_version)s > tnc_dev_version.txt')],
#     workdir="/home/pi/buildbot/versions/"))

# delete previous changelog
factory_tnc_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="Delete previous changelog",
    env={},
    command=["rm", "-rf", "debian/changelog"],
    workdir="sources/"))

# create changelog
factory_tnc_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="create changelog",
    env={'EMAIL': "j.l.toledano.l@gmail.com"},
    command=["dch", "--create", "--distribution", "unstable", "--package", "turbonc", "--newversion", util.Interpolate("%(prop:tag)s-%(prop:minor_version)s.dev"), "Unstable Release version."],
    workdir="sources/"))

# build debs
factory_tnc_pyside6_arm64_dev.addStep(steps.ShellCommand(
    name="build debs",
    env={'DEB_BUILD_OPTIONS': "nocheck"},
    command=["dpkg-buildpackage", "-b", "-uc"],
    workdir="sources/"))




# upload files to http server
factory_tnc_pyside6_arm64_dev.addStep(steps.FileUpload(
    name="upload files to http server",
    workersrc=util.Interpolate("/home/bb/work/turbonc-pyside6-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
    masterdest=util.Interpolate("/home/buildbot/repo/turbonc-pyside6-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))

# upload files to apt server
# factory_tnc_pyside6_arm64_dev.addStep(steps.FileUpload(
#     name="upload files to apt server",
#     workersrc=util.Interpolate("/home/bb/work/turbonc-pyside6-arm64-dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/develop/python3-turbonc-arm_64_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")))





# # copy files to the http repo
# factory_tnc_arm64.addStep(steps.FileUpload(
#     name="copy files to the http repo",
#     workersrc=util.Interpolate("/home/buildbot/workdir/turbonc-arm64_dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/repo/turbonc-arm64_dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")
#     )
# )
#
#
# # delete old files from apt directory
# # factory_tnc_arm64.addStep(steps.ShellCommand(
# #     name="delete files from apt directory",
# #     command=["sh",
# #              "/home/buildbot/buildbot/master/scripts/clean_apt_develop.sh",
# #              util.Interpolate("python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")
# #             ],
# #     workdir="sources/"))
#
# # move new files to the apt repo
# factory_tnc_arm64.addStep(steps.FileUpload(
#     name="move new files to the apt repo",
#     workersrc=util.Interpolate("/home/buildbot/workdir/turbonc-arm64_dev/python3-turbonc_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb"),
#     masterdest=util.Interpolate("/home/buildbot/debian/apt/pool/main/develop/python3-turbonc-arm_64_%(prop:tag)s-%(prop:minor_version)s.dev_arm64.deb")
#     )
# )
#
# # delete files from build directory
# # factory_tnc_arm64.addStep(steps.ShellCommand(
# #     name="delete files from build directory",
# #     command=["rm", util.Interpolate("/home/buildbot/buildbot/worker/monokrom-dev/python3-monokrom_%(prop:tag)s-%(prop:minor_version)s.dev_all.deb")],
# #     workdir="sources/"))
#
# # scan new packages in apt repository
# factory_tnc_arm64.addStep(steps.MasterShellCommand(
#     name="scan new packages in apt repository",
#     command="/home/buildbot/buildbot/master/scripts/do_apt_develop.sh"
#     )
# )
#


# factory_tnc_arm64.addStep(steps.GitHub(name="downlaod static docs",
#                                              repourl='git@github.com:kcjengr/probe_basic.git',
#                                              origin="origin",
#                                              branch="gh-pages",
#                                              mode='full',
#                                              workdir="docs/"))
#
# factory_tnc_arm64.addStep(steps.ShellCommand(name="reset gh-pages",
#                                                    command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
#                                                    workdir="docs/"))
#
# factory_tnc_arm64.addStep(steps.ShellCommand(name="delete git index",
#                                                    command=["rm", ".git/index"],
#                                                    workdir="docs/"))
#
# factory_tnc_arm64.addStep(steps.ShellCommand(name="clean gh-pages",
#                                                    command=["git", "clean", "-fdx"],
#                                                    workdir="docs/"))
#
# factory_tnc_arm64.addStep(
#     steps.Sphinx(
#         name="compile sphinx docs",
#         haltOnFailure=True,
#         sphinx="/home/buildbot/venv/bin/sphinx-build",
#         sphinx_builddir="/home/buildbot/buildbot/worker/tnc-arm-dev/docs/",
#         sphinx_sourcedir="/home/buildbot/buildbot/worker/tnc-arm-dev/sources/docs_src/source/",
#         strict_warnings=False,
#         env={"LANG": "en_EN.UTF-8"},
#         workdir="docs/"))
#
# factory_tnc_arm64.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_tnc_arm64.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_tnc_arm64.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
