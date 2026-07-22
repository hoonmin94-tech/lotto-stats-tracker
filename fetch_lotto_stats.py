"""
로또 6/45 전체 회차 데이터를 가져와 번호별 출현 빈도 통계를 계산합니다.
"""

import json
import requests
from collections import Counter
from datetime import datetime, timezone

SOURCE_URL = "https://smok95.github.io/lotto/results/all.json"


def fetch_all_draws():
    resp = requests.get(SOURCE_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_stats(draws):
    freq = Counter()
    last_seen_draw = {}

    for d in draws:
        draw_no = d["draw_no"]
        numbers = d["numbers"]
        for n in numbers:
            freq[n] += 1
            last_seen_draw[n] = draw_no

    latest_draw_no = max(d["draw_no"] for d in draws)

    numbers_stat = []
    for n in range(1, 46):
        gap = latest_draw_no - last_seen_draw.get(n, 0)
        numbers_stat.append({
            "number": n,
            "count": freq.get(n, 0),
            "last_seen_draw": last_seen_draw.get(n, None),
            "draws_since_last_seen": gap,
        })

    sorted_by_count = sorted(numbers_stat, key=lambda x: -x["count"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_draws_analyzed": latest_draw_no,
        "numbers": numbers_stat,
        "hot_numbers": [x["number"] for x in sorted_by_count[:5]],
        "cold_numbers": [x["number"] for x in sorted_by_count[-5:]],
    }


def main():
    draws = fetch_all_draws()
    stats = build_stats(draws)

    with open("lotto_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"분석 완료: 총 {stats['total_draws_analyzed']}회차")
    print(f"핫 넘버: {stats['hot_numbers']}")
    print(f"콜드 넘버: {stats['cold_numbers']}")


if __name__ == "__main__":
    main()
