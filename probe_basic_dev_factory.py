#
# ProbeBasic Develop Factory
#

import pass_file
from buildbot.plugins import steps, util

factory_probe_basic_dev = util.BuildFactory()
# fetch sources
factory_probe_basic_dev.addStep(steps.GitHub(repourl='git://github.com/kcjengr/probe_basic.git',
                                             mode='full',
                                             submodules=True))

# install qtpyvcp to virtual env
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# install sources to virtual env
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "-m", "pip", "install", "--upgrade", "."],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# build source and wheel for distribution
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "setup.py", "bdist_wheel"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# build source and wheel for distribution
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python", "setup.py", "sdist"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# publish on github
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/worker/probe_basic-dev/build/.scripts/publish_github_release.sh",
             "",
             "kcjengr/probe_basic",
             pass_file.github_kcjengr_token],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# publish on pypi
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/worker/probe_basic-dev/build/.scripts/publish_pypi_release.sh",
             pass_file.pypi_probe_basic_token],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# get version from installed probe_basic package
factory_probe_basic_dev.addStep(
    steps.SetPropertyFromCommand(
        workdir="build",
        command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python",
                 "pb-installer/scripts/check_probe_basic_version.py"],
        property="probe_basic_dev_version",
        env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# add version and date to installer package file
factory_probe_basic_dev.addStep(
    steps.ShellCommand(workdir="build",
                       command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python",
                                "pb-installer/scripts/create_probe_basic_package_config.py",
                                "pb-installer/templates/probe_basic_package_template.xml",
                                "pb-installer/packages/com.probebasic.core/meta/package.xml",
                                util.Property("probe_basic_dev_version")],
                       env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# add version and date to installer config file
factory_probe_basic_dev.addStep(
    steps.ShellCommand(workdir="build",
                       command=["/home/kcjengr/buildbot/venvs/probe_basic_dev_venv/bin/python",
                                "pb-installer/scripts/create_config.py",
                                "pb-installer/templates/config_template.xml",
                                "pb-installer/config/config.xml",
                                "http://repository.qtpyvcp.com/repo/pb-dev/repo",
                                util.Property("probe_basic_dev_version")],
                       env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_dev_venv"}))

# copy files to installer directories
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="build/dist/",
                                                    dest="build/pb-installer/packages/com.probebasic.core/data/"))

# sim files to installer directories
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="config/",
                                                    dest="build/pb-installer/packages/com.probebasic.sim/data/probe_basic/config/"))

factory_probe_basic_dev.addStep(steps.RemoveDirectory(dir="build/dist/"))

factory_probe_basic_dev.addStep(steps.RemoveDirectory(dir="build/pb-installer/repo"))

# configure the installer
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["qmake"],
                                                   workdir="build/pb-installer",
                                                   env={"QT_SELECT": "qt5",
                                                        "PB_VERSION": util.Property("probe_basic_dev_version")}))

# build the installer
factory_probe_basic_dev.addStep(steps.Compile(command=["make"],
                                              workdir="build/pb-installer",
                                              env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="build/pb-installer/repo", dest="/home/kcjengr/repo/pb-dev"))

# copy installer to repository
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="build/pb-installer/bin", dest="/home/kcjengr/repo/pb-dev"))

