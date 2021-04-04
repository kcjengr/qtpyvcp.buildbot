#
# QtPyVCP Develop Factory
#

from buildbot.plugins import steps, util

factory_qtpyvcp_dev = util.BuildFactory()

# fetch sources
factory_qtpyvcp_dev.addStep(steps.GitHub(name="download qtpyvcp sources",
                                             repourl='git@github.com:kcjengr/qtpyvcp.git',
                                             branch='master',
                                             mode='full',
                                             submodules=True,
                                             workdir="sources/"))

# install qtpyvcp to buildbot virtual env
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="install qtpyvcp from pip into buildbot venv",
    command=["/home/kcjengr/buildbot/venvs/buildbot_venv/bin/python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/buildbot_venv"},
    workdir="sources/"))

# install qtpyvcp to virtual env
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="install qtpyvcp from sources into build venv",
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python", "-m", "pip", "install", "-e", "."],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"},
    workdir="sources/"))

# build binaries and wheel for distribution
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="build binaries and wheel for distribution",
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python", "setup.py", "bdist_wheel"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"},
    workdir="sources/"))

# build source for distribution
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="build source for distribution",
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python", "setup.py", "sdist"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"},
    workdir="sources/"))


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


# get version from installed qtpyvcp package
factory_qtpyvcp_dev.addStep(
    steps.SetPropertyFromCommand(
        name="obtain qtpyvcp version number",
        command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python",
                 "installer/scripts/check_version.py"],
        property="qtpyvcp_dev_version",
        env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"},
        workdir="sources/"))

# add version and date to installer config file
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="add version and date to installer package file",
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python",
            "installer/scripts/create_config.py",
            "installer/templates/config_template.xml",
            "installer/config/config.xml",
            "http://repository.qtpyvcp.com/dev/repo/",
            util.Property("qtpyvcp_dev_version")
    ],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"},
   workdir="sources/"))

# add version and date to installer package file
factory_qtpyvcp_dev.addStep(steps.ShellCommand(
    name="add version and date to installer package file",
    command=["/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv/bin/python",
        "installer/scripts/create_package_config.py",
        "installer/templates/package_template.xml",
        "installer/packages/com.kcjengr.qtpyvcp/meta/package.xml",
        util.Property("qtpyvcp_dev_version")
    ],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/qtpyvcp_dev_venv"},
    workdir="sources/"))

# copy files to installer directories
factory_qtpyvcp_dev.addStep(steps.CopyDirectory(
    name="copy qtpyvcp builds to the installer core package",
    src="sources/dist",
    dest="sources/installer/packages/com.kcjengr.qtpyvcp/data"))

factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(dir="build/dist"))
# factory_dev.addStep(steps.RemoveDirectory(dir="build/installer/repo"))

# configure the installer
factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="configure the installer",
                                               command=["qmake"],
                                               workdir="sources/installer",
                                               env={"QT_SELECT": "qt5",
                                                    "QTPYVCP_VERSION": util.Property("qtpyvcp_dev_version")}))

# build the installer
factory_qtpyvcp_dev.addStep(steps.Compile(name="compile the installer",
                                          command=["make"],
                                          workdir="sources/installer",
                                          env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_qtpyvcp_dev.addStep(steps.CopyDirectory(name="copy the packages to repository",
                                                src="sources/installer/repo",
                                                dest="/home/kcjengr/repo/dev"))

# copy installer to repository
factory_qtpyvcp_dev.addStep(steps.CopyDirectory(name="copy the installer to repository",
                                                src="sources/installer/bin",
                                                dest="/home/kcjengr/repo/dev"))

factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(name="delete copy of the local repo", dir="sources/installer/repo"))
factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(name="delete build directory", dir="sources/build/"))
factory_qtpyvcp_dev.addStep(steps.RemoveDirectory(name="delete dist directory", dir="sources/dist/"))



factory_qtpyvcp_dev.addStep(steps.GitHub(name="downlaod static docs",
                                             repourl='git@github.com:kcjengr/qtpyvcp.git',
                                             origin="origin",
                                             branch="gh-pages",
                                             mode='full',
                                             workdir="docs/"))

factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="reset gh-pages",
                                                   command=["git", "symbolic-ref", "HEAD", "refs/heads/gh-pages"],
                                                   workdir="docs/"))
                                                   
factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="delete git index",
                                                   command=["rm", ".git/index"],
                                                   workdir="docs/"))
                                                   
factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="clean gh-pages",
                                                   command=["git", "clean", "-fdx"],
                                                   workdir="docs/"))

factory_qtpyvcp_dev.addStep(
    steps.Sphinx(
        name="compile sphinx docs",
        sphinx_builddir="/home/kcjengr/buildbot/worker/qtpyvcp-dev/docs/",
        sphinx_sourcedir="/home/kcjengr/buildbot/worker/qtpyvcp-dev/sources/docs/source/",
        workdir="docs/"))
 
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="add doc files", command=["git", "add", "."], workdir="docs/"))
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="commit doc files", command=["git", "commit", "-a", "-m", "deploy gh-pages"], workdir="docs/"))
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(name="push docs", command=["git", "push", "--force", "origin", "gh-pages"], workdir="docs/"))
