import os, requests, time, math, pandas as pd
from requests.adapters import HTTPAdapter, Retry

USER_AGENT = "Stat386Project/1.0 (akfmdktm@gmail.com)"
BASE = "https://musicbrainz.org/ws/2"
SLEEP = 1.2

session = requests.Session()
retries = Retry(
    total=5, connect=5, read=5,
    backoff_factor=1.0,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)
session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=2))
session.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Connection": "close",
})

def mb_get(endpoint, params):
    url = f"{BASE}/{endpoint}"
    r = session.get(url, params=params, timeout=30)
    print(f"[GET] {r.url} -> {r.status_code}")
    r.raise_for_status()
    return r.json()

def fetch_release_groups(query, limit=100, max_items=500):
    all_items = []
    for offset in range(0, max_items, limit):
        data = mb_get("release-group", {
            "query": query,
            "fmt": "json",
            "limit": limit,
            "offset": offset
        })
        items = data.get("release-groups", [])
        all_items.extend(items)
        print(f"  - fetched {len(items)} (total {len(all_items)})")
        time.sleep(1)
        if len(items) < limit:
            break
    return all_items

def fetch_releases_for_rg(rg_id):
    data = mb_get("release-group/" + rg_id, {
        "fmt": "json",
        "inc": "releases"
    })
    rels = data.get("releases", []) or []
    time.sleep(1)
    return rels

def main():
    q = (
        'primarytype:album '
        'AND (tag:piano OR tag:orchestra OR piano OR orchestra) '
        'AND (tag:classical OR classical) '
        'AND firstreleasedate:[1900-01-01 TO 2020-12-31]'
    )

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
                date_str = (rel.get("date") or "")[:4]
                year = int(date_str) if date_str.isdigit() else None
                if year is None or (1900 <= year <= 2020):
                    us_releases.append(rel)

        if not us_releases:
            continue

        text_blob = " ".join(filter(None, [
            title,
            rg.get("disambiguation"),
            " ".join(t.get("name","") for t in rg.get("tags",[]) or [])
        ])).lower()

        if any(k in text_blob for k in ["piano"]):
            genre_type = "Piano"
        elif any(k in text_blob for k in ["orchestra", "symphony", "philharmonic"]):
            genre_type = "Orchestra"
        else:
            genre_type = "Unknown"

        for rel in us_releases:
            date_str = (rel.get("date") or "")[:4]
            year = int(date_str) if date_str.isdigit() else None
            rows.append({
                "rg_id": rg_id,
                "title": title,
                "first_release_date": first_date,
                "release_title": rel.get("title"),
                "release_date": rel.get("date"),
                "release_country": rel.get("country"),
                "primary_type": primary_type,
                "genre_type": genre_type,
                "year": year
            })

        if i % 20 == 0:
            print(f"Processed {i}/{len(rgs)} release-groups... (rows={len(rows)})")

    df = pd.DataFrame(rows)
    print("\nSample rows:")
    print(df.head(10))

    df = df[df["year"].notna()].copy()
    df["decade"] = (df["year"] // 10) * 10

    agg = df.groupby(["decade", "genre_type"]).size().reset_index(name="album_count")
    agg = agg[agg["genre_type"].isin(["Piano", "Orchestra"])]
    agg = agg.sort_values(["decade", "genre_type"])

    print("\nAggregated counts (by decade & genre_type):")
    print(agg.head(20))

    df.to_csv("us_classical_raw.csv", index=False)
    agg.to_csv("us_classical_counts_by_decade.csv", index=False)
    print("\nSaved: us_classical_raw.csv, us_classical_counts_by_decade.csv")

if __name__ == "__main__":
    main()

