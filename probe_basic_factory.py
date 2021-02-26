#
# ProbeBasic Factory
#

import pass_file
from buildbot.plugins import steps, util

factory_probe_basic = util.BuildFactory()
# fetch sources
factory_probe_basic.addStep(steps.GitHub(repourl='git://github.com/kcjengr/probe_basic.git',
                                         mode='full',
                                         submodules=True))

# install qtpyvcp to virtual env
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# install sources to virtual env
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python", "-m", "pip", "install", "--upgrade", "."],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# build source and wheel for distribution
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python", "setup.py", "bdist_wheel"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# build source and wheel for distribution
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python", "setup.py", "sdist"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))


# get version from installed probe_basic package
factory_probe_basic.addStep(
    steps.SetPropertyFromCommand(
        workdir="build",
        command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python",
                 "pb-installer/scripts/check_probe_basic_version.py"],
        property="probe_basic_version",
        env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# add version and date to installer package file
factory_probe_basic.addStep(
    steps.ShellCommand(workdir="build",
                       command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python",
                                "pb-installer/scripts/create_probe_basic_package_config.py",
                                "pb-installer/templates/probe_basic_package_template.xml",
                                "pb-installer/packages/com.probebasic.core/meta/package.xml",
                                util.Property("probe_basic_version")],
                       env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# add version and date to installer config file
factory_probe_basic.addStep(
    steps.ShellCommand(workdir="build",
                       command=["/home/kcjengr/buildbot/venvs/probe_basic_venv/bin/python",
                                "pb-installer/scripts/create_config.py",
                                "pb-installer/templates/config_template.xml",
                                "pb-installer/config/config.xml",
                                "http://repository.qtpyvcp.com/repo/pb/repo",
                                util.Property("probe_basic_version")],
                       env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# copy files to installer directories
factory_probe_basic.addStep(steps.CopyDirectory(src="build/dist",
                                                    dest="build/pb-installer/packages/com.probebasic.core/data"))

# configure the installer
factory_probe_basic.addStep(steps.ShellCommand(command=["qmake"],
                                                   workdir="build/pb-installer",
                                                   env={"QT_SELECT": "qt5",
                                                        "PB_VERSION": util.Property("probe_basic_version")}))

# build the installer
factory_probe_basic.addStep(steps.Compile(command=["make"],
                                          workdir="build/pb-installer",
                                          env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_probe_basic.addStep(steps.CopyDirectory(src="build/pb-installer/repo", dest="/home/kcjengr/repo/pb"))

# copy installer to repository
factory_probe_basic.addStep(steps.CopyDirectory(src="build/pb-installer/bin", dest="/home/kcjengr/repo/pb"))


# publish on github
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/worker/probe_basic/build/.scripts/publish_github_release.sh",
             "kcjengr/probe_basic",
             util.Property("probe_basic_version"),
             pass_file.github_kcjengr_token],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))

# publish on pypi
factory_probe_basic.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/worker/probe_basic/build/.scripts/publish_pypi_release.sh"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/probe_basic_venv"}))



factory_probe_basic.addStep(steps.RemoveDirectory(dir="build/dist"))
factory_probe_basic.addStep(steps.RemoveDirectory(dir="build/pb-installer/repo"))
