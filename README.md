# ganeum-marathon-data

가늠(Ganeum) 앱의 한국 마라톤/러닝 대회 일정 데이터. `roadrun.co.kr`에서 주 1회 자동 스크래핑한다.

- `marathons.json` — 대회 일정(GitHub Pages로 서빙). 필드: date · dow · name · location · region · distances · organizer · phone · registration · homepage
- `scrape.py` — 스크래퍼(지역 매핑 + 종목 콤마보정). 기본은 **올해와 다음 해**를 함께 받는다(올해만 받으면 연말에 일정이 비어 간다).
- `test_scrape.py` — 연도·중복·안전 검사 시험. 자동 갱신 전에 먼저 돈다.
- `.github/workflows/refresh.yml` — 주간 자동 갱신(cron)

앱은 `https://kim-yong-su.github.io/ganeum-marathon-data/marathons.json`을 받아 로컬 캐시에 저장하고, 실패 시 앱 번들 스냅샷으로 폴백한다.

## 안전 검사

새 결과에서 오늘 이후 대회가 0건이거나, 직전 파일보다 절반 아래로 줄면 `marathons.json`을 덮어쓰지 않고 실패로 끝난다(Actions 실패 메일로 알 수 있다). 원본 사이트 구조가 바뀌어 빈 목록이 조용히 올라가는 것을 막기 위해서다. 확인 뒤 그래도 올려야 하면 `python scrape.py --force`.

## 수동 갱신

```bash
pip install -r requirements.txt
python scrape.py             # 올해 + 다음 해
python scrape.py 2027        # 특정 연도만
```
