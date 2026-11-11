"""Feature packages loader. Owner: Antigravity.

Maps Python package names with underscores (e.g., features.core_announcement_engine)
to their corresponding feature folders (e.g., features/core-announcement-engine).
Supports both member-prefixed package names and legacy aliases for 100% compatibility.
"""
import importlib.util
import os
import sys
from importlib.abc import MetaPathFinder

_features_dir = os.path.dirname(os.path.abspath(__file__))

FEATURE_MAPPING = {
    # Feature folder mappings
    "core_announcement_engine": "core-announcement-engine",
    "publisher_auth": "publisher-auth",
    "notice_details": "notice-details",
    "student_dashboard": "student-dashboard",
    "search_notifications": "search-notifications",
}


class FeaturePackageFinder(MetaPathFinder):
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        if fullname.startswith("features."):
            parts = fullname.split(".")
            if len(parts) == 2 and parts[1] in FEATURE_MAPPING:
                disk_dir = os.path.join(_features_dir, FEATURE_MAPPING[parts[1]])
                init_file = os.path.join(disk_dir, "__init__.py")
                return importlib.util.spec_from_file_location(
                    fullname,
                    init_file,
                    submodule_search_locations=[disk_dir],
                )
        return None


if not any(isinstance(finder, type) and finder.__name__ == "FeaturePackageFinder" for finder in sys.meta_path):
    sys.meta_path.insert(0, FeaturePackageFinder)
