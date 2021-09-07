"""Version utils."""


from functools import lru_cache

from awesomeversion import AwesomeVersionException, AwesomeVersion


@lru_cache(maxsize=1024)
def version_left_higher_then_right(left: str, right: str) -> bool:
    """Return a bool if source is newer than target, will also be true if identical."""
    try:
        return AwesomeVersion(left) >= AwesomeVersion(right)
    except AwesomeVersionException:
        return False
