#
# QtPyVCP Develop Factory
#

from buildbot.plugins import steps, util

factory_qtpyvcp_dev = util.BuildFactory()
# fetch sources
factory_qtpyvcp_dev.addStep(steps.GitHub(repourl='git://github.com/kcjengr/qtpyvcp.git',
                                         mode='full',
                                         submodules=True))

# install sources to virtual env
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python", "-m", "pip", "install", "--upgrade", "."],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

# build source, package, and wheel for distribution
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python", "setup.py", "bdist_wheel"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python", "setup.py", "sdist"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

# build debian packages
#factory_qtpyvcp_dev.addStep(steps.ShellCommand(
#    command=["fpm", "-t", "deb", "-p", "debs", "-s", "python", "-f", "--license", 'GPLv2',
#            "--vendor", "KCJ Engineering",
#             "--maintainer", "Kurt Jacobson <kcjengr@gmail.com>", "--url",
#            "https://qtpyvcp.kcjengr.com" ,"--description",
#            "QtPyVCP - Qt and Python based Virtual Control Panel framework for LinuxCNC.",
#            "-d", "python-pip",
#            "-d", "python-pyqt5",
#            "-d", "python-dbus.mainloop.pyqt5",
#            "-d", "python-pyqt5.qtopengl",
#            "-d", "python-pyqt5.qsci",
#            "-d", "python-pyqt5.qtmultimedia",
#            "-d", "gstreamer1.0-plugins-bad",
#            "-d", "libqt5multimedia5-plugins",
#            "-d", "pyqt5-dev-tools",
#            "-d", "qttools5-dev-tools",
#            "--after-install", ".travis/after_install.sh",
#            "--after-remove", ".travis/after_remove.sh",
#            "--no-auto-depends",
#            "--verbose", "setup.py"],))

# publish on github
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/worker/qtpyvcp-dev/build/.travis/publish_github_release.sh",
             "kcjengr/qtpyvcp",
             "",
             pass_file.github_qtpyvcp_token],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

# publish on pypi
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/worker/qtpyvcp-dev/build/.travis/publish_pypi_release.sh",
             pass_file.pypi_qtpyvcp_token],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))


# get version from installed python package
factory_qtpyvcp_dev.addStep(steps.SetPropertyFromCommand(workdir="build",
                                                         command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python",
                                                                  "installer/scripts/check_version.py"],
                                                         property="qtpyvcp_dev_version",
                                                         env={
                                                             "VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

# add version and date to installer config file
factory_qtpyvcp_dev.addStep(steps.ShellCommand(workdir="build",
                                               command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python",
                                                        "installer/scripts/create_config.py",
                                                        "installer/templates/config_template.xml",
                                                        "installer/config/config.xml",
                                                        "http://repository.qtpyvcp.com/dev/repo/",
                                                        util.Property("qtpyvcp_dev_version")
                                                        ],
                                               env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

# add version and date to installer package file
factory_qtpyvcp_dev.addStep(steps.ShellCommand(workdir="build",
                                               command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python",
                                                        "installer/scripts/create_package_config.py",
                                                        "installer/templates/package_template.xml",
                                                        "installer/packages/com.kcjengr.qtpyvcp/meta/package.xml",
                                                        util.Property("qtpyvcp_dev_version")
                                                        ],
                                               env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"}))

# copy files to installer directories
factory_qtpyvcp_dev.addStep(steps.CopyDirectory(src="build/dist",
                                                dest="build/installer/packages/com.kcjengr.qtpyvcp/data"))

factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(dir="build/dist"))
# factory_dev.addStep(steps.RemoveDirectory(dir="build/installer/repo"))

# configure the installer
factory_qtpyvcp_dev.addStep(steps.ShellCommand(command=["qmake"],
                                               workdir="build/installer",
                                               env={"QT_SELECT": "qt5",
                                                    "QTPYVCP_VERSION": util.Property("qtpyvcp_dev_version")}))

# build the installer
factory_qtpyvcp_dev.addStep(steps.Compile(command=["make"],
                                          workdir="build/installer",
                                          env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_qtpyvcp_dev.addStep(steps.CopyDirectory(src="build/installer/repo",
                                                dest="/home/kcjengr/repo/dev"))

# copy installer to repository
factory_qtpyvcp_dev.addStep(steps.CopyDirectory(src="build/installer/bin",
                                                dest="/home/kcjengr/repo/dev"))
