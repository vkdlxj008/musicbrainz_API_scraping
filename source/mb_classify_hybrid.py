import os
import re
import unicodedata
import pandas as pd

PIANO_SOLO_KEYWORDS = [
    "piano", "etude", "prelude", "nocturne", "mazurka", "ballade", "scherzo",
    "polonaise", "waltz", "walzer", "fantaisie", "fantasy", "rhapsody", "impromptu",
    "bagatelle", "barcarolle", "arabeske", "berceuse", "kinderszenen", "kreisleriana",
    "clavier", "invention", "sinfonia", "partita", "goldberg", "pelerinage",
    "images", "estampes", "bergamasque", "annees", "transcendental"
]

ORCHESTRA_KEYWORDS = [
    "orchestra", "symphony", "philharmonic", "concerto", "suite",
    "overture", "tone poem", "requiem", "mass", "cantata"
]

OTHER_INSTRUMENTS = [
    "violin", "violoncello", "cello", "flute", "clarinet", "oboe", "horn",
    "harp", "organ", "trumpet", "trombone", "bassoon", "guitar", "lute", "saxophone"
]

def word_re(words):
    parts = [r"\b" + re.escape(w) + r"\b" if " " not in w else r"\b" + re.escape(w) + r"\b"
             for w in words]
    return re.compile("|".join(parts), flags=re.IGNORECASE)

RE_PIANO   = word_re(PIANO_SOLO_KEYWORDS)
RE_ORCH    = word_re(ORCHESTRA_KEYWORDS)
RE_OTHER   = word_re(OTHER_INSTRUMENTS)

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    return s.lower()

def detect_genre_from_text(text: str) -> str:
    """Hybrid > Orchestra > PianoSolo > Unknown"""
    t = normalize_text(text)
    piano_hit = bool(RE_PIANO.search(t))
    orch_hit  = bool(RE_ORCH.search(t))
    other_hit = bool(RE_OTHER.search(t))
    if piano_hit and orch_hit:
        return "Hybrid"
    if orch_hit:
        return "Orchestra"
    if piano_hit and not other_hit:
        return "PianoSolo"
    if piano_hit and other_hit:
        return "Unknown"
    return "Unknown"

def main():
    in_path = "us_classical_raw.csv"
    out_dir = "data"
    os.makedirs(out_dir, exist_ok=True)

    df = pd.read_csv(in_path)

    if "year" not in df.columns:
        df["year"] = pd.to_numeric(df.get("release_date", "").astype(str).str[:4], errors="coerce")

    combo_cols = []
    for col in ["title", "release_title", "primary_type", "disambiguation"]:
        if col in df.columns:
            combo_cols.append(col)
        else:
            df[col] = ""

    df["__text__"] = df[combo_cols].astype(str).agg(" ".join, axis=1)

    df["genre_refined"] = df["__text__"].apply(detect_genre_from_text)

    dedup_keys = [k for k in ["rg_id", "release_title"] if k in df.columns]
    if dedup_keys:
        before = len(df)
        df = df.drop_duplicates(subset=dedup_keys)
        after = len(df)
        print(f"Dedup: {before} -> {after}")

    df = df[df["year"].notna()].copy()
    df["decade"] = (df["year"].astype(int) // 10) * 10

    agg = (
        df.groupby(["decade", "genre_refined"])
          .size()
          .reset_index(name="album_count")
          .sort_values(["decade", "genre_refined"])
    )

    out_dir = "data"

    refined_path = os.path.join(out_dir, "us_classical_refined_hybrid.csv")
    counts_path  = os.path.join(out_dir, "us_classical_counts_hybrid_by_decade.csv")

    df.drop(columns="__text__", inplace=True)
    df.to_csv(refined_path, index=False)
    agg.to_csv(counts_path, index=False)

    print("\n=== Head(Refined) ===")
    print(df[["title","release_title","year","genre_refined"]].head(10))
    print("\n=== Aggregated by decade & genre ===")
    print(agg.head(20))
    print(f"\nSaved:\n  {refined_path}\n  {counts_path}")

if __name__ == "__main__":
    main()

