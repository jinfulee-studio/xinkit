#!/usr/bin/env python3
"""Calculate an evidence-backed Awwwards-grade proxy score and release decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCORER_VERSION = "1.3.0"
RUBRIC_VERSION = "2026-07-20"

DIMENSIONS: dict[str, dict[str, float]] = {
    "design": {
        "concept_art_direction": 0.25,
        "hierarchy_composition": 0.25,
        "typography_color_media": 0.20,
        "system_states": 0.20,
        "responsive": 0.10,
    },
    "usability": {
        "task_information_architecture": 0.25,
        "navigation_discoverability": 0.20,
        "feedback_recovery": 0.20,
        "responsive_input": 0.20,
        "accessibility_control": 0.15,
    },
    "creativity": {
        "original_concept": 0.35,
        "meaningful_interaction": 0.30,
        "brand_specificity": 0.20,
        "media_technology_innovation": 0.15,
    },
    "content": {
        "clarity_relevance": 0.30,
        "narrative_hierarchy": 0.25,
        "evidence_credibility": 0.25,
        "copy_media_localization": 0.20,
    },
}

OFFICIAL_WEIGHTS = {
    "design": 0.40,
    "usability": 0.30,
    "creativity": 0.20,
    "content": 0.10,
}

# Minimum severity: a gate may be upgraded toward P0, never downgraded.
GATE_MIN_SEVERITY = {
    "Q-G01": "P0",
    "Q-G02": "P0",
    "Q-G03": "P1",
    "Q-G04": "P1",
    "Q-G05": "P1",
    "Q-G06": "P1",
    "Q-G07": "P1",
    "Q-G08": "P1",
    "Q-G09": "P1",
    "Q-G10": "P1",
    "Q-G11": "P2",
    "Q-G12": "P1",
}

SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
NON_NA_GATES = {
    "Q-G01",
    "Q-G02",
    "Q-G03",
    "Q-G04",
    "Q-G05",
    "Q-G06",
    "Q-G07",
    "Q-G08",
    "Q-G10",
    "Q-G12",
}
VALID_TAGS = {"MEASURED", "OBSERVED", "PROVIDED", "INFERRED", "UNKNOWN", "CONFLICT"}
VALID_SEVERITIES = set(SEVERITY_RANK)
VALID_STATUSES = {"PASS", "FAIL", "UNKNOWN", "N/A"}
DIRECT_GATE_TAGS = {"MEASURED", "OBSERVED"}
TAG_CONFIDENCE_CAP = {
    "MEASURED": 1.0,
    "OBSERVED": 0.8,
    "PROVIDED": 0.6,
    "INFERRED": 0.4,
    "CONFLICT": 0.0,
    "UNKNOWN": 0.0,
}
ARTIFACT_TYPES = {"production", "staging", "prototype", "figma", "screenshots"}
ACCESS_MODES = {"runtime", "interactive_prototype", "design_file", "screenshots"}
EVIDENCE_KINDS = {
    "screenshot",
    "design_inspection",
    "prototype_walkthrough",
    "runtime_walkthrough",
    "code_inspection",
    "lab_measurement",
    "field_data",
    "user_test",
    "automated_scan",
    "content_record",
    "asset_license",
    "release_plan",
    "approval_record",
    "other",
}
KINDS_ALLOWED_BY_ACCESS_MODE = {
    "screenshots": {
        "screenshot",
        "content_record",
        "asset_license",
        "release_plan",
        "approval_record",
        "other",
    },
    "design_file": {
        "screenshot",
        "design_inspection",
        "content_record",
        "asset_license",
        "release_plan",
        "approval_record",
        "other",
    },
    "interactive_prototype": {
        "screenshot",
        "design_inspection",
        "prototype_walkthrough",
        "user_test",
        "content_record",
        "asset_license",
        "release_plan",
        "approval_record",
        "other",
    },
    "runtime": EVIDENCE_KINDS,
}

# These artifact types cannot prove a PASS for the listed release gates.
UNSUPPORTED_PASS_GATES = {
    "screenshots": {
        "Q-G01",
        "Q-G02",
        "Q-G04",
        "Q-G05",
        "Q-G06",
        "Q-G07",
        "Q-G08",
        "Q-G09",
        "Q-G10",
        "Q-G11",
        "Q-G12",
    },
    "design_file": {"Q-G05", "Q-G07", "Q-G08", "Q-G09", "Q-G10", "Q-G11", "Q-G12"},
    "interactive_prototype": {
        "Q-G05",
        "Q-G07",
        "Q-G08",
        "Q-G09",
        "Q-G10",
        "Q-G11",
        "Q-G12",
    },
    "runtime": set(),
}

PASS_KIND_REQUIREMENTS = {
    "Q-G01": ({"runtime_walkthrough", "user_test"},),
    "Q-G02": ({"runtime_walkthrough", "user_test"},),
    "Q-G03": ({"content_record", "asset_license"},),
    "Q-G04": ({"runtime_walkthrough"},),
    "Q-G05": (
        {"runtime_walkthrough", "user_test"},
        {"code_inspection", "automated_scan", "lab_measurement"},
    ),
    "Q-G06": ({"runtime_walkthrough", "user_test"},),
    "Q-G08": ({"runtime_walkthrough"},),
    "Q-G09": ({"runtime_walkthrough", "user_test"},),
    "Q-G10": ({"runtime_walkthrough", "user_test"},),
    "Q-G11": ({"code_inspection", "automated_scan"},),
    "Q-G12": ({"release_plan"},),
}
FAIL_KIND_REQUIREMENTS = {
    "Q-G01": {"runtime_walkthrough", "user_test", "code_inspection"},
    "Q-G02": {"runtime_walkthrough", "user_test", "code_inspection"},
    "Q-G03": {"content_record", "asset_license"},
    "Q-G04": {"runtime_walkthrough", "lab_measurement"},
    "Q-G05": {
        "runtime_walkthrough",
        "user_test",
        "code_inspection",
        "automated_scan",
        "lab_measurement",
    },
    "Q-G06": {"runtime_walkthrough", "user_test"},
    "Q-G07": {"lab_measurement", "field_data"},
    "Q-G08": {"runtime_walkthrough", "code_inspection"},
    "Q-G09": {"runtime_walkthrough", "user_test", "code_inspection"},
    "Q-G10": {"runtime_walkthrough", "user_test"},
    "Q-G11": {"code_inspection", "automated_scan"},
    "Q-G12": {"release_plan"},
}
NON_WAIVABLE_P1_GATES = {"Q-G12"}
QUOTE_REJECTION_PHRASES = {
    "do not accept",
    "not accepted",
    "reject",
    "block release",
    "拒绝",
    "不接受",
    "不同意",
    "禁止上线",
}

SCREENSHOT_LOW_CONFIDENCE = {
    ("design", "system_states"),
    ("design", "responsive"),
    *{("usability", criterion) for criterion in DIMENSIONS["usability"]},
    ("creativity", "meaningful_interaction"),
    ("creativity", "media_technology_innovation"),
}
FIGMA_MEDIUM_CONFIDENCE = {
    ("design", "system_states"),
    ("design", "responsive"),
    ("usability", "feedback_recovery"),
    ("usability", "responsive_input"),
    ("usability", "accessibility_control"),
    ("creativity", "meaningful_interaction"),
    ("creativity", "media_technology_innovation"),
}

FORCED_UNKNOWN_CRITERIA = {
    "screenshots": {
        ("design", "system_states"),
        ("usability", "feedback_recovery"),
        ("usability", "responsive_input"),
        ("usability", "accessibility_control"),
        ("creativity", "meaningful_interaction"),
        ("creativity", "media_technology_innovation"),
    },
    "design_file": {("usability", "accessibility_control")},
    "interactive_prototype": {("usability", "accessibility_control")},
    "runtime": set(),
}

ACCEPTANCE_FIELDS = {
    "decision",
    "approver",
    "approver_role",
    "quote",
    "timestamp",
    "version",
    "scope",
    "owner",
    "due",
    "approval_evidence_id",
    "verified_by",
    "verified_at",
    "verification_attestation",
}


class InputError(ValueError):
    """Raised when an audit input violates schema or integrity rules."""


def require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{path} must be a non-empty string")
    return value.strip()


def require_number(value: Any, path: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{path} must be a finite number")
    result = float(value)
    if not minimum <= result <= maximum:
        raise InputError(f"{path} must be between {minimum} and {maximum}")
    return result


def parse_timestamp(value: Any, path: str) -> tuple[str, datetime]:
    text = require_text(value, path)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise InputError(f"{path} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InputError(f"{path} must include Z or an explicit UTC offset")
    return text, parsed


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def normalize_status(value: Any, path: str) -> str:
    status = require_text(value, path).upper().replace("_", "/")
    if status == "NA":
        status = "N/A"
    if status not in VALID_STATUSES:
        raise InputError(f"{path} must be one of {sorted(VALID_STATUSES)}")
    return status


def artifact_confidence_cap(access_mode: str, dimension: str, criterion: str) -> float:
    pair = (dimension, criterion)
    if access_mode == "screenshots":
        if pair in SCREENSHOT_LOW_CONFIDENCE:
            return 0.4
        if dimension in {"creativity", "content"}:
            return 0.6
        return 0.8
    if access_mode == "design_file" and pair in FIGMA_MEDIUM_CONFIDENCE:
        return 0.6
    if access_mode == "interactive_prototype" and pair in {
        ("usability", "accessibility_control"),
        ("creativity", "media_technology_innovation"),
    }:
        return 0.6
    return 1.0


def validate_evidence(
    raw: Any,
    audit_time: datetime,
    access_mode: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(raw, list) or not raw:
        raise InputError("evidence must be a non-empty array")
    seen: dict[str, dict[str, Any]] = {}
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        path = f"evidence[{index}]"
        if not isinstance(item, dict):
            raise InputError(f"{path} must be an object")
        evidence_id = require_text(item.get("id"), f"{path}.id")
        if evidence_id in seen:
            raise InputError(f"duplicate evidence id: {evidence_id}")
        tag = require_text(item.get("tag"), f"{path}.tag").upper()
        if tag not in VALID_TAGS:
            raise InputError(f"{path}.tag must be one of {sorted(VALID_TAGS)}")
        kind = require_text(item.get("kind"), f"{path}.kind").lower()
        if kind not in EVIDENCE_KINDS:
            raise InputError(f"{path}.kind must be one of {sorted(EVIDENCE_KINDS)}")
        if kind not in KINDS_ALLOWED_BY_ACCESS_MODE[access_mode]:
            raise InputError(
                f"{path}.kind {kind} is incompatible with access_mode {access_mode}"
            )
        captured_at, captured_datetime = parse_timestamp(
            item.get("captured_at"), f"{path}.captured_at"
        )
        if captured_datetime > audit_time:
            raise InputError(f"{path}.captured_at cannot be later than audit_time")
        approval_record = item.get("approval_record")
        if kind == "approval_record":
            if not isinstance(approval_record, dict):
                raise InputError(f"{path}.approval_record must be an object")
            approval_record = {
                "gate_id": require_text(
                    approval_record.get("gate_id"), f"{path}.approval_record.gate_id"
                ).upper(),
                "decision": require_text(
                    approval_record.get("decision"), f"{path}.approval_record.decision"
                ).upper(),
                "version": require_text(
                    approval_record.get("version"), f"{path}.approval_record.version"
                ),
                "scope": require_text(
                    approval_record.get("scope"), f"{path}.approval_record.scope"
                ),
                "approver": require_text(
                    approval_record.get("approver"), f"{path}.approval_record.approver"
                ),
                "approver_role": require_text(
                    approval_record.get("approver_role"),
                    f"{path}.approval_record.approver_role",
                ),
                "quote_sha256": require_text(
                    approval_record.get("quote_sha256"),
                    f"{path}.approval_record.quote_sha256",
                ).lower(),
            }
        elif approval_record is not None:
            raise InputError(f"{path}.approval_record is only valid for kind approval_record")

        record = {
            "id": evidence_id,
            "tag": tag,
            "kind": kind,
            "source": require_text(item.get("source"), f"{path}.source"),
            "captured_at": captured_at,
            "scope": require_text(item.get("scope"), f"{path}.scope"),
            "limitations": require_text(item.get("limitations"), f"{path}.limitations"),
            "approval_record": approval_record,
        }
        seen[evidence_id] = record
        normalized.append(record)
    return normalized, seen


def validate_evidence_ids(
    raw: Any,
    path: str,
    known_evidence: dict[str, dict[str, Any]],
    *,
    allow_empty: bool,
) -> list[str]:
    if not isinstance(raw, list):
        raise InputError(f"{path} must be an array")
    ids: list[str] = []
    for index, item in enumerate(raw):
        evidence_id = require_text(item, f"{path}[{index}]")
        if evidence_id not in known_evidence:
            raise InputError(f"{path}[{index}] references unknown evidence id {evidence_id}")
        if evidence_id not in ids:
            ids.append(evidence_id)
    if not allow_empty and not ids:
        raise InputError(f"{path} must contain at least one evidence id")
    return ids


def calculate_dimension(
    raw: Any,
    dimension: str,
    reviewer_path: str,
    known_evidence: dict[str, dict[str, Any]],
    access_mode: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError(f"{reviewer_path}.scores.{dimension} must be an object")

    weights = DIMENSIONS[dimension]
    unexpected = sorted(set(raw) - set(weights))
    if unexpected:
        raise InputError(
            f"{reviewer_path}.scores.{dimension} has unknown subcriteria: {', '.join(unexpected)}"
        )

    weighted_known = 0.0
    weighted_confidence = 0.0
    known_weight = 0.0
    unknown: list[str] = []
    subscores: dict[str, Any] = {}

    for criterion, weight in weights.items():
        path = f"{reviewer_path}.scores.{dimension}.{criterion}"
        item = raw.get(criterion)
        if not isinstance(item, dict):
            raise InputError(f"{path} must be an object")
        limitation = require_text(item.get("limitation"), f"{path}.limitation")
        value = item.get("value")
        confidence = require_number(item.get("confidence"), f"{path}.confidence", 0.0, 1.0)

        if (dimension, criterion) in FORCED_UNKNOWN_CRITERIA[access_mode]:
            evidence_ids = validate_evidence_ids(
                item.get("evidence_ids", []),
                f"{path}.evidence_ids",
                known_evidence,
                allow_empty=True,
            )
            unknown.append(criterion)
            subscores[criterion] = {
                "value": None,
                "input_value": value,
                "confidence": 0.0,
                "confidence_cap": 0.0,
                "evidence_ids": evidence_ids,
                "limitation": (
                    f"Forced UNKNOWN: access_mode {access_mode} cannot prove this criterion. "
                    f"{limitation}"
                ),
                "capability_forced_unknown": True,
            }
            continue

        if value is None:
            if confidence != 0:
                raise InputError(f"{path}.confidence must be 0 when value is null")
            evidence_ids = validate_evidence_ids(
                item.get("evidence_ids", []),
                f"{path}.evidence_ids",
                known_evidence,
                allow_empty=True,
            )
            unknown.append(criterion)
            subscores[criterion] = {
                "value": None,
                "confidence": 0.0,
                "confidence_cap": 0.0,
                "evidence_ids": evidence_ids,
                "limitation": limitation,
                "capability_forced_unknown": False,
            }
            continue

        numeric_value = require_number(value, f"{path}.value", 0.0, 10.0)
        if confidence <= 0:
            raise InputError(f"{path}.confidence must be greater than 0 when value is scored")
        evidence_ids = validate_evidence_ids(
            item.get("evidence_ids"),
            f"{path}.evidence_ids",
            known_evidence,
            allow_empty=False,
        )
        records = [known_evidence[evidence_id] for evidence_id in evidence_ids]
        tags = [record["tag"] for record in records]
        unsupported_tags = sorted(set(tags) & {"UNKNOWN", "CONFLICT"})
        if unsupported_tags:
            raise InputError(
                f"{path}.evidence_ids cannot support a numeric score with "
                f"{'/'.join(unsupported_tags)} evidence"
            )
        evidence_cap = min(TAG_CONFIDENCE_CAP[tag] for tag in tags)
        artifact_cap = artifact_confidence_cap(access_mode, dimension, criterion)
        confidence_cap = min(evidence_cap, artifact_cap)
        if confidence > confidence_cap + 1e-9:
            raise InputError(
                f"{path}.confidence exceeds evidence/artifact cap {confidence_cap:.1f}"
            )
        if numeric_value >= 9.0:
            strong_tags = set(tags)
            distinct_kinds = {record["kind"] for record in records}
            distinct_sources = {record["source"].casefold() for record in records}
            if (
                access_mode == "screenshots"
                or len(records) < 2
                or not {"MEASURED", "OBSERVED"}.issubset(strong_tags)
                or len(distinct_kinds) < 2
                or len(distinct_sources) < 2
                or confidence < 0.8
            ):
                raise InputError(
                    f"{path}.value 9–10 requires runtime/design evidence from at least two "
                    "distinct sources and kinds, including MEASURED and OBSERVED evidence, "
                    "with confidence >= 0.8"
                )

        weighted_known += numeric_value * weight
        weighted_confidence += confidence * weight
        known_weight += weight
        subscores[criterion] = {
            "value": numeric_value,
            "confidence": confidence,
            "confidence_cap": confidence_cap,
            "evidence_ids": evidence_ids,
            "limitation": limitation,
            "capability_forced_unknown": False,
        }

    score = weighted_known if not unknown else None
    lower_bound = weighted_known
    upper_bound = weighted_known + (1.0 - known_weight) * 10.0
    return {
        "score": round(score, 3) if score is not None else None,
        "range": [round(lower_bound, 3), round(upper_bound, 3)],
        "confidence": round(weighted_confidence, 3),
        "known_weight": round(known_weight, 3),
        "unknown_subcriteria": unknown,
        "subscores": subscores,
    }


def validate_reviewers(
    raw: Any,
    known_evidence: dict[str, dict[str, Any]],
    access_mode: str,
) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise InputError("reviewers must be a non-empty array")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        path = f"reviewers[{index}]"
        if not isinstance(item, dict):
            raise InputError(f"{path} must be an object")
        reviewer_id = require_text(item.get("id"), f"{path}.id")
        if reviewer_id in seen:
            raise InputError(f"duplicate reviewer id: {reviewer_id}")
        seen.add(reviewer_id)
        scores = item.get("scores")
        if not isinstance(scores, dict):
            raise InputError(f"{path}.scores must be an object")
        missing_dimensions = sorted(set(DIMENSIONS) - set(scores))
        unexpected_dimensions = sorted(set(scores) - set(DIMENSIONS))
        if missing_dimensions:
            raise InputError(f"{path}.scores missing dimensions: {', '.join(missing_dimensions)}")
        if unexpected_dimensions:
            raise InputError(f"{path}.scores has unknown dimensions: {', '.join(unexpected_dimensions)}")
        dimensions = {
            dimension: calculate_dimension(
                scores[dimension],
                dimension,
                path,
                known_evidence,
                access_mode,
            )
            for dimension in DIMENSIONS
        }
        signature_payload = json.dumps(
            dimensions,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        normalized.append(
            {
                "id": reviewer_id,
                "reviewer_identity": require_text(
                    item.get("reviewer_identity"), f"{path}.reviewer_identity"
                ),
                "role": require_text(item.get("role"), f"{path}.role"),
                "scorecard_sha256": hashlib.sha256(signature_payload).hexdigest(),
                "dimensions": dimensions,
            }
        )
    return normalized


def aggregate_dimensions(
    reviewers: list[dict[str, Any]],
    *,
    effective_single_reviewer: bool,
) -> dict[str, dict[str, Any]]:
    aggregates: dict[str, dict[str, Any]] = {}
    for dimension in DIMENSIONS:
        complete_scores = [
            reviewer["dimensions"][dimension]["score"]
            for reviewer in reviewers
            if reviewer["dimensions"][dimension]["score"] is not None
        ]
        lower_bounds = [reviewer["dimensions"][dimension]["range"][0] for reviewer in reviewers]
        upper_bounds = [reviewer["dimensions"][dimension]["range"][1] for reviewer in reviewers]
        confidences = [reviewer["dimensions"][dimension]["confidence"] for reviewer in reviewers]
        incomplete_reviewers = [
            {
                "id": reviewer["id"],
                "unknown_subcriteria": reviewer["dimensions"][dimension]["unknown_subcriteria"],
            }
            for reviewer in reviewers
            if reviewer["dimensions"][dimension]["score"] is None
        ]
        complete = len(complete_scores) == len(reviewers)
        score = statistics.median(complete_scores) if complete else None
        spread = (
            max(complete_scores) - min(complete_scores)
            if len(complete_scores) >= 2
            else None
        )
        reconcile = spread is not None and spread > 1.5
        confidence = statistics.median(confidences)
        if effective_single_reviewer:
            confidence = min(confidence, 0.8)
        if not complete:
            status = "INCOMPLETE"
        elif reconcile:
            status = "RECONCILE"
        else:
            status = "OK"
        aggregates[dimension] = {
            "score": round(score, 3) if score is not None else None,
            "range": [
                round(statistics.median(lower_bounds), 3),
                round(statistics.median(upper_bounds), 3),
            ],
            "confidence": round(confidence, 3),
            "spread": round(spread, 3) if spread is not None else None,
            "status": status,
            "reconciliation_required": reconcile,
            "complete_reviewers": len(complete_scores),
            "reviewer_count": len(reviewers),
            "incomplete_reviewers": incomplete_reviewers,
        }
    return aggregates


def safe_parse_acceptance_time(value: Any, path: str, issues: list[str]) -> datetime | None:
    try:
        return parse_timestamp(value, path)[1]
    except InputError as exc:
        issues.append(str(exc))
        return None


def validate_acceptance(
    raw: Any,
    path: str,
    *,
    artifact_author: str,
    gate_id: str,
    version: str,
    scope: str,
    audit_time: datetime,
    known_evidence: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not isinstance(raw, dict):
        return False, ["risk_acceptance is missing"]
    missing = sorted(
        field
        for field in ACCEPTANCE_FIELDS
        if not isinstance(raw.get(field), str) or not raw[field].strip()
    )
    if missing:
        return False, [f"missing fields: {', '.join(missing)}"]

    approver = raw["approver"].strip()
    verifier = raw["verified_by"].strip()
    if raw["decision"].strip().upper() != "ACCEPT_RISK":
        issues.append("decision must equal ACCEPT_RISK")
    if raw["verification_attestation"].strip().upper() != "DECISION_AND_QUOTE_CONSISTENT":
        issues.append("verification_attestation must equal DECISION_AND_QUOTE_CONSISTENT")
    if approver.casefold() == artifact_author.casefold():
        issues.append("artifact author cannot approve their own release")
    if verifier.casefold() in {artifact_author.casefold(), approver.casefold()}:
        issues.append("verification must be independent from artifact author and approver")

    quote = raw["quote"].strip()
    if len(quote) < 20 or gate_id.casefold() not in quote.casefold():
        issues.append(f"quote must explicitly identify {gate_id}")
    folded_quote = quote.casefold()
    if any(phrase in folded_quote for phrase in QUOTE_REJECTION_PHRASES):
        issues.append("quote contains an explicit rejection that conflicts with ACCEPT_RISK")
    if raw["version"].strip() != version:
        issues.append("risk acceptance version does not match audited version")
    if raw["scope"].strip() != scope:
        issues.append("risk acceptance scope must exactly match audited scope")

    accepted_at = safe_parse_acceptance_time(raw["timestamp"], f"{path}.timestamp", issues)
    due_at = safe_parse_acceptance_time(raw["due"], f"{path}.due", issues)
    verified_at = safe_parse_acceptance_time(raw["verified_at"], f"{path}.verified_at", issues)
    if accepted_at is not None and accepted_at > audit_time:
        issues.append("timestamp cannot be later than audit_time")
    if due_at is not None and due_at <= audit_time:
        issues.append("due must be later than audit_time")
    if verified_at is not None and verified_at > audit_time:
        issues.append("verified_at cannot be later than audit_time")
    if accepted_at is not None and verified_at is not None and verified_at < accepted_at:
        issues.append("verified_at cannot be earlier than timestamp")

    approval_evidence_id = raw["approval_evidence_id"].strip()
    approval_evidence = known_evidence.get(approval_evidence_id)
    if approval_evidence is None:
        issues.append("approval_evidence_id must reference the evidence ledger")
    else:
        if approval_evidence["tag"] != "OBSERVED":
            issues.append(
                "approval_evidence_id must reference independently OBSERVED approval evidence"
            )
        if approval_evidence["kind"] != "approval_record":
            issues.append("approval_evidence_id must have kind approval_record")
        if approval_evidence["scope"] != scope:
            issues.append("approval evidence scope must exactly match audited scope")
        approval_record = approval_evidence.get("approval_record")
        expected_record = {
            "gate_id": gate_id,
            "decision": "ACCEPT_RISK",
            "version": version,
            "scope": scope,
            "approver": approver,
            "approver_role": raw["approver_role"].strip(),
            "quote_sha256": hashlib.sha256(quote.encode("utf-8")).hexdigest(),
        }
        if not isinstance(approval_record, dict) or any(
            approval_record.get(field) != expected
            for field, expected in expected_record.items()
        ):
            issues.append(
                "approval_record metadata must match gate, decision, version, scope, "
                "approver, role and quote hash"
            )
        evidence_at = safe_parse_acceptance_time(
            approval_evidence["captured_at"],
            f"{path}.approval_evidence.captured_at",
            issues,
        )
        if accepted_at is not None and evidence_at is not None and evidence_at < accepted_at:
            issues.append("approval evidence cannot be captured before timestamp")
        if verified_at is not None and evidence_at is not None and evidence_at > verified_at:
            issues.append("approval evidence cannot be captured after verified_at")

    return not issues, issues


def validate_gates(
    raw: Any,
    known_evidence: dict[str, dict[str, Any]],
    *,
    artifact_author: str,
    artifact_type: str,
    access_mode: str,
    version: str,
    scope: str,
    audit_time: datetime,
) -> list[dict[str, Any]]:
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        raise InputError("gates must be an array")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(raw):
        path = f"gates[{index}]"
        if not isinstance(item, dict):
            raise InputError(f"{path} must be an object")
        gate_id = require_text(item.get("id"), f"{path}.id").upper()
        if gate_id in seen:
            raise InputError(f"duplicate gate id: {gate_id}")
        seen.add(gate_id)

        severity = require_text(item.get("severity"), f"{path}.severity").upper()
        if severity not in VALID_SEVERITIES:
            raise InputError(f"{path}.severity must be one of {sorted(VALID_SEVERITIES)}")
        minimum = GATE_MIN_SEVERITY.get(gate_id)
        if minimum is not None and SEVERITY_RANK[severity] > SEVERITY_RANK[minimum]:
            raise InputError(
                f"{path}.severity cannot be lower than {minimum} for required gate {gate_id}"
            )

        input_status = normalize_status(item.get("status"), f"{path}.status")
        if input_status == "N/A" and gate_id in NON_NA_GATES:
            raise InputError(f"{gate_id} cannot be N/A; use PASS, FAIL, or UNKNOWN")
        reason = require_text(item.get("reason"), f"{path}.reason")
        evidence_ids = validate_evidence_ids(
            item.get("evidence_ids", []),
            f"{path}.evidence_ids",
            known_evidence,
            allow_empty=input_status in {"UNKNOWN", "N/A"},
        )

        status = input_status
        downgrade_reasons: list[str] = []
        if status == "PASS" and gate_id in UNSUPPORTED_PASS_GATES[access_mode]:
            status = "UNKNOWN"
            downgrade_reasons.append(
                f"access_mode {access_mode} cannot prove PASS for {gate_id}"
            )
        if status in {"PASS", "FAIL"}:
            tags = {known_evidence[evidence_id]["tag"] for evidence_id in evidence_ids}
            direct_kinds = {
                known_evidence[evidence_id]["kind"]
                for evidence_id in evidence_ids
                if known_evidence[evidence_id]["tag"] in DIRECT_GATE_TAGS
            }
            if not (tags & DIRECT_GATE_TAGS):
                status = "UNKNOWN"
                downgrade_reasons.append(
                    "PASS/FAIL requires at least one MEASURED or OBSERVED evidence item"
                )
        if status == "PASS":
            requirements = PASS_KIND_REQUIREMENTS.get(gate_id, ())
            if gate_id == "Q-G07":
                if artifact_type == "production":
                    requirements = ({"field_data"},)
                elif artifact_type == "staging":
                    requirements = ({"lab_measurement"},)
                else:
                    status = "UNKNOWN"
                    downgrade_reasons.append(
                        f"target artifact_type {artifact_type} cannot prove release performance"
                    )
            missing_requirements = [
                sorted(requirement)
                for requirement in requirements
                if not (direct_kinds & requirement)
            ]
            if status == "PASS" and missing_requirements:
                status = "UNKNOWN"
                readable = " and ".join("/".join(group) for group in missing_requirements)
                downgrade_reasons.append(
                    f"{gate_id} PASS lacks required evidence kind(s): {readable}"
                )
        if status == "FAIL" and gate_id in FAIL_KIND_REQUIREMENTS:
            allowed_fail_kinds = FAIL_KIND_REQUIREMENTS[gate_id]
            if not (direct_kinds & allowed_fail_kinds):
                status = "UNKNOWN"
                downgrade_reasons.append(
                    f"{gate_id} FAIL requires direct evidence kind(s): "
                    f"{'/'.join(sorted(allowed_fail_kinds))}"
                )
        if downgrade_reasons:
            reason = f"{'; '.join(downgrade_reasons)}. Original assessment: {reason}"

        acceptance_complete = False
        acceptance_issues: list[str] = []
        if severity == "P1" and status == "FAIL" and gate_id not in NON_WAIVABLE_P1_GATES:
            acceptance_complete, acceptance_issues = validate_acceptance(
                item.get("risk_acceptance"),
                f"{path}.risk_acceptance",
                artifact_author=artifact_author,
                gate_id=gate_id,
                version=version,
                scope=scope,
                audit_time=audit_time,
                known_evidence=known_evidence,
            )
        elif severity == "P1" and status == "FAIL" and gate_id in NON_WAIVABLE_P1_GATES:
            acceptance_issues = [f"{gate_id} must PASS for final release; risk acceptance is disabled"]

        normalized.append(
            {
                "id": gate_id,
                "minimum_severity": minimum,
                "severity": severity,
                "input_status": input_status,
                "status": status,
                "evidence_ids": evidence_ids,
                "reason": reason,
                "status_downgraded": bool(downgrade_reasons),
                "risk_acceptance_complete": acceptance_complete,
                "risk_acceptance_issues": acceptance_issues,
                "risk_acceptance": item.get("risk_acceptance"),
                "synthetic": False,
            }
        )

    for gate_id, severity in GATE_MIN_SEVERITY.items():
        if gate_id not in seen:
            normalized.append(
                {
                    "id": gate_id,
                    "minimum_severity": severity,
                    "severity": severity,
                    "input_status": None,
                    "status": "UNKNOWN",
                    "evidence_ids": [],
                    "reason": "Required gate omitted from input; normalized to UNKNOWN.",
                    "status_downgraded": True,
                    "risk_acceptance_complete": False,
                    "risk_acceptance_issues": [],
                    "risk_acceptance": None,
                    "synthetic": True,
                }
            )
    return sorted(normalized, key=lambda gate: gate["id"])


def decide_release(gates: list[dict[str, Any]]) -> tuple[str, list[str]]:
    p0_fail = [
        gate["id"] for gate in gates if gate["severity"] == "P0" and gate["status"] == "FAIL"
    ]
    p0_unknown = [
        gate["id"] for gate in gates if gate["severity"] == "P0" and gate["status"] == "UNKNOWN"
    ]
    p1_unaccepted = [
        gate["id"]
        for gate in gates
        if gate["severity"] == "P1"
        and gate["status"] == "FAIL"
        and not gate["risk_acceptance_complete"]
    ]
    p1_unknown = [
        gate["id"] for gate in gates if gate["severity"] == "P1" and gate["status"] == "UNKNOWN"
    ]
    p1_accepted = [
        gate["id"]
        for gate in gates
        if gate["severity"] == "P1"
        and gate["status"] == "FAIL"
        and gate["risk_acceptance_complete"]
    ]

    if p0_fail:
        return "NO-GO", [f"P0 FAIL: {', '.join(p0_fail)}"]
    if p0_unknown:
        return "HOLD", [f"P0 UNKNOWN: {', '.join(p0_unknown)}"]
    if p1_unaccepted:
        return "HOLD", [f"P1 FAIL without verified acceptance: {', '.join(p1_unaccepted)}"]
    if p1_unknown:
        return "HOLD", [f"P1 UNKNOWN: {', '.join(p1_unknown)}"]
    if p1_accepted:
        return "CONDITIONAL-GO", [
            f"P1 FAIL with independently recorded acceptance: {', '.join(p1_accepted)}"
        ]
    return "GO", ["No P0/P1 FAIL or UNKNOWN gates."]


def canonical_sha256(data: dict[str, Any]) -> str:
    try:
        payload = json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise InputError("input must be canonical JSON without NaN or Infinity") from exc
    return hashlib.sha256(payload).hexdigest()


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise InputError("schema_version must equal integer 1")
    project = require_text(data.get("project"), "project")
    version = require_text(data.get("version"), "version")
    artifact_author = require_text(data.get("artifact_author"), "artifact_author")
    scope = require_text(data.get("scope"), "scope")
    artifact_type = require_text(data.get("artifact_type"), "artifact_type").lower()
    if artifact_type not in ARTIFACT_TYPES:
        raise InputError(f"artifact_type must be one of {sorted(ARTIFACT_TYPES)}")
    access_mode = require_text(data.get("access_mode"), "access_mode").lower()
    if access_mode not in ACCESS_MODES:
        raise InputError(f"access_mode must be one of {sorted(ACCESS_MODES)}")
    audit_time_text, audit_time = parse_timestamp(data.get("audit_time"), "audit_time")

    evidence, evidence_by_id = validate_evidence(data.get("evidence"), audit_time, access_mode)
    reviewers = validate_reviewers(data.get("reviewers"), evidence_by_id, access_mode)
    independent_reviewer_count = len(
        {reviewer["reviewer_identity"].casefold() for reviewer in reviewers}
    )
    unique_scorecard_count = len({reviewer["scorecard_sha256"] for reviewer in reviewers})
    effective_single_reviewer = independent_reviewer_count < 2 or unique_scorecard_count < 2
    reviewer_integrity_warnings: list[str] = []
    if independent_reviewer_count < len(reviewers):
        reviewer_integrity_warnings.append(
            "Reviewer identities repeat; isolated passes do not count as independent reviewers."
        )
    if unique_scorecard_count < len(reviewers):
        reviewer_integrity_warnings.append(
            "Duplicate scorecards detected; copied reviews do not increase confidence."
        )

    dimensions = aggregate_dimensions(
        reviewers,
        effective_single_reviewer=effective_single_reviewer,
    )
    overall_complete = all(item["score"] is not None for item in dimensions.values())
    overall_score = (
        sum(dimensions[name]["score"] * weight for name, weight in OFFICIAL_WEIGHTS.items())
        if overall_complete
        else None
    )
    overall_range = [
        sum(dimensions[name]["range"][0] * weight for name, weight in OFFICIAL_WEIGHTS.items()),
        sum(dimensions[name]["range"][1] * weight for name, weight in OFFICIAL_WEIGHTS.items()),
    ]
    overall_confidence = sum(
        dimensions[name]["confidence"] * weight for name, weight in OFFICIAL_WEIGHTS.items()
    )
    if effective_single_reviewer:
        overall_confidence = min(overall_confidence, 0.8)

    gates = validate_gates(
        data.get("gates"),
        evidence_by_id,
        artifact_author=artifact_author,
        artifact_type=artifact_type,
        access_mode=access_mode,
        version=version,
        scope=scope,
        audit_time=audit_time,
    )
    decision, decision_reasons = decide_release(gates)
    reconciliation = [
        name for name, item in dimensions.items() if item["reconciliation_required"]
    ]
    incomplete_dimensions = [
        name for name, item in dimensions.items() if item["status"] == "INCOMPLETE"
    ]

    if overall_score is None:
        comparison = "UNAVAILABLE: required subcriteria are UNKNOWN"
    elif overall_score >= 6.5:
        comparison = "At/above conservative internal 6.5 HM comparison line"
    else:
        comparison = "Below conservative internal 6.5 HM comparison line"

    evidence_summary = {
        tag: sum(1 for item in evidence if item["tag"] == tag)
        for tag in sorted(VALID_TAGS)
        if any(item["tag"] == tag for item in evidence)
    }
    evidence_kind_summary = {
        kind: sum(1 for item in evidence if item["kind"] == kind)
        for kind in sorted(EVIDENCE_KINDS)
        if any(item["kind"] == kind for item in evidence)
    }

    return {
        "schema_version": 1,
        "scorer_version": SCORER_VERSION,
        "rubric_version": RUBRIC_VERSION,
        "input_sha256": canonical_sha256(data),
        "project": project,
        "version": version,
        "artifact_type": artifact_type,
        "access_mode": access_mode,
        "audit_time": audit_time_text,
        "scope": scope,
        "model": {
            "type": "Internal Awwwards-grade proxy",
            "weights": OFFICIAL_WEIGHTS,
            "award_guarantee": False,
            "sotd_threshold": None,
        },
        "reviewer_count": len(reviewers),
        "independent_reviewer_count": independent_reviewer_count,
        "unique_scorecard_count": unique_scorecard_count,
        "reviewer_integrity_warnings": reviewer_integrity_warnings,
        "reviewers": [
            {
                "id": reviewer["id"],
                "reviewer_identity": reviewer["reviewer_identity"],
                "role": reviewer["role"],
                "scorecard_sha256": reviewer["scorecard_sha256"],
            }
            for reviewer in reviewers
        ],
        "evidence_count": len(evidence),
        "evidence_summary": evidence_summary,
        "evidence_kind_summary": evidence_kind_summary,
        "evidence": evidence,
        "dimensions": dimensions,
        "overall": {
            "score_10": round(overall_score, 3) if overall_score is not None else None,
            "score_100": round(overall_score * 10, 1) if overall_score is not None else None,
            "range_10": [round(value, 3) for value in overall_range],
            "confidence": round(overall_confidence, 3),
            "comparison": comparison,
        },
        "incomplete_dimensions": incomplete_dimensions,
        "reconciliation_required": reconciliation,
        "release": {
            "decision": decision,
            "reasons": decision_reasons,
            "score_used_for_decision": False,
        },
        "gates": gates,
        "integrity_notes": [
            "Scores are an internal proxy, not an official Awwwards evaluation.",
            "6.5 is a conservative internal comparison line, not an award prediction.",
            "No fixed public SOTD threshold is asserted.",
            "Approvals require an independently observed record; identity, authority and signature "
            "authenticity remain human-controlled.",
        ],
    }


def format_value(value: Any, digits: int = 2) -> str:
    if value is None:
        return "UNKNOWN"
    return f"{value:.{digits}f}"


def escape_md_cell(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_markdown(result: dict[str, Any]) -> str:
    overall = result["overall"]
    project = escape_md_cell(result["project"])
    lines = [
        f"# {project} — audit calculation",
        "",
        f"- Version: `{escape_md_cell(result['version'])}`",
        f"- Artifact type: `{result['artifact_type']}`",
        f"- Access mode: `{result['access_mode']}`",
        f"- Audit time: `{result['audit_time']}`",
        f"- Release decision: **{result['release']['decision']}**",
        f"- Internal score: **{format_value(overall['score_10'])}/10** "
        f"({format_value(overall['score_100'], 1)}/100)",
        f"- Score range: {overall['range_10'][0]:.2f}–{overall['range_10'][1]:.2f}/10",
        f"- Overall confidence: {overall['confidence']:.2f}",
        f"- Comparison: {overall['comparison']}",
        f"- Scorer/rubric: {result['scorer_version']} / {result['rubric_version']}",
        f"- Input SHA-256: `{result['input_sha256']}`",
        "",
        "## Dimensions",
        "",
        "| Dimension | Score | Range | Confidence | Spread | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name in OFFICIAL_WEIGHTS:
        item = result["dimensions"][name]
        spread = "—" if item["spread"] is None else f"{item['spread']:.2f}"
        lines.append(
            f"| {name.title()} | {format_value(item['score'])} | "
            f"{item['range'][0]:.2f}–{item['range'][1]:.2f} | "
            f"{item['confidence']:.2f} | {spread} | {item['status']} |"
        )
    lines.extend(
        [
            "",
            "## Release gates",
            "",
            "| Gate | Severity | Status | Evidence | Reason |",
            "|---|---|---|---|---|",
        ]
    )
    for gate in result["gates"]:
        evidence = ", ".join(gate["evidence_ids"]) or "—"
        status = gate["status"]
        if gate["input_status"] is not None and gate["input_status"] != status:
            status = f"{gate['input_status']}→{status}"
        lines.append(
            f"| {gate['id']} | {gate['severity']} | {status} | "
            f"{escape_md_cell(evidence)} | {escape_md_cell(gate['reason'])} |"
        )
    lines.extend(["", "Decision basis:"])
    lines.extend(f"- {escape_md_cell(reason)}" for reason in result["release"]["reasons"])
    if result["incomplete_dimensions"]:
        lines.append(
            f"- Incomplete dimensions: {', '.join(result['incomplete_dimensions'])}"
        )
    if result["reconciliation_required"]:
        lines.append(
            f"- Independent review reconciliation required: "
            f"{', '.join(result['reconciliation_required'])}"
        )
    lines.extend(f"- {escape_md_cell(warning)}" for warning in result["reviewer_integrity_warnings"])
    lines.extend(
        [
            "",
            "> This is an internal Awwwards-grade proxy, not an official evaluation or award guarantee.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate evidence-backed internal Awwwards-style scores and release gates."
    )
    parser.add_argument("--input", required=True, type=Path, help="Audit JSON input")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with args.input.open("r", encoding="utf-8") as handle:
            data = json.load(handle, object_pairs_hook=no_duplicate_keys)
        if not isinstance(data, dict):
            raise InputError("top-level JSON must be an object")
        result = calculate(data)
    except (OSError, UnicodeError, json.JSONDecodeError, InputError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(render_markdown(result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
