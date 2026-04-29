#!/usr/bin/env python3
"""feedback-learner: 누적 피드백을 분석하여 큐레이션 기준을 업데이트합니다."""
import json
import os
import sys

FEEDBACK_PATH = "output/site/feedback.json"
CRITERIA_PATH = ".claude/skills/video-curator/references/curation_criteria.json"
MIN_FEEDBACK_COUNT = 10
ESCALATION_RATIO = 0.9


def main():
    if not os.path.exists(FEEDBACK_PATH):
        print("feedback.json not found, 스킵")
        return

    with open(FEEDBACK_PATH, encoding="utf-8") as f:
        feedback = json.load(f)

    unprocessed = [item for item in feedback if not item.get("processed", True)]
    if len(unprocessed) < MIN_FEEDBACK_COUNT:
        print(f"미처리 피드백 {len(unprocessed)}건 < {MIN_FEEDBACK_COUNT}건 기준, 스킵")
        return

    good = sum(1 for item in unprocessed if item.get("rating") == "GOOD")
    bad = sum(1 for item in unprocessed if item.get("rating") == "BAD")
    total = good + bad
    print(f"피드백 분석: GOOD={good}, BAD={bad}, 합계={total}")

    # 에스컬레이션 체크
    if total > 0 and (good / total >= ESCALATION_RATIO or bad / total >= ESCALATION_RATIO):
        dominant = "GOOD" if good / total >= ESCALATION_RATIO else "BAD"
        print(f"ESCALATION: {dominant} 비율 {max(good,bad)/total:.0%} → 운영자 검토 필요")
        print("자동 기준 변경을 건너뜁니다. run_log.json에 기록됩니다.")
        # 에스컬레이션 시에도 processed 마킹은 하지 않음 (운영자 검토 후 처리)
        return

    # 피드백 통계 업데이트
    with open(CRITERIA_PATH, encoding="utf-8") as f:
        criteria = json.load(f)

    criteria["feedback_stats"]["total_good"] += good
    criteria["feedback_stats"]["total_bad"] += bad
    criteria["feedback_stats"]["processed_count"] += total

    # Phase 3: LLM 기반 preferred_topics/excluded_topics 자동 조정 예정
    # 현재는 통계만 업데이트

    with open(CRITERIA_PATH, "w", encoding="utf-8") as f:
        json.dump(criteria, f, ensure_ascii=False, indent=2)

    # 처리 완료 마킹
    for item in feedback:
        if not item.get("processed", True):
            item["processed"] = True

    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)

    print(f"피드백 처리 완료: GOOD={good}, BAD={bad}")


if __name__ == "__main__":
    main()
