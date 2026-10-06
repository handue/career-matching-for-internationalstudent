"""Types and validation for saved job analyses. / 저장된 공고 분석의 타입과 검증입니다."""

from typing import Literal, TypedDict, cast


Status = Literal["yes", "no", "unknown"]


class SourceMetadata(TypedDict):
    source_url: str
    board: str
    job_id: int
    fetched_at_utc: str


class AnalysisResult(TypedDict):
    title: str
    company: str
    location: str
    skills: list[str]
    experience_requirement: str
    cpt_status: Status
    cpt_evidence: str
    opt_status: Status
    opt_evidence: str
    stem_opt_status: Status
    stem_opt_evidence: str
    visa_sponsorship_status: Status
    visa_sponsorship_evidence: str
    h1b_status: Status
    h1b_evidence: str
    green_card_status: Status
    green_card_evidence: str


class SavedJobAnalysis(TypedDict):
    source: SourceMetadata
    model: str
    analyzed_at_utc: str
    analysis: AnalysisResult


def require_object(value: object, label: str) -> dict[str, object]:
    """Require an object with string keys. / 문자열 키를 가진 객체인지 확인합니다."""
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be a JSON object with string keys")
    return cast(dict[str, object], value)


def require_string(value: object, label: str) -> str:
    """Require a string value. / 문자열 값인지 확인합니다."""
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    return value


def require_status(value: object, label: str) -> Status:
    """Require a known classification status. / 정해진 분류 상태인지 확인합니다."""
    if value == "yes":
        return "yes"
    if value == "no":
        return "no"
    if value == "unknown":
        return "unknown"
    raise ValueError(f"{label} must be yes, no, or unknown")


def parse_source_metadata(value: object) -> SourceMetadata:
    """Validate fetched-posting metadata. / 수집한 공고의 출처 정보를 검증합니다."""
    data = require_object(value, "Source metadata")
    job_id = data.get("job_id")
    if isinstance(job_id, bool) or not isinstance(job_id, int) or job_id <= 0:
        raise ValueError("source.job_id must be a positive integer")
    return {
        "source_url": require_string(data.get("source_url"), "source.source_url"),
        "board": require_string(data.get("board"), "source.board"),
        "job_id": job_id,
        "fetched_at_utc": require_string(data.get("fetched_at_utc"), "source.fetched_at_utc"),
    }


def parse_analysis_result(value: object) -> AnalysisResult:
    """Validate the analyzer's JSON object. / 분석기의 JSON 결과를 검증합니다."""
    data = require_object(value, "Analysis")
    skills = data.get("skills")
    if not isinstance(skills, list):
        raise ValueError("analysis.skills must be a list of strings")
    checked_skills: list[str] = []
    for skill in skills:
        if not isinstance(skill, str):
            raise ValueError("analysis.skills must be a list of strings")
        checked_skills.append(skill)
    return {
        "title": require_string(data.get("title"), "analysis.title"),
        "company": require_string(data.get("company"), "analysis.company"),
        "location": require_string(data.get("location"), "analysis.location"),
        "skills": checked_skills,
        "experience_requirement": require_string(
            data.get("experience_requirement"), "analysis.experience_requirement"
        ),
        "cpt_status": require_status(data.get("cpt_status"), "analysis.cpt_status"),
        "cpt_evidence": require_string(data.get("cpt_evidence"), "analysis.cpt_evidence"),
        "opt_status": require_status(data.get("opt_status"), "analysis.opt_status"),
        "opt_evidence": require_string(data.get("opt_evidence"), "analysis.opt_evidence"),
        "stem_opt_status": require_status(data.get("stem_opt_status"), "analysis.stem_opt_status"),
        "stem_opt_evidence": require_string(data.get("stem_opt_evidence"), "analysis.stem_opt_evidence"),
        "visa_sponsorship_status": require_status(
            data.get("visa_sponsorship_status"), "analysis.visa_sponsorship_status"
        ),
        "visa_sponsorship_evidence": require_string(
            data.get("visa_sponsorship_evidence"), "analysis.visa_sponsorship_evidence"
        ),
        "h1b_status": require_status(data.get("h1b_status"), "analysis.h1b_status"),
        "h1b_evidence": require_string(data.get("h1b_evidence"), "analysis.h1b_evidence"),
        "green_card_status": require_status(
            data.get("green_card_status"), "analysis.green_card_status"
        ),
        "green_card_evidence": require_string(
            data.get("green_card_evidence"), "analysis.green_card_evidence"
        ),
    }


def parse_saved_job_analysis(value: object) -> SavedJobAnalysis:
    """Validate a saved result before listing it. / 조회 전에 저장 결과를 검증합니다."""
    data = require_object(value, "Saved analysis")
    return {
        "source": parse_source_metadata(data.get("source")),
        "model": require_string(data.get("model"), "model"),
        "analyzed_at_utc": require_string(data.get("analyzed_at_utc"), "analyzed_at_utc"),
        "analysis": parse_analysis_result(data.get("analysis")),
    }
