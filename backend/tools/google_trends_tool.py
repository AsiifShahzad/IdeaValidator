import time
from pytrends.request import TrendReq
from backend.tools._keyword_extractor import extract_keyword_variants


def get_google_trends(query: str) -> dict:
    try:
        variants = extract_keyword_variants(query)
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 30))

        for keyword in variants:
            print(f"[google_trends] Trying: '{keyword}'")
            try:
                pytrends.build_payload([keyword], timeframe="today 3-m", geo="")
                time.sleep(1)
                df = pytrends.interest_over_time()

                if df.empty or keyword not in df.columns:
                    continue

                values = [int(v) for v in df[keyword].tolist()]
                peak   = max(values) if values else 0

                if peak == 0:
                    continue

                first  = sum(values[:len(values)//2]) or 1
                second = sum(values[len(values)//2:]) or 0
                direction = "rising" if second > first * 1.1 else "declining" if second < first * 0.9 else "stable"

                print(f"[google_trends] ✅ Got data for '{keyword}': {direction}, peak={peak}")
                return {
                    "direction":    direction,
                    "peak_interest": peak,
                    "data_points":  values[-8:],
                    "keyword_used": keyword,
                }
            except Exception:
                continue

        print("[google_trends] All variants returned no data")
        return {"direction": "unknown", "peak_interest": 0, "data_points": [], "keyword_used": ""}

    except Exception as e:
        print(f"[google_trends] Error: {e}")
        return {"direction": "unknown", "peak_interest": 0, "data_points": [], "keyword_used": ""}