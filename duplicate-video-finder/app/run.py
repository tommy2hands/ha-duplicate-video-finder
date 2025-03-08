#!/usr/bin/env python3

import os
import sys
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("duplicate_video_finder")

# Initialize FastAPI app
app = FastAPI(title="Duplicate Video Finder")

# Create the required directories if they don't exist
static_dir = os.path.join(os.getcwd(), "static")
templates_dir = os.path.join(os.getcwd(), "templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)

# Video file extensions to look for
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".m4v", ".mpeg", ".mpg", ".3gp", ".ts", ".mts", ".m2ts"
}

# Load configuration from Home Assistant options
config_path = "/data/options.json"
config = {}

try:
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    logger.info(f"Loaded configuration from {config_path}")
except FileNotFoundError:
    logger.warning(f"Config file not found at {config_path}, using defaults")
    config = {
        "scan_paths": ["/media", "/share"],
        "exclude_paths": [],
        "log_level": "info"
    }
except json.JSONDecodeError as e:
    logger.error(f"Error parsing config file: {e}")
    config = {
        "scan_paths": ["/media", "/share"],
        "exclude_paths": [],
        "log_level": "info"
    }

# Set log level from config
log_level = getattr(logging, config.get("log_level", "info").upper())
logger.setLevel(log_level)

# Store the scan results
scan_results = {}
scan_status = {
    "status": "idle",
    "last_scan": None,
    "total_files": 0,
    "processed_files": 0,
    "duplicate_sets": 0,
}


class ScanRequest(BaseModel):
    paths: Optional[List[str]] = None
    exclude_paths: Optional[List[str]] = None
    scan_by_content: bool = False


class DeleteRequest(BaseModel):
    file_path: str


def get_video_files(scan_paths: List[str], exclude_paths: List[str]) -> Dict[str, List[str]]:
    """Scan file system for video files and group by filename."""
    video_files = {}
    total_files = 0
    processed_files = 0

    # Update scan status
    scan_status["status"] = "scanning"
    scan_status["total_files"] = 0
    scan_status["processed_files"] = 0
    scan_status["duplicate_sets"] = 0

    # First pass to count total files (for progress reporting)
    logger.info("Counting files for scan...")
    for base_path in scan_paths:
        try:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.warning(f"Path does not exist: {base_path}")
                continue

            for path in base_path.rglob("*"):
                if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
                    # Check if this file should be excluded
                    if any(str(path).startswith(exclude) for exclude in exclude_paths):
                        continue
                    total_files += 1
        except Exception as e:
            logger.error(f"Error counting files in {base_path}: {e}")

    scan_status["total_files"] = total_files
    logger.info(f"Found {total_files} video files to process")

    # Second pass to process files
    for base_path in scan_paths:
        try:
            base_path = Path(base_path)
            if not base_path.exists():
                continue

            for path in base_path.rglob("*"):
                if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
                    # Check if this file should be excluded
                    if any(str(path).startswith(exclude) for exclude in exclude_paths):
                        continue

                    filename = path.name
                    file_path = str(path)

                    if filename not in video_files:
                        video_files[filename] = []
                    video_files[filename].append(file_path)

                    # Update progress
                    processed_files += 1
                    scan_status["processed_files"] = processed_files

                    # Log progress every 100 files
                    if processed_files % 100 == 0:
                        logger.info(f"Processed {processed_files}/{total_files} files")

        except Exception as e:
            logger.error(f"Error scanning {base_path}: {e}")

    # Filter out non-duplicates
    duplicate_files = {k: v for k, v in video_files.items() if len(v) > 1}
    scan_status["duplicate_sets"] = len(duplicate_files)

    return duplicate_files


def calculate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash of a file for content-based duplicate detection."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return "error"


def get_duplicate_videos_by_content(files_by_name: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Group duplicate videos by content hash."""
    content_duplicates = {}
    files_processed = 0
    total_files = sum(len(files) for files in files_by_name.values())

    for filename, file_paths in files_by_name.items():
        file_hashes = {}

        for file_path in file_paths:
            file_hash = calculate_file_hash(file_path)
            files_processed += 1

            if file_hash not in file_hashes:
                file_hashes[file_hash] = []
            file_hashes[file_hash].append(file_path)

            # Log progress for large sets
            if files_processed % 10 == 0:
                logger.info(f"Hashed {files_processed}/{total_files} files")

        # Keep only duplicates (more than one file with the same hash)
        for file_hash, paths in file_hashes.items():
            if len(paths) > 1:
                content_duplicates[f"{filename}_{file_hash[:8]}"] = paths

    return content_duplicates


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main index page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scan_status": scan_status}
    )


@app.get("/api/status")
async def get_status():
    """Get the current scan status."""
    return JSONResponse(scan_status)


@app.get("/api/results")
async def get_results():
    """Get the scan results."""
    return JSONResponse({
        "duplicates": [
            {"name": name, "count": len(paths), "paths": paths}
            for name, paths in scan_results.items()
        ]
    })


@app.post("/api/scan")
async def start_scan(request: ScanRequest):
    """Start a scan for duplicate videos."""
    global scan_results

    # If already scanning, return error
    if scan_status["status"] == "scanning":
        raise HTTPException(status_code=400, detail="A scan is already in progress")

    # Use provided paths or default from config
    scan_paths = request.paths if request.paths else config["scan_paths"]
    exclude_paths = request.exclude_paths if request.exclude_paths else config["exclude_paths"]

    logger.info(f"Starting scan with paths: {scan_paths}, excluding: {exclude_paths}")

    # Run the scan in the background
    scan_status["status"] = "scanning"
    scan_status["last_scan"] = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Get files grouped by name first
        files_by_name = get_video_files(scan_paths, exclude_paths)

        # If content-based scan requested, further process by hash
        if request.scan_by_content:
            logger.info("Performing content-based duplicate detection")
            scan_results = get_duplicate_videos_by_content(files_by_name)
        else:
            scan_results = files_by_name

        logger.info(f"Scan completed. Found {len(scan_results)} duplicate sets")
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        scan_status["status"] = "error"
        return JSONResponse({"status": "error", "message": str(e)})

    scan_status["status"] = "idle"
    return JSONResponse({"status": "success", "duplicate_sets": len(scan_results)})


@app.post("/api/delete")
async def delete_file(request: DeleteRequest):
    """Delete a file from the file system."""
    file_path = request.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")
        return JSONResponse({"status": "success", "message": f"File deleted: {file_path}"})
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point for the addon."""
    try:
        # Start the Uvicorn server
        logger.info("Starting Duplicate Video Finder")
        uvicorn.run("run:app", host="0.0.0.0", port=7000, log_level="info")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
