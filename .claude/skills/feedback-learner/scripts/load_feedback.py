#!/usr/bin/env python3
"""feedback.json에서 미처리 피드백을 로드합니다."""
import json
import os
import sys

FEEDBACK_PATH = "output/site/feedback.json"


def load_unprocessed():
    if not os.path.exists(FEEDBACK_PATH):
        return []
    with open(FEEDBACK_PATH, encoding="utf-8") as f:
        feedback = json.load(f)
    return [item for item in feedback if not item.get("processed", True)]


if __name__ == "__main__":
    items = load_unprocessed()
    print(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"\n미처리 피드백: {len(items)}건", file=sys.stderr)
