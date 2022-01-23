import os
import re
import subprocess
from typing import Mapping
from typing import Callable
from typing import Iterable
from typing import Any

import dotbot


class Brew(dotbot.Plugin):
    _directives: Mapping[str, Callable]
    _defaults: Mapping[str, Any]

    _autoBootstrapOption: str = "auto_bootstrap"
    _forceIntelOption: str = "force_intel"

    def __init__(self, context) -> None:
        self._directives = {
            "install-brew": self._installBrew,
            "brew": self._brew,
            "cask": self._cask,
            "tap": self._tap,
            "brewfile": self._brewfile,
        }
        self._defaults = {
            'brew': {
                'auto_bootstrap': False,
                'stdin': False,
                'stderr': False,
                'stdout': False,
            },

            'cask': {
                'auto_bootstrap': False,
                'stdin': False,
                'stderr': False,
                'stdout': False,
            },

            'brewfile': {
                'auto_bootstrap': False,
                'stdin': False,
                'stderr': False,
                'stdout': False,
            },
        }
        super().__init__(context)

    def can_handle(self, directive: str) -> bool:
        return directive in list(self._directives.keys())

    def handle(self, directive: str, data: Iterable) -> bool:
        defaults = self._context.defaults().get(directive, {})
        my_defaults = defaults | self._defaults[directive]
        return self._directives[directive](data, my_defaults)

    def _invokeShellCommand(self, cmd, defaults):
        with open(os.devnull, "w") as devnull:
            stdin = stdout = stderr = devnull
            if defaults.get("stdin", False) == True:
                stdin = None
            if defaults.get("stdout", False) == True:
                stdout = None
            if defaults.get("stderr", False) == True:
                stderr = None
            if defaults.get(self._forceIntelOption, False) == True:
                cmd = "arch --x86_64 " + cmd
            return subprocess.call(
                cmd,
                shell=True,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                cwd=self._context.base_directory(),
            )

    def _tap(self, tap_list, defaults):
        if defaults.get(self._autoBootstrapOption, False) == True:
            self._bootstrap_brew()
        log = self._log
        for tap in tap_list:
            log.info("Tapping %s" % tap)
            cmd = "brew tap %s" % (tap)
            result = self._invokeShellCommand(cmd, defaults)
            if result != 0:
                log.warning("Failed to tap [%s]" % tap)
                return False
        return True

    def _brew(self, packages, defaults):
        if defaults.get(self._autoBootstrapOption, True) == True:
            self._bootstrap_brew()
        return self._processPackages(
            "brew install %s", "test -d /usr/local/Cellar/%s || brew ls --versions %s", packages, defaults
        )

    def _cask(self, packages, defaults):
        if defaults.get(self._autoBootstrapOption, True) == True:
            self._bootstrap_brew()
            self._bootstrap_cask()
        return self._processPackages(
            "brew install --cask %s", "test -d /usr/local/Caskroom/%s || brew ls --cask --versions %s", packages, defaults
        )

    def _processPackages(
        self, install_format, check_installed_format, packages, defaults
    ) -> bool:
        for pkg in packages:
            if (
                self._install(install_format, check_installed_format, pkg, defaults)
                == False
            ):
                self._log.error("Some packages were not installed")
                return False
        self._log.info("All packages have been installed")
        return True

    def _install(self, install_format, check_installed_format, pkg, defaults):
        cwd = self._context.base_directory()

        if not pkg:
            self._log.error('Cannot process blank package name')
            return False

        # Take out tap names (before slashes), and flags (after spaces)
        pkg_name = re.search(r'^(?:.+/)?(.+?)(?: .+)?$', pkg)[1]

        with open(os.devnull, "w") as devnull:
            isInstalled = subprocess.call(
                check_installed_format % (pkg_name, pkg_name),
                shell=True,
                stdin=devnull,
                stdout=devnull,
                stderr=devnull,
                cwd=cwd,
            )

            if isInstalled == 0:
                self._log.debug("%s already installed" % pkg)
                return True

            self._log.info("Installing %s" % pkg)
            result = self._invokeShellCommand(install_format % (pkg), defaults)
            if 0 != result:
                self._log.warning("Failed to install [%s]" % pkg)

            return 0 == result

    def _brewfile(self, brew_files, defaults):
        log = self._log
        # this directive has opposite defaults re stdin/stderr/stdout
        defaults["stdin"] = defaults.get("stdin", True)
        defaults["stderr"] = defaults.get("stderr", True)
        defaults["stdout"] = defaults.get("stdout", True)
        if defaults.get(self._autoBootstrapOption, True) == True:
            self._bootstrap_brew()
            self._bootstrap_cask()
        for f in brew_files:
            log.info("Installing from file %s" % f)
            cmd = "brew bundle --verbose --file=%s" % f
            result = self._invokeShellCommand(cmd, defaults)

            if result != 0:
                log.warning("Failed to install file [%s]" % f)
                return False
        return True

    def _installBrew(self, components):
        log = self._log
        for component in components:
            if component == "brew":
                self._bootstrap_brew()
            elif component == "cask":
                self._bootstrap_cask()
            else:
                log.error("Unknown component to install [%s]" % component)
                return False
        return True

    def _bootstrap_brew(self):
        self._log.info("Installing brew")
        link = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
        cmd = """[[ $(command -v brew) != "" ]] || /bin/bash -c "$(curl -fsSL {0})" """.format(
            link
        )
        return subprocess.call(cmd, shell=True, cwd=self._context.base_directory()) == 0

    def _bootstrap_cask(self):
        self._log.info("Installing cask")
        cmd = "brew tap homebrew/cask"
        return subprocess.call(cmd, shell=True, cwd=self._context.base_directory()) == 0
