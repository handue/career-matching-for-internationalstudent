"""Shared project paths for CLI and workers. / CLI·작업자가 공유하는 프로젝트 경로입니다."""
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]

DEFAULT_CONFIG: Path = ROOT / "config" / "ats_boards.json"
DEFAULT_QUERY_CONFIG: Path = ROOT / "config" / "ats_discovery_queries.json"
DEFAULT_PROFILE_CONFIG: Path = ROOT / "config" / "search_profile.json"
DISCOVERED_CONFIG: Path = ROOT / "data" / "results" / "ats_boards_discovered.json"
