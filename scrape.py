#!/usr/bin/env python3
"""가늠 대회 일정 스크래퍼: roadrun.co.kr -> marathons.json (지역 매핑 + 종목 콤마보정)."""
import json
import re
import sys
import datetime

METRO = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종"]
PROVINCE = ["경기", "강원", "충북", "충남", "충청", "전북", "전남", "전라", "경북", "경남", "경상", "제주"]
CITY_PROVINCE = {
    "춘천": "강원", "원주": "강원", "강릉": "강원", "태백": "강원", "철원": "강원", "속초": "강원", "평창": "강원", "정선": "강원", "삼척": "강원", "홍천": "강원",
    "안동": "경북", "경주": "경북", "포항": "경북", "구미": "경북", "김천": "경북", "영주": "경북", "상주": "경북", "문경": "경북",
    "창원": "경남", "김해": "경남", "진주": "경남", "통영": "경남", "거제": "경남", "양산": "경남", "사천": "경남", "밀양": "경남", "남해": "경남", "함양": "경남", "장수": "전북",
    "전주": "전북", "군산": "전북", "익산": "전북", "정읍": "전북", "남원": "전북", "김제": "전북",
    "여수": "전남", "순천": "전남", "목포": "전남", "광양": "전남", "나주": "전남", "담양": "전남", "해남": "전남", "곡성": "전남",
    "청주": "충북", "충주": "충북", "제천": "충북", "음성": "충북", "괴산": "충북",
    "천안": "충남", "아산": "충남", "공주": "충남", "서산": "충남", "논산": "충남", "보령": "충남", "당진": "충남", "금산": "충남",
    "고양": "경기", "성남": "경기", "수원": "경기", "용인": "경기", "하남": "경기", "남양주": "경기", "파주": "경기", "김포": "경기",
    "안양": "경기", "부천": "경기", "화성": "경기", "평택": "경기", "의정부": "경기", "이천": "경기", "양평": "경기", "가평": "경기", "포천": "경기", "여주": "경기",
    "제주": "제주", "서귀포": "제주", "울릉": "경북",
}


def region_of(location: str):
    loc = location or ""
    for m in METRO:
        if m in loc:
            return m
    for p in PROVINCE:
        if loc.startswith(p) or (" " + p) in loc:
            return p
    for city, prov in CITY_PROVINCE.items():
        if city in loc:
            return f"{prov} {city}"
    return None


def fix_distances(tags):
    tags = [t.strip() for t in (tags or []) if t and t.strip()]
    out = []
    i = 0
    while i < len(tags):
        t = tags[i]
        if re.fullmatch(r"\d{1,3}", t) and i + 1 < len(tags) and re.match(r"\d{3}", tags[i + 1]):
            out.append(f"{t},{tags[i + 1]}")
            i += 2
        else:
            out.append(t)
            i += 1
    return out


def transform(rows):
    races = []
    for r in rows:
        name = (r.get("event_name") or "").strip()
        if not name:
            continue
        try:
            date = f"{int(r['year'])}-{int(r['month']):02d}-{int(r['day']):02d}"
        except (KeyError, ValueError, TypeError):
            continue
        org = r.get("organizer")
        org = " · ".join(org) if isinstance(org, list) else (org or "")
        loc = r.get("location") or ""
        races.append({
            "date": date,
            "dow": r.get("day_of_week") or "",
            "name": name,
            "location": loc,
            "region": region_of(loc),
            "distances": fix_distances(r.get("tags")),
            "organizer": org,
            "phone": r.get("phone") or "",
            "registration": r.get("registration_period") or "",
            "homepage": r.get("homepage") or "",
        })
    races.sort(key=lambda x: x["date"])
    return {
        "updated": datetime.date.today().isoformat(),
        "source": "roadrun.co.kr",
        "count": len(races),
        "races": races,
    }


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--raw":
        rows = json.load(open(sys.argv[2], encoding="utf-8"))
    else:
        import kr_marathon_schedule as k
        year = sys.argv[1] if len(sys.argv) > 1 else str(datetime.date.today().year)
        rows = k.get_marathons(year, fetch_details=True)
    out = transform(rows)
    with open("marathons.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"wrote marathons.json: {out['count']} races, region set on "
          f"{sum(1 for r in out['races'] if r['region'])}")


if __name__ == "__main__":
    main()
