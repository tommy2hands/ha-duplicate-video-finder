"""Constants for the Duplicate Video Finder integration."""

DOMAIN = "duplicate_video_finder"

# Event types
EVENT_SCAN_STARTED = f"{DOMAIN}_scan_started"
EVENT_SCAN_COMPLETED = f"{DOMAIN}_scan_completed"
EVENT_SCAN_ERROR = f"{DOMAIN}_scan_error"

# Service calls
SERVICE_START_SCAN = "start_scan"

# States
STATE_IDLE = "idle"
STATE_SCANNING = "scanning"

# Video file extensions
VIDEO_EXTENSIONS = [
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", 
    ".m4v", ".mpg", ".mpeg", ".3gp", ".3g2", ".asf", ".f4v", 
    ".f4p", ".f4a", ".f4b", ".vob", ".ogv", ".ogg", ".mts", 
    ".m2ts", ".ts", ".qt", ".divx", ".xvid", ".m1v", ".m2v", 
    ".mp2", ".mpe", ".mpv", ".m4p", ".rmvb", ".rm"
]
