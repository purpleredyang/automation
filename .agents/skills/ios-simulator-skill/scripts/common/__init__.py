"""Shared exports for ios-simulator-skill scripts."""

from .cache_utils import ProgressiveCache, get_cache
from .device_utils import (
    build_idb_command,
    build_simctl_command,
    get_booted_device_udid,
    get_device_screen_size,
    resolve_device_identifier,
    resolve_udid,
    transform_screenshot_coords,
)
from .idb_utils import count_elements, flatten_tree, get_accessibility_tree, get_screen_size
from .screenshot_utils import capture_screenshot, generate_screenshot_name, resize_screenshot

__all__ = [
    "ProgressiveCache",
    "build_idb_command",
    "build_simctl_command",
    "capture_screenshot",
    "count_elements",
    "flatten_tree",
    "generate_screenshot_name",
    "get_accessibility_tree",
    "get_booted_device_udid",
    "get_cache",
    "get_device_screen_size",
    "get_screen_size",
    "resolve_device_identifier",
    "resolve_udid",
    "resize_screenshot",
    "transform_screenshot_coords",
]
