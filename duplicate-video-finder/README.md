# Duplicate Video Finder Add-on

Find and manage duplicate video files in your Home Assistant media libraries.

## About

This add-on helps you identify duplicate video files across your Home Assistant media directories. It provides a clean interface to scan for duplicates and manage them efficiently.

## Features

- Scan for duplicate videos by filename or content hash
- View duplicates in an easy-to-use interface
- Delete unwanted duplicate files directly from the UI
- Configure custom scan paths and exclusions
- Appears in your Home Assistant sidebar for easy access

## Installation

1. Add the repository to your Home Assistant add-on store
2. Install the "Duplicate Video Finder" add-on
3. Start the add-on
4. Open the Web UI from your sidebar

## Configuration

```yaml
scan_paths:
  - /media
  - /share
exclude_paths: []
log_level: info
```

### Option: `scan_paths`

List of directories to scan for duplicate videos.

### Option: `exclude_paths`

List of directories to exclude from scanning.

### Option: `log_level`

The `log_level` option controls the level of log output by the add-on and can
be changed to be more or less verbose, which might be useful when you are
dealing with an unknown issue. Possible values are:

- `trace`: Show every detail, like all called internal functions.
- `debug`: Shows detailed debug information.
- `info`: Normal (usually) interesting events.
- `warning`: Exceptional occurrences that are not errors.
- `error`: Runtime errors that do not require immediate action.
- `fatal`: Something went terribly wrong. Add-on becomes unusable.

Please note that each level automatically includes log messages from a
more severe level, e.g., `debug` also shows `info` messages. By default,
the `log_level` is set to `info`, which is the recommended setting unless
you are troubleshooting.
