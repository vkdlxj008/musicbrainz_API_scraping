import os, time, requests, pandas as pd
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry
from pathlib import Path

load_dotenv()
USER_AGENT = os.environ.get("USER_AGENT")
if not USER_AGENT:
    raise RuntimeError("Set USER_AGENT in .env (e.g., Stat251Project/1.0 (you@domain))")

BASE = "https://musicbrainz.org/ws/2"
SLEEP = 1.2
OUTDIR = Path("data"); OUTDIR.mkdir(exist_ok=True)

session = requests.Session()
retries = Retry(total=5, connect=5, read=5, backoff_factor=1.0,
                status_forcelist=[429,500,502,503,504],
                allowed_methods=["GET"], raise_on_status=False)
session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=2))
session.headers.update({"User-Agent": USER_AGENT, "Accept":"application/json", "Connection":"close"})

def mb_get(endpoint, params):
    url = f"{BASE}/{endpoint}"
    r = session.get(url, params=params, timeout=30)
    print(f"[GET] {r.url} -> {r.status_code}")
    r.raise_for_status()
    return r.json()

def fetch_release_groups(query, limit=100, max_items=500):
    all_items = []
    for offset in range(0, max_items, limit):
        data = mb_get("release-group", {"query": query, "fmt":"json", "limit":limit, "offset":offset})
        items = data.get("release-groups", []) or []
        all_items.extend(items)
        print(f"  - fetched {len(items)} (total {len(all_items)})")
        time.sleep(SLEEP)
        if len(items) < limit:
            break
    return all_items

def fetch_releases_for_rg(rg_id):
    try:
        data = mb_get(f"release-group/{rg_id}", {"fmt":"json", "inc":"releases"})
        time.sleep(SLEEP)
        return data.get("releases", []) or []
    except requests.RequestException as e:
        print(f"[SKIP] {rg_id}: {e}")
        time.sleep(SLEEP*2)
        return []

def main():
    q = ('primarytype:album AND (tag:piano OR tag:orchestra OR piano OR orchestra) '
         'AND (tag:classical OR classical) AND firstreleasedate:[1900-01-01 TO 2020-12-31]')

    print("Searching release-groups...")
    rgs = fetch_release_groups(q, limit=100, max_items=500)
    print(f"Total release-groups fetched: {len(rgs)}")

    rows = []
    for i, rg in enumerate(rgs, 1):
        rg_id = rg["id"]
        title = rg.get("title")
        first_date = rg.get("first-release-date")
        primary_type = rg.get("primary-type")
        releases = fetch_releases_for_rg(rg_id)

        us_releases = []
        for rel in releases:
            if rel.get("country") == "US":
                y = (rel.get("date") or "")[:4]
                year = int(y) if y.isdigit() else None
                if year is None or (1900 <= year <= 2020):
                    us_releases.append(rel)

        if not us_releases:
            continue

        text_blob = " ".join(filter(None, [
            title, rg.get("disambiguation"),
            " ".join(t.get("name","") for t in (rg.get("tags") or []))
        ])).lower()

        if "piano" in text_blob:
            genre_type = "Piano"
        elif any(k in text_blob for k in ["orchestra","symphony","philharmonic"]):
            genre_type = "Orchestra"
        else:
            genre_type = "Unknown"

        for rel in us_releases:
            y = (rel.get("date") or "")[:4]
            year = int(y) if y.isdigit() else None
            rows.append({
                "rg_id": rg_id, "title": title, "first_release_date": first_date,
                "release_title": rel.get("title"), "release_date": rel.get("date"),
                "release_country": rel.get("country"), "primary_type": primary_type,
                "genre_type": genre_type, "year": year
            })

        if i % 200 == 0:
            pd.DataFrame(rows).to_csv(OUTDIR/"us_classical_raw_partial.csv", index=False)
            print(f"[CHECKPOINT] rows={len(rows)} at i={i}")

    df = pd.DataFrame(rows)
    print("\nSample rows:"); print(df.head(10))

    df = df[df["year"].notna()].copy()
    df["decade"] = (df["year"].astype(int) // 10) * 10

    agg = (df.groupby(["decade","genre_type"]).size()
             .reset_index(name="album_count")
             .query("genre_type in ['Piano','Orchestra']")
             .sort_values(["decade","genre_type"]))

    print("\nAggregated counts (by decade & genre_type):"); print(agg.head(20))

    df.to_csv(OUTDIR/"us_classical_raw.csv", index=False)
    agg.to_csv(OUTDIR/"us_classical_counts_by_decade.csv", index=False)
    print(f"\nSaved: {OUTDIR/'us_classical_raw.csv'}, {OUTDIR/'us_classical_counts_by_decade.csv'}")

if __name__ == "__main__":
    main()
