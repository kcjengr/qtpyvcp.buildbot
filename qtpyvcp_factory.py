#
# QtPyVCP Factory
#

from buildbot.plugins import steps, util

factory_qtpyvcp = util.BuildFactory()

# fetch sources
factory_qtpyvcp.addStep(steps.GitHub(repourl='git://github.com/kcjengr/qtpyvcp.git',
                                     mode='full',
                                     submodules=True))

# install sources to virtual env
factory_qtpyvcp.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_venv/bin/python", "-m", "pip", "install", "."],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_venv"}))

# build source and wheel for distribution
factory_qtpyvcp.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_venv/bin/python", "setup.py", "bdist_wheel"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_venv"}))

# get version from installed python package
factory_qtpyvcp.addStep(steps.SetPropertyFromCommand(workdir="build",
                                                     command=["/home/kcjengr/buildbot/venvs/qtpyvcp_venv/bin/python",
                                                              "installer/scripts/check_version.py"],
                                                     property="qtpyvcp_version",
                                                     env={
                                                         "VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_venv"}))

# add version and date to installer config file
factory_qtpyvcp.addStep(steps.ShellCommand(workdir="build",
                                           command=["/home/kcjengr/buildbot/venvs/qtpyvcp_venv/bin/python",
                                                    "installer/scripts/create_config.py",
                                                    "installer/templates/config_template.xml",
                                                    "installer/config/config.xml",
                                                    "http://repository.qtpyvcp.com/main/repo/",
                                                    util.Property("qtpyvcp_version")
                                                    ],
                                           env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_venv"}))

# add version and date to installer package file
factory_qtpyvcp.addStep(steps.ShellCommand(workdir="build",
                                           command=["/home/kcjengr/buildbot/venvs/qtpyvcp_venv/bin/python",
                                                    "installer/scripts/create_package_config.py",
                                                    "installer/templates/package_template.xml",
                                                    "installer/packages/com.kcjengr.qtpyvcp/meta/package.xml",
                                                    util.Property("qtpyvcp_version")
                                                    ],
                                           env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_venv"}))

# copy files to installer directories
factory_qtpyvcp.addStep(steps.CopyDirectory(src="build/dist",
                                            dest="build/installer/packages/com.kcjengr.qtpyvcp/data"))

factory_qtpyvcp.addStep(steps.RemoveDirectory(dir="build/dist"))
# factory_qtpyvcp.addStep(steps.RemoveDirectory(dir="build/installer/repo"))

# configure the installer
factory_qtpyvcp.addStep(steps.ShellCommand(command=["qmake"], workdir="build/installer",
                                           env={"QT_SELECT": "qt5",
                                                "QTPYVCP_VERSION": util.Property("qtpyvcp_version")}))

# build the installer
factory_qtpyvcp.addStep(steps.Compile(command=["make"],
                                      workdir="build/installer",
                                      env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_qtpyvcp.addStep(steps.CopyDirectory(src="build/installer/repo",
                                            dest="/home/kcjengr/repo/main"))

# copy installer to repository
factory_qtpyvcp.addStep(steps.CopyDirectory(src="build/installer/bin",
                                            dest="/home/kcjengr/repo/main"))
