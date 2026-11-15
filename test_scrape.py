import datetime
import unittest

import scrape


def row(year, month, day, name):
    return {"year": year, "month": month, "day": day, "event_name": name, "location": "서울", "tags": ["10km"]}


class ScrapeTests(unittest.TestCase):
    def test_default_years_include_next_year(self):
        self.assertEqual(scrape.default_years(datetime.date(2026, 11, 15)), ["2026", "2027"])
        self.assertEqual(scrape.default_years(datetime.date(2027, 1, 2)), ["2027", "2028"])

    def test_transform_merges_years_and_drops_duplicates(self):
        rows = [row(2026, 12, 28, "A"), row(2027, 1, 1, "B"), row(2026, 12, 28, "A")]
        out = scrape.transform(rows, ["2026", "2027"])
        self.assertEqual([r["date"] for r in out["races"]], ["2026-12-28", "2027-01-01"])
        self.assertEqual(out["count"], 2)
        self.assertEqual(out["years"], [2026, 2027])

    def test_rejects_when_nothing_upcoming(self):
        today = datetime.date(2026, 12, 30)
        out = scrape.transform([row(2026, 12, 28, "A")])
        self.assertIsNotNone(scrape.check_sane(out, None, today))

    def test_rejects_sudden_drop(self):
        today = datetime.date(2026, 11, 15)
        previous = scrape.transform([row(2026, 12, d, f"P{d}") for d in range(1, 29)])
        new = scrape.transform([row(2026, 12, d, f"N{d}") for d in range(1, 6)])
        self.assertIsNotNone(scrape.check_sane(new, previous, today))

    def test_accepts_normal_refresh(self):
        today = datetime.date(2026, 11, 15)
        previous = scrape.transform([row(2026, 12, d, f"P{d}") for d in range(1, 29)])
        new = scrape.transform([row(2026, 12, d, f"P{d}") for d in range(1, 29)] + [row(2027, 1, 1, "B")])
        self.assertIsNone(scrape.check_sane(new, previous, today))


if __name__ == "__main__":
    unittest.main()
