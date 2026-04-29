#!/usr/bin/env python3
"""갱신된 curation_criteria.json을 저장합니다."""
import json
import os
import sys
from datetime import datetime, timezone

CRITERIA_PATH = ".claude/skills/video-curator/references/curation_criteria.json"

REQUIRED_KEYS = [
    "version", "last_updated", "update_reason", "categories",
    "inclusion_rules", "scoring_weights", "threshold", "feedback_stats"
]


def validate_criteria(criteria):
    for key in REQUIRED_KEYS:
        if key not in criteria:
            return False, f"필수 키 누락: {key}"
    if not isinstance(criteria["threshold"], (int, float)):
        return False, "threshold는 숫자여야 함"
    weights = criteria.get("scoring_weights", {})
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        return False, f"scoring_weights 합계가 1.0이 아님: {total}"
    return True, None


def save_criteria(criteria, update_reason=""):
    ok, err = validate_criteria(criteria)
    if not ok:
        print(f"ERROR: 기준 파일 검증 실패 - {err}", file=sys.stderr)
        sys.exit(1)

    if update_reason:
        criteria["update_reason"] = update_reason
    criteria["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with open(CRITERIA_PATH, "w", encoding="utf-8") as f:
        json.dump(criteria, f, ensure_ascii=False, indent=2)
    print(f"curation_criteria.json 저장 완료 (v{criteria['version']})")


if __name__ == "__main__":
    # stdin으로 JSON을 받아 저장
    if not sys.stdin.isatty():
        criteria = json.load(sys.stdin)
        reason = sys.argv[1] if len(sys.argv) > 1 else ""
        save_criteria(criteria, reason)
    else:
        print("Usage: echo '<json>' | python save_updated_criteria.py '업데이트 사유'")
