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
    tokens = re.split(r"[\s,·]+", loc)
    for city, prov in CITY_PROVINCE.items():
        if any(tok.startswith(city) for tok in tokens):
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


def transform(rows, years=None):
    races = []
    seen = set()
    for r in rows:
        name = (r.get("event_name") or "").strip()
        if not name:
            continue
        try:
            date = f"{int(r['year'])}-{int(r['month']):02d}-{int(r['day']):02d}"
        except (KeyError, ValueError, TypeError):
            continue
        if (date, name) in seen:
            continue
        seen.add((date, name))
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
    out = {
        "updated": datetime.date.today().isoformat(),
        "source": "roadrun.co.kr",
        "count": len(races),
        "races": races,
    }
    if years:
        out["years"] = [int(y) for y in years]
    return out


def default_years(today):
    # 올해만 받으면 연말에 다음 해 대회가 하나도 없어 앱 일정 탭이 비어 간다(2026-11: 마지막 대회 12/28).
    return [str(today.year), str(today.year + 1)]


def upcoming_count(races, today):
    iso = today.isoformat()
    return sum(1 for r in races if r.get("date", "") >= iso)


def check_sane(new, previous, today):
    """덮어쓰기 전 검사. 문제가 있으면 이유 문자열, 없으면 None.

    수집이 '성공'해도 원본 구조가 바뀌면 빈 목록이 조용히 올라간다. 앱은 이 파일을 그대로 보여 주므로
    앞으로 남은 대회가 0건이거나 직전 파일보다 절반 아래로 줄면 저장하지 않고 실패로 끝낸다.
    """
    upcoming = upcoming_count(new["races"], today)
    if upcoming == 0:
        return "오늘 이후 대회가 0건"
    if previous:
        before = upcoming_count(previous.get("races", []), today)
        if before >= 20 and upcoming < before * 0.5:
            return f"오늘 이후 대회가 {before}건에서 {upcoming}건으로 절반 아래로 줄어듦"
    return None


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]
    today = datetime.date.today()
    if len(args) > 1 and args[0] == "--raw":
        rows = json.load(open(args[1], encoding="utf-8"))
        years = None
    else:
        import kr_marathon_schedule as k
        years = args or default_years(today)
        rows = []
        for year in years:
            got = k.get_marathons(year, fetch_details=True)
            print(f"{year}: {len(got)} rows")
            rows.extend(got)
    out = transform(rows, years)
    try:
        previous = json.load(open("marathons.json", encoding="utf-8"))
    except (OSError, ValueError):
        previous = None
    problem = check_sane(out, previous, today)
    if problem and not force:
        print(f"NOT WRITTEN: {problem}. 원본 사이트나 수집 라이브러리를 확인하세요(무시하려면 --force).")
        sys.exit(1)
    with open("marathons.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"wrote marathons.json: {out['count']} races "
          f"({upcoming_count(out['races'], today)} upcoming), region set on "
          f"{sum(1 for r in out['races'] if r['region'])}")


if __name__ == "__main__":
    main()
