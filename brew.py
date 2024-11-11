import os
import re
import subprocess
from typing import Mapping
from typing import Callable
from typing import Iterable
from typing import Any

import dotbot


class Brew(dotbot.Plugin):
    _directives: Mapping[str, Callable] = {}
    _defaults: Mapping[str, Any] = {}

    def __init__(self, *args, **kwargs) -> None:
        self._directives = {
            "install-brew": self._install_brew,
            "brew": self._brew,
            "cask": self._cask,
            "tap": self._tap,
            "brewfile": self._brewfile,
        }
        self._defaults = {
            "brew": {
                "stdin": False,
                "stderr": False,
                "stdout": False,
                "force_intel": False,
            },
            "cask": {
                "stdin": False,
                "stderr": False,
                "stdout": False,
                "force_intel": False,
            },
            "brewfile": {
                "stdin": True,
                "stderr": True,
                "stdout": True,
                "force_intel": False,
            },
            "install-brew": {
                "stdin": True,
                "stderr": True,
                "stdout": True,
                "force_intel": False,
            },
        }
        super().__init__(*args, **kwargs)

    def can_handle(self, directive: str) -> bool:
        return directive in list(self._directives.keys())

    def handle(self, directive: str, data: Iterable) -> bool:
        user_defaults = self._context.defaults().get(directive, {})
        local_defaults = self._defaults.get(directive, {})
        defaults = {**local_defaults, **user_defaults}
        return self._directives[directive](data, defaults)

    def _invoke_shell_command(self, cmd: str, defaults: Mapping[str, Any]) -> int:
        with open(os.devnull, "w") as devnull:
            if defaults["force_intel"]:
                cmd = "arch --x86_64 " + cmd

            return subprocess.call(
                cmd,
                shell=True,
                cwd=self._context.base_directory(),
                stdin=True if defaults["stdin"] else devnull,
                stdout=True if defaults["stdout"] else devnull,
                stderr=True if defaults["stderr"] else devnull,
            )

    def _tap(self, tap_list, defaults) -> bool:
        result: bool = True

        for tap in tap_list:
            self._log.info(f"Tapping {tap}")
            cmd: str = f"brew tap {tap}"
            cmd_result: int = self._invoke_shell_command(cmd, defaults)
            if cmd_result != 0:
                # even if one tap fails, attempt the remaining ones
                self._log.warning(f"Failed to tap [{tap}]")
                result = False
        return result

    def _brew(self, packages: list, defaults: Mapping[str, Any]) -> bool:
        result: bool = True

        for pkg in packages:
            run = self._install(
                "brew install {pkg}",
                "test -d /usr/local/Cellar/{pkg_name} "
                + "|| brew ls --versions {pkg_name}",
                pkg,
                defaults,
            )
            if not run:
                self._log.error("Some packages were not installed")
                result = False

        if result:
            self._log.info("All brew packages have been installed")

        return result

    def _cask(self, packages, defaults) -> bool:
        result: bool = True

        for pkg in packages:
            run = self._install(
                "brew install --cask {pkg}",
                "test -d /usr/local/Caskroom/{pkg_name} "
                + "|| brew ls --cask --versions {pkg_name}",
                pkg,
                defaults,
            )
            if not run:
                self._log.error("Some packages were not installed")
                result = False

        if result:
            self._log.info("All cask packages have been installed")

        return result

    def _install(self, install_format, check_installed_format, pkg, defaults):
        cwd = self._context.base_directory()

        if not pkg:
            self._log.error("Cannot process blank package name")
            return False

        # Take out tap names (before slashes), and flags (after spaces), to get
        # just the package name (the part in between)
        pkg_parse = re.search(r"^(?:.+/)?(.+?)(?: .+)?$", pkg)
        if not pkg_parse:
            # ¯\_(ツ)_/¯
            self._log.error(f"Package name {pkg} doesn't work for some reason")
            return False

        pkg_name = pkg_parse[1]

        with open(os.devnull, "w") as devnull:
            isInstalled = subprocess.call(
                check_installed_format.format(pkg_name=pkg_name),
                shell=True,
                stdin=devnull,
                stdout=devnull,
                stderr=devnull,
                cwd=cwd,
            )

            if isInstalled == 0:
                self._log.debug(f"{pkg} already installed")
                return True

            self._log.info(f"Installing {pkg}")
            result = self._invoke_shell_command(
                install_format.format(pkg=pkg), defaults
            )
            if 0 != result:
                self._log.warning("Failed to install [{pkg}]")

            return 0 == result

    def _brewfile(self, brew_files: list, defaults: Mapping[str, Any]) -> bool:
        result: bool = True

        for file in brew_files:
            self._log.info(f"Installing from file {file}")
            cmd = f"brew bundle --verbose --file={file}"

            if 0 != self._invoke_shell_command(cmd, defaults):
                self._log.warning(f"Failed to install file [{file}]")
                result = False

        return result

    def _install_brew(self, val: bool, defaults: Mapping[str, Any]) -> bool:
        if not val:
            self._log.error("Why would you even put `install-brew: false` in there?")
            return False

        link = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
        cmd = f'/bin/bash -c "$(curl -fsSL {link})"'
        return self._install(cmd, 'command -v brew', 'brew', defaults)
