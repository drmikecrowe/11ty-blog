---
title: Introducing VPEM-Visual Studio Profile Extension Manager
description: |
   VPEM is designed to help you manage your VSCode extensions across different profiles. It provides dumping, categorizing, and applying to individual profiles
date: 2024-10-05T10:11:00.050Z
preview: /images/2024/10/VPEM-apply.gif
draft: true
tags:
   - tech
   - vscode
categories:
   - personal
seo:
   title: null
   description: null
   image: /images/2024/10/VPEM-apply.gif
images:
   feature: 2024/10/Extension-Images.png
   thumb: null
   slide: null
---

![vscode-extensions](2024/10/Extension-Images.png)

# VS Code Profile Extension Manager (VPEM)

VS Code Profile Extension Manager (VPEM) is a powerful command-line tool designed to help you manage your Visual Studio Code extensions across different profiles. It allows you to dump, categorize, and apply extensions with ease, streamlining your VS Code setup process.

## Status

This project has been developed strictly on Linux, though it should work everywhere.  If you find an issue, please report it in the [GitHub issue tracker](https://github.com/drmikecrowe/vscode-profile-extension-manager/issues).

Executables are built using [pyinstaller](https://github.com/pyinstaller/pyinstaller) and are available for Linux, Windows and MacOS.  Again, if any issues are found, please report them in the [GitHub issue tracker](https://github.com/drmikecrowe/vscode-profile-extension-manager/issues).

## Why?

I tend to use a lot of extensions.  Further, I find my self swithing frequently between TypeScript, Python and now C#.  Sometimes I work in Azure.  Othertimes in AWS.

I realized that multiple profiles might make more sense than tons of extensions in a single profile.  However, it's also really easy to experiment with extensions and leave unused ones polluting the profile.  This tool helps me keep things organized.

For example, here's how to apply a group of extensions to a profile:

![Apply Extensions](https://github.com/drmikecrowe/vscode-profile-extension-manager/blob/main/assets/VPEM-apply-example.png)

## Process

- First, dump your extensions for all your profiles

![Dump Extensions](https://github.com/drmikecrowe/vscode-profile-extension-manager/blob/main/assets/VPEM-dump.gif)

- Next, categorizing extensions by searching for common strings and assign to categories

![Categorize Extensions](https://github.com/drmikecrowe/vscode-profile-extension-manager/blob/main/assets/VPEM-categorize.gif)

- Finally, apply extensions to a profile

![Apply Extensions](https://github.com/drmikecrowe/vscode-profile-extension-manager/blob/main/assets/VPEM-apply.gif)

## Installation

To install VPEM, you can use pip:

**Recommended way:**

```sh
pipx install pipx install vscode_profile_extension_manager
```

Alternatively, you may download the released binaries in the repo.  However, these are mass-produced by actions I've pulled from various places, so I can't guarantee they're tested.

Finally, you can also use [jpillora/installer](https://github.com/jpillora/installer) to automate the installation:

```sh
curl -q https://i.jpillora.com/drmikecrowe/vscode-profile-extension-manager! | sh
```

## Usage

Here are some basic usage examples:

- Dump extensions from a profile:

```sh
   vpem dump --profile "Default"
```

- Apply extensions to a profile:

```sh
   vpem apply --profile "Work" --category "Python Development"
```

- List all categories:

```sh
   vpem list-categories
```

## Contributing

We welcome contributions to VPEM! If you'd like to contribute, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with a clear message
4. Push your changes to your fork
5. Create a pull request

Please make sure to update tests as appropriate and adhere to the project's coding standards.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE.md) file for details.

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub issue tracker](https://github.com/drmikecrowe/vscode-profile-extension-manager/issues).
