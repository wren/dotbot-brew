# Dotbot-brew

<a href="https://github.com/wren/dotbot-brew/actions/workflows/macos.yml">
  <img src="https://github.com/wren/dotbot-brew/actions/workflows/macos.yml/badge.svg" alt="macOS">
</a>
<a href="https://github.com/wren/dotbot-brew/actions/workflows/ubuntu.yml">
  <img src="https://github.com/wren/dotbot-brew/actions/workflows/ubuntu.yml/badge.svg" alt="Ubuntu">
</a>

Plugin for [dotbot](https://github.com/anishathalye/dotbot) that adds `brew` and `cask`
directives. It allows installation of packages using `brew` and `brew cask` on OS X. In
case `brew` is not installed, it will be automatically loaded and configured. The plugin
itself is pretty silly as it doesn\'t handle updates and fails on unsupported operating
systems.

## Installation

Just add it as submodule of your dotfiles repository.

```shell
git submodule add https://github.com/wren/dotbot-brew.git
```

Modify your `install` script, so it automatically enables `brew` plugin.

```shell
"${BASEDIR}/${DOTBOT_DIR}/${DOTBOT_BIN}" -d "${BASEDIR}" --plugin-dir dotbot-brew -c "${CONFIG}" "${@}"
```

## Usage

In your `install.conf.yaml` use `brew` directive to list all packages to be installed
using `brew`. The same works with `cask` and `brewfile`. For example:

```yaml
- brewfile:
    - Brewfile
    - brew/Brewfile

- tap:
    - caskroom/fonts

- brew:
    - git
    - git-lfs
    - emacs --with-cocoa --with-gnutls --with-librsvg --with-imagemagick --HEAD --use-git-head

- brew: [gnupg, gnupg2]

- cask: [colorpicker, vlc]
```

If you plan on having multiple instances of the directives in this
package, you should consider using defaults to disable auto~bootstrap~
(installation of brew and cask on every command), and installing first
with the installBrew: directive

```yaml
- defaults:
    - brewfile:
        - auto_bootstrap: false
    - brew:
        - auto_bootstrap: false
    - cask:
        - auto_bootstrap: false

- install-brew: true

- brewfile:
    - Brewfile
    - brew/Brewfile

- tap:
    - caskroom/fonts

- brew:
    - git
    - git-lfs
    - jrnl
    - neovim --HEAD
    - yq

- brew: [age, zsh]

- cask: [signal, vlc, font-fira-code-nerd-font]
```

Defaults also can control stdin, stdout and stderr (disabling with
false, enabling with true)
