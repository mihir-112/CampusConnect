"""Feature packages loader. Owner: Antigravity.

Maps Python package names with underscores (e.g., features.mihir_core_announcement_engine)
to their corresponding feature folders (e.g., features/mihir-core-announcement-engine).
Supports both member-prefixed package names and legacy aliases for 100% compatibility.
"""
import importlib.util
import os
import sys
from importlib.abc import MetaPathFinder

_features_dir = os.path.dirname(os.path.abspath(__file__))

FEATURE_MAPPING = {
    # Member-prefixed package names
    "mihir_core_announcement_engine": "mihir-core-announcement-engine",
    "aariz_publisher_auth": "aariz-publisher-auth",
    "nayeem_notice_details": "nayeem-notice-details",
    "moksh_student_dashboard": "moksh-student-dashboard",
    "mridul_search_notifications": "mridul-search-notifications",
    # Legacy aliases (backward compatibility)
    "core_announcement_engine": "mihir-core-announcement-engine",
    "publisher_auth": "aariz-publisher-auth",
    "notice_details": "nayeem-notice-details",
    "student_dashboard": "moksh-student-dashboard",
    "search_notifications": "mridul-search-notifications",
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
