#
# QtPyVCP Factory
#

import pass_file

from buildbot.plugins import steps, util

factory_qtpyvcp = util.BuildFactory()

# fetch sources
factory_qtpyvcp.addStep(steps.GitHub(name="download qtpyvcp sources",
                                     repourl='git@github.com:kcjengr/qtpyvcp.git',
                                     mode='full',
                                     branch=util.Properties("ref"),
                                     submodules=True,
                                     method='clobber',
                                     workdir="sources/"))

# install qtpyvcp to virtual env
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="install qtpyvcp from sources",
    command=["python", "-m", "pip", "install", "--upgrade", "."],
    workdir="sources/"))

# build binaries and wheel for distribution
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="build binaries and wheel for distribution",
    command=["python", "setup.py", "bdist_wheel"],
    workdir="sources/"))

# build source for distribution
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="build source for distribution",
    command=["python", "setup.py", "sdist"],
    workdir="sources/"))

# publish on pypi
factory_qtpyvcp.addStep(steps.ShellCommand(
    command=["pip", "install", "--upgrade", "twine"],
    workdir="sources/"))

factory_qtpyvcp.addStep(steps.ShellCommand(
    command=["/home/buildbot/.local/bin/twine", "upload", "dist/qtpyvcp*.tar.gz"],
    workdir="sources/"))

# build debian packages
# factory_qtpyvcp_dev.addStep(steps.ShellCommand(
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


# add version and date to installer config file
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="add version and date to installer package file",
    command=["python",
             "installer/scripts/create_config.py",
             "installer/templates/config_template.xml",
             "installer/config/config.xml",
             "http://repository.qtpyvcp.com/main/repo/",
             util.Property("ref").split("/").pop()
             ],
    workdir="sources/"))

# add version and date to installer package file
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="add version and date to installer package file",
    command=["python",
             "installer/scripts/create_package_config.py",
             "installer/templates/package_template.xml",
             "installer/packages/com.kcjengr.qtpyvcp/meta/package.xml",
             util.Property("ref").split("/").pop()
             ],
    workdir="sources/", ))

# copy files to installer directories
factory_qtpyvcp.addStep(steps.CopyDirectory(
    name="copy qtpyvcp builds to the installer core package",
    src="sources/dist",
    dest="sources/installer/packages/com.kcjengr.qtpyvcp/data"))

factory_qtpyvcp.addStep(steps.RemoveDirectory(dir="sources/dist"))
factory_qtpyvcp.addStep(steps.RemoveDirectory(dir="sources/installer/repo"))

# configure the installer
factory_qtpyvcp.addStep(steps.ShellCommand(
    name="configure the installer",
    command=["qmake"],
    workdir="sources/installer",
    env={"QT_SELECT": "qt5", "QTPYVCP_VERSION": util.Property("got_revision")}))

# build the installer
factory_qtpyvcp.addStep(steps.Compile(name="compile the installer",
                                      command=["make"],
                                      workdir="sources/installer",
                                      env={"QT_SELECT": "qt5"}))

# copy packages to repository
factory_qtpyvcp.addStep(steps.CopyDirectory(name="copy the packages to repository",
                                            src="sources/installer/repo",
                                            dest="/home/buildbot/repo/main"))

# copy installer to repository
factory_qtpyvcp.addStep(steps.CopyDirectory(name="copy the installer to repository",
                                            src="sources/installer/bin",
                                            dest="/home/buildbot/repo/main"))

# publish on github
factory_qtpyvcp.addStep(steps.ShellCommand(
    command=["/home/buildbot/buildbot/worker/qtpyvcp/sources/.scripts/publish_github_release.sh",
             "kcjengr/qtpyvcp", util.Property("got_revision")],
    workdir="sources/"))

factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete copy of the local repo", dir="sources/installer/repo"))
factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete build directory", dir="sources/build/"))
factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete dist directory", dir="sources/dist/"))

factory_qtpyvcp.addStep(steps.RemoveDirectory(name="delete docs directory", dir="docs/"))

factory_qtpyvcp.addStep(
    steps.Sphinx(
        name="compile sphinx docs",
        haltOnFailure=True,
        sphinx="/home/buildbot/.local/bin/sphinx-build",
        sphinx_builddir="/home/buildbot/buildbot/worker/qtpyvcp/docs",
        sphinx_sourcedir="/home/buildbot/buildbot/worker/qtpyvcp/sources/docs/source/",
        strict_warnings=False,
        env={"LANG": "en_EN.UTF-8"},
        workdir="sources/docs/source/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="Initialize docs repository",
                                           command=["git", "init"],
                                           workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="add remote repository",
                                           command=["git", "remote", "add", "origin",
                                                    "git@github.com:kcjengr/qtpyvcp.git"],
                                           workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="switch branch",
                                           command=["git", "checkout", "-b", "gh-pages"],
                                           workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="add docs",
                                           command=["git", "add", "."],
                                           workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="commit docs",
                                           command=["git", "commit", "-m", "Deploy docs"],
                                           workdir="docs/"))

factory_qtpyvcp.addStep(steps.ShellCommand(name="push docs",
                                           command=["git", "push", "--force", "origin", "gh-pages"],
                                           workdir="docs/"))
