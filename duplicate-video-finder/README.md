# Duplicate Video Finder

_Scan your media directories for duplicate video files and easily manage them from Home Assistant._

## About

This add-on helps you identify and manage duplicate video files in your Home Assistant media libraries. It scans directories for duplicate videos and provides an easy-to-use interface to review and clean up duplicates.

## Features

- Scans your media directories for duplicate video files
- Detects duplicates by filename comparison or content hash (optional deep scan)
- Shows results in an easy-to-use interface
- Allows you to delete duplicate files directly from the UI
- Appears in your Home Assistant sidebar for easy access
- Supports custom scan paths and exclusions

## Configuration

```yaml
# Example configuration.yaml entry
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

The log level for the add-on. Choose from: `trace`, `debug`, `info`, `notice`, `warning`, `error`, `fatal`.

## How to use

1. Start the add-on
2. Open the web UI by clicking on the "Duplicate Videos" item in your sidebar
3. Configure the scan options if needed
4. Click "Start Scan" to begin scanning for duplicates
5. Review the results and manage duplicate files as needed
