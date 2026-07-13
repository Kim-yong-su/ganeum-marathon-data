# ganeum-marathon-data

가늠(Ganeum) 앱의 한국 마라톤/러닝 대회 일정 데이터. `roadrun.co.kr`에서 주 1회 자동 스크래핑한다.

- `marathons.json` — 대회 일정(GitHub Pages로 서빙). 필드: date · dow · name · location · region · distances · organizer · phone · registration · homepage
- `scrape.py` — 스크래퍼(지역 매핑 + 종목 콤마보정)
- `.github/workflows/refresh.yml` — 주간 자동 갱신(cron)

앱은 `https://kim-yong-su.github.io/ganeum-marathon-data/marathons.json`을 받아 로컬 캐시에 저장하고, 실패 시 앱 번들 스냅샷으로 폴백한다.

## 수동 갱신

```bash
pip install -r requirements.txt
python scrape.py        # 올해
python scrape.py 2027   # 특정 연도
```
