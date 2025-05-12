"""
Version information for the application.
This file is used throughout the application to maintain consistent version info.
"""

__version__ = "1.0.1"
__release_date__ = "2025-05-11"

# Version tuple for programmatic comparison
VERSION = (1, 0, 1)

# Dictionary form for API responses
VERSION_INFO = {
    "version": __version__,
    "release_date": __release_date__,
    "major": VERSION[0],
    "minor": VERSION[1],
    "patch": VERSION[2],
}
