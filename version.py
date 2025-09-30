#!/usr/bin/env python3
"""
UniMCPSim Version Information
"""

__version__ = "2.1.0"
__version_info__ = (2, 1, 0)

# Version history
VERSION_HISTORY = {
    "2.1.0": {
        "date": "2025-09-30",
        "features": [
            "Enhanced token permission management with modal interface",
            "App details viewer with complete action information",
            "One-click MCP configuration generator",
            "Prompt template management system",
            "Unified navigation and footer components",
            "Batch permission settings with select all functionality"
        ]
    },
    "2.0.0": {
        "date": "2025-09-29",
        "features": [
            "Core MCP simulator fully functional",
            "9 pre-configured product simulators",
            "AI-enhanced response generation",
            "Web admin interface",
            "Token-based authentication"
        ]
    }
}

def get_version():
    """Get current version string"""
    return __version__

def get_version_info():
    """Get version tuple"""
    return __version_info__

def get_version_history():
    """Get version history"""
    return VERSION_HISTORY