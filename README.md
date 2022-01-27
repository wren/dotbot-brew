# Dotbot-brew

<a href="https://github.com/wren/dotbot-brew/actions/workflows/macos.yml">
  <img src="https://github.com/wren/dotbot-brew/actions/workflows/macos.yml/badge.svg" alt="macOS">
</a>
<a href="https://github.com/wren/dotbot-brew/actions/workflows/ubuntu.yml">
  <img src="https://github.com/wren/dotbot-brew/actions/workflows/ubuntu.yml/badge.svg" alt="Ubuntu">
</a>

This is a plugin for [dotbot](https://github.com/anishathalye/dotbot) that adds `brew`,
`cask`, `tap`, `brewfile`, and `install-brew` directives. It allows installation of
packages using either `brew` or `brew cask`.


## Features

This plugin features an exceptionally fast check for installed packages (much faster
than `brew` itself), and can handle hundreds of packages in a second or two. This is
much faster than `brew` itself which takes [1-2 seconds *per
package*](https://github.com/Homebrew/brew/issues/7701) (through `brew list
package_name`). Please note that installing packages still takes the normal amount of
time.

This plugin can also install `brew` from scratch. It can be configured to automatically
install `brew` if missing (through the `auto_bootstrap` setting), or to install `brew`
explicitly (though the `install-brew` directive).

## Installation

Add it as submodule of your dotfiles repository (per the [dotbot plugin installation
guidelines](https://github.com/anishathalye/dotbot#plugins)).

```shell
git submodule add https://github.com/wren/dotbot-brew.git
```

Modify your `install` script, so it automatically enables `brew` plugin.

```shell
"${BASEDIR}/${DOTBOT_DIR}/${DOTBOT_BIN}" -d "${BASEDIR}" --plugin-dir dotbot-brew -c "${CONFIG}" "${@}"
```

## Usage

In your `install.conf.yaml` use `brew` directive to list all packages to be installed
using `brew`. The same works with `cask` and `brewfile`.

Also, if you plan on having multiple directives, you should consider using defaults to
set your preferred settings.

For example, your config might look something like:

```yaml
- defaults:
    - brewfile:
        - stdout: true,
    - brew:
        - auto_bootstrap: true
        - stderr: False,
        - stdout: False,

- install-brew: true

- brewfile:
    - Brewfile
    - brew/Brewfile

- tap:
    - caskroom/fonts

- brew:
    - age
    - git
    - git-lfs
    - jrnl
    - neovim --HEAD
    - yq
    - zsh

- cask:
    - signal
    - vlc
    - font-fira-code-nerd-font
```

## Special Thanks

This project owes special thanks to
[d12frosted](https://github.com/d12frosted/dotbot-brew) and
[miguelandres](https://github.com/miguelandres/dotbot-brew) for their work in their own
versions of `dotbot-brew` (which this project was originally forked from).

