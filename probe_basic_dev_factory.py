#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util

factory_probe_basic_dev = util.BuildFactory()
# fetch sources
factory_probe_basic_dev.addStep(steps.GitHub(name="download probe_basic sources",
                                             repourl='git@github.com:kcjengr/probe_basic.git',
                                             mode='full',
                                             submodules=True,
                                             workdir="sources/"))


# install qtpyvcp to buildbot virtual env
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="install qtpyvcp from pip into buildbot venv",
    command=["/home/kcjengr/buildbot/venvs/buildbot_venv/bin/python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/buildbot_venv"},
    workdir="sources/"))

# install qtpyvcp to virtual env
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="install qtpyvcp from pip into build venv",
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
    workdir="sources/"))

# install sources to virtual env
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="install probe basic from sources into build venv",
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "-m", "pip", "install", "--upgrade", "."],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
    workdir="sources/"))

# build binaries and wheel for distribution
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="build binaries and wheel for distribution",
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "setup.py", "bdist_wheel"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
    workdir="sources/"))

# build source for distribution
factory_probe_basic_dev.addStep(steps.ShellCommand(
    name="build source for distribution",
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "setup.py", "sdist"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
    workdir="sources/"))

# get version from installed probe_basic package
factory_probe_basic_dev.addStep(
    steps.SetPropertyFromCommand(
        name="obtain probe_basic version number",
        command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python",
                 "pb-installer/scripts/check_probe_basic_version.py"],
        property="probe_basic_dev_version",
        env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
        workdir="sources/"))



# add version and date to installer package file
factory_probe_basic_dev.addStep(
    steps.ShellCommand(name="add version and date to installer package file",
                       command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python",
                                "pb-installer/scripts/create_probe_basic_package_config.py",
                                "pb-installer/templates/probe_basic_package_template.xml",
                                "pb-installer/packages/com.probebasic.core/meta/package.xml",
                                util.Property("probe_basic_dev_version")],
                       env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
                       workdir="sources/"))

# add version and date to installer config file
factory_probe_basic_dev.addStep(
    steps.ShellCommand(name="add version, date and repo to installer config file",
                       command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python",
                                "pb-installer/scripts/create_config.py",
                                "pb-installer/templates/config_template.xml",
                                "pb-installer/config/config.xml",
                                "http://repository.qtpyvcp.com/repo/pb-dev/repo",
                                util.Property("probe_basic_dev_version")],
                       env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"},
                       workdir="sources/"))

# copy files to installer directories
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="sources/dist",
                                                    dest="sources/pb-installer/packages/com.probebasic.core/data/",
                                                    ))

# sim files to installer directories
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="sources/config",
                                                    dest="sources/pb-installer/packages/com.probebasic.sim/data/probe_basic/",
                                                    workdir="sources/"))



# configure the installer
factory_probe_basic_dev.addStep(steps.ShellCommand(name="configure the installer",
                                                   command=["qmake"],
                                                   workdir="sources/pb-installer",
                                                   env={"QT_SELECT": "qt5",
                                                        "PB_VERSION": util.Property("probe_basic_dev_version")}))

# build the installer
factory_probe_basic_dev.addStep(steps.Compile(command=["make"],
                                              workdir="sources/pb-installer",
                                              env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="sources/pb-installer/repo",
                                                    dest="/home/kcjengr/repo/pb-dev"))

# copy installer to repository
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="sources/pb-installer/bin",
                                                    dest="/home/kcjengr/repo/pb-dev"))

factory_probe_basic_dev.addStep(steps.RemoveDirectory(dir="sources/pb-installer/repo"))

factory_probe_basic_dev.addStep(steps.RemoveDirectory(dir="sources/build/"))
factory_probe_basic_dev.addStep(steps.RemoveDirectory(dir="sources/dist/"))


factory_probe_basic_dev.addStep(steps.GitHub(repourl='git@github.com:kcjengr/probe_basic.github.io.git',
                                             origin="origin",
                                             branch="gh-pages",
                                             mode='full',
                                             workdir="docs/"))

factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
                                                   workdir="docs/"))
                                                   
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["rm", ".git/index"],
                                                   workdir="docs/"))
                                                   
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "clean", "-fdx"],
                                                   workdir="docs/"))

factory_probe_basic_dev.addStep(
    steps.Sphinx(
        sphinx_builddir=".",
        sphinx_sourcedir="/home/kcjengr/buildbot/worker/probe_basic-dev/sources/docs_src/source",
        workdir="docs/"))
 
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "add", "."], workdir="docs/"))
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "push", "."], workdir="docs/"))
