# Home Assistant Duplicate Video Finder Add-on Repository

This repository contains the Duplicate Video Finder add-on for Home Assistant. This add-on helps you identify and manage duplicate video files in your Home Assistant media libraries.

## Add-on: Duplicate Video Finder

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

_Scan your media directories for duplicate video files and easily manage them from Home Assistant._

## Installation

### Adding this repository to your Home Assistant instance

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on Store**.
2. Click the **...** menu at the top right corner -> **Repositories**
3. Add `https://github.com/tommy2hands/ha-duplicate-video-finder` to the repository input field.
4. Click **Add** -> **Close**

### Installing the add-on

1. Click on the **Duplicate Video Finder** card in the add-on store.
2. Click the **INSTALL** button.
3. Start the add-on by clicking **START**.
4. Check the logs of the add-on to see if everything went well.
5. A sidebar item called "Duplicate Videos" should appear in your Home Assistant sidebar.

## Features

- Scans your media directories for duplicate video files
- Detects duplicates by filename comparison or content hash (optional deep scan)
- Shows results in an easy-to-use interface
- Allows you to delete duplicate files directly from the UI
- Appears in your Home Assistant sidebar for easy access
- Supports custom scan paths and exclusions

## Documentation

For full documentation and usage instructions, see the [add-on documentation](./duplicate-video-finder/README.md).

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/tommy2hands/ha-duplicate-video-finder/issues).

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
