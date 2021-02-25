#
# ProbeBasic Develop Factory
#

from buildbot.plugins import steps, util

factory_probe_basic_dev = util.BuildFactory()
# fetch sources
factory_probe_basic_dev.addStep(steps.GitHub(repourl='git@github.com:kcjengr/probe_basic.git',
                                             mode='full',
                                             submodules=True))

# install qtpyvcp to buildbot virtual env
factory_probe_basic_dev.addStep(steps.ShellCommand(
    command=["/home/kcjengr/buildbot/venvs/buildbot_venv/bin/python", "-m", "pip", "install", "--upgrade", "qtpyvcp"],
    env={"VIRTUAL_ENV": "/home/kcjengr/buildbot/venvs/buildbot_venv"}))

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
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="build/dist",
                                                    dest="build/pb-installer/packages/com.probebasic.core/data/"))

# sim files to installer directories
factory_probe_basic_dev.addStep(steps.CopyDirectory(src="build/config",
                                                    dest="build/pb-installer/packages/com.probebasic.sim/data/probe_basic/"))


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


factory_probe_basic_dev.addStep(steps.RemoveDirectory(dir="build/build/"))


# push gh-pages
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "reset", "--hard",
                                                            "HEAD"]))

# build sphinx docs
factory_probe_basic_dev.addStep(
    steps.Sphinx(
        sphinx_builddir="docs",
        sphinx_sourcedir="docs_src/source",
        )
    )

# push gh-pages
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "checkout",
                                                            "gh-pages"]))
# gh-pages pop stash changes
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "add", "docs"]))
# gh-pages pop stash changes
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "commit", "-m", "'deploy gh-pages'"]))

# push gh-pages
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "push",
                                                            "origin",
                                                            "gh-pages"]))

# push gh-pages
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "checkout",
                                                            "master"]))


# push gh-pages
factory_probe_basic_dev.addStep(steps.ShellCommand(command=["git", "reset", "--hard",
                                                            "HEAD"]))
                             