"""File scanner for duplicate video files."""
import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Set, Tuple

from homeassistant.core import HomeAssistant

from .const import VIDEO_EXTENSIONS

_LOGGER = logging.getLogger(__name__)


class DuplicateVideoScanner:
    """Scanner class that searches for duplicate video files."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the scanner."""
        self.hass = hass
        self._executor = ThreadPoolExecutor(max_workers=2)  # Limit workers to avoid overloading system
        
    async def scan(self) -> List[List[str]]:
        """Scan the file system for duplicate video files.
        
        Returns:
            List of lists, where each inner list contains paths to duplicate files
        """
        # Run the scan in a thread pool to avoid blocking
        return await self.hass.async_add_executor_job(self._scan_for_duplicates)
        
    def _scan_for_duplicates(self) -> List[List[str]]:
        """Perform the actual scan for duplicate video files."""
        _LOGGER.info("Starting to scan for duplicate video files")
        
        # Dictionary to store filename -> file paths mapping
        file_map: Dict[str, List[str]] = {}
        
        # Track root drives/filesystems to scan
        root_paths = self._get_root_paths()
        
        # Track total files scanned for logging
        total_files = 0
        video_files = 0
        
        # Scan each root path
        for root_path in root_paths:
            _LOGGER.info(f"Scanning {root_path}")
            
            try:
                for root, dirs, files in os.walk(root_path):
                    # Skip directories that are not accessible
                    if not os.access(root, os.R_OK):
                        _LOGGER.debug(f"Skipping inaccessible directory: {root}")
                        continue
                    
                    # Skip system directories that might cause issues
                    if any(d.startswith(('.', '$', 'System Volume Information')) for d in root.split(os.sep)):
                        continue
                        
                    for file in files:
                        total_files += 1
                        
                        # Only process video files
                        _, ext = os.path.splitext(file.lower())
                        if ext not in VIDEO_EXTENSIONS:
                            continue
                            
                        video_files += 1
                        
                        # Use the filename (without extension) as key for duplicate detection
                        filename_without_ext = os.path.splitext(file)[0]
                        full_path = os.path.join(root, file)
                        
                        if filename_without_ext in file_map:
                            file_map[filename_without_ext].append(full_path)
                        else:
                            file_map[filename_without_ext] = [full_path]
                        
                        # Log progress occasionally
                        if video_files % 1000 == 0:
                            _LOGGER.info(f"Processed {video_files} video files so far...")
                    
            except PermissionError as e:
                _LOGGER.warning(f"Permission error accessing {root}: {e}")
            except Exception as e:
                _LOGGER.error(f"Error scanning {root}: {e}")
                
        _LOGGER.info(f"Scan completed. Processed {total_files} total files, {video_files} video files")
        
        # Filter results to only include files with duplicates
        duplicates = [paths for name, paths in file_map.items() if len(paths) > 1]
        _LOGGER.info(f"Found {len(duplicates)} sets of duplicate videos")
        
        return duplicates
    
    def _get_root_paths(self) -> List[str]:
        """Get the root paths to scan.
        
        On Windows, this will be all available drives.
        On Unix-like systems, this will start from root.
        """
        if os.name == 'nt':  # Windows
            # Get all available drives
            import string
            from ctypes import windll
            
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drive = f"{letter}:\\"
                    # Only include drives that are accessible
                    if os.path.exists(drive):
                        drives.append(drive)
                bitmask >>= 1
                
            return drives
        else:  # Unix-like
            return ["/"]  # Start from root
