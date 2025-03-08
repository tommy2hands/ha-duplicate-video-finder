# Home Assistant Duplicate Video Finder

A Home Assistant integration that scans your file system for duplicate video files.

## Features

- Scans your entire file system for duplicate video files
- Identifies duplicates based on filename
- Shows results in a simple list format
- Compatible with Home Assistant via HACS

## Installation

1. Install HACS if you don't have it already
2. Add this repository as a custom repository in HACS
3. Install the integration through HACS
4. Restart Home Assistant
5. Add the integration through the Home Assistant UI

## Usage

After installation, you can start a scan from the integration page. Results will be displayed as a list of duplicate video files found on your system.

## Planned Features

- Content hash-based duplication detection
- Ability to delete duplicates directly from the UI
- Scheduled scans
- Exclude specific directories from scanning
