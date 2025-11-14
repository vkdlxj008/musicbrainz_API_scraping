# 🎵 Classical Music Data Curation Project: Piano vs Orchestra Trends (1900–2020)

## Research Question
**How has the balance between piano-related and orchestra-related classical album production in the United States evolved between 1900 and 2020?**

---

## Project Overview
This project curates an **original classical music dataset** using the **MusicBrainz API**, focusing on U.S. album releases between 1900 and 2020. It classifies albums into **PianoSolo**, **Orchestra**, **Hybrid** (piano + orchestra, e.g., concertos), and **Unknown**, and analyzes trends in album production across decades.

This data science project demonstrates:

- 🎧 **API Integration:** Collecting classical album data via the MusicBrainz WS/2 API  
- 🧹 **Data Cleaning & Classification:** Refining metadata to classify albums by instrumentation  
- 📊 **Exploratory Data Analysis:** Visualizing long-term recording trends of piano vs orchestra music  
- 💡 **Reproducible Pipeline:** From data collection → cleaning → visualization in one automated process

---

## 🗂️ Project Structure
```
musicbrainz_API_scraping/
├── blog/
│   ├── hybrid_decade_counts.png      # Decade × Genre plot
│   ├── hybrid_piano_share.png        # Piano-related share plot
│   └── hybrid_total_albums.png       # Total album count per decade
├── data/
│   ├── us_classical_raw.csv
│   ├── us_classical_counts_by_decade.csv
│   ├── us_classical_refined_hybrid.csv
│   └── us_classical_counts_hybrid_by_decade.csv
├── notebooks/
│   └── eda.ipynb                     # Exploratory data analysis
├── source/
│   ├── api_get_raw.py                # MusicBrainz API data collection
│   ├── mb_classify_hybrid.py        # Hybrid classification & aggregation
│   └── run_pipeline.py               # Automated end-to-end pipeline
├── .env.example                      # Example environment (USER_AGENT)
├── .gitignore
├── requirements.txt                  # Dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Create Virtual Environment (Recommended)
```bash
python -m venv .venv
.venv\Scripts\activate
source .venv/bin/activate
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure API Access
Create a `.env` file in the root directory:

```bash
USER_AGENT=Stat386Project/1.0 (your_email@example.com)
```

MusicBrainz doesn't require an API key, but User-Agent must include your email for ethical API use.

---

## ▶️ Running the Project

### Option 1: Full Automated Pipeline
```bash
python source/run_pipeline.py
```

This will:
1. Fetch classical album data from the MusicBrainz API
2. Filter by U.S. releases (1900–2020)
3. Classify albums into PianoSolo, Orchestra, Hybrid, Unknown
4. Aggregate by decade
5. Save processed data and visualizations under `/data/` and `/blog/`

### Option 2: Step-by-Step
```bash
python source/api_get_raw.py          # Raw API collection
python source/mb_classify_hybrid.py   # Refine & classify
python notebooks/eda.ipynb            # Visualization / EDA
```

---

## 📊 Dataset Description

### Features
| Column | Description |
|--------|-------------|
| `rg_id` | MusicBrainz release-group ID |
| `title` | Album title |
| `release_title` | Specific release name |
| `release_date` | Release year |
| `release_country` | Country (filtered to US) |
| `primary_type` | Release-group type (Album, etc.) |
| `genre_type` | Basic keyword classification (Piano / Orchestra / Unknown) |
| `genre_refined` | Refined category (PianoSolo / Orchestra / Hybrid / Unknown) |
| `year` | Parsed release year |
| `decade` | Decade grouping (e.g., 1990, 2000) |

### Dataset Size
- ✅ 200+ records (meets minimum requirement)
- ✅ 5+ features
- Coverage: U.S. classical albums spanning 1900–2020

---

## 🧠 Exploratory Data Analysis Highlights

| Graph | Insight |
|-------|---------|
| **Hybrid Decade Counts** | Shows decade-level trends for PianoSolo, Orchestra, Hybrid, Unknown albums |
| **Piano Share by Decade** | Displays relative share of piano-related albums ((PianoSolo + Hybrid) / Total) |
| **Total Album Count** | Contextualizes dataset volume and metadata density per decade |

### Key Findings:
- Piano-related recordings peaked between 1980–2000, reflecting the rise of digital recording and soloist branding.
- Orchestra-focused albums remain steady but less dominant after 1990.
- Metadata richness declines before 1960 due to limited archival records.

---

## 🧭 Ethical Data Use
- **Source:** MusicBrainz WS/2 API
- **Compliance:** Requests spaced at ≥1 sec to respect rate limits
- **User-Agent** includes identifiable contact info
- All metadata under **CC0 license**
- No personal or copyrighted audio files collected

---

## 🧩 Dependencies
```
requests
pandas
matplotlib
python-dotenv
requests-cache
```

---

## 📈 Future Enhancements
- Expand to non-U.S. releases for global comparison
- Integrate Discogs API for cross-verification
- Improve keyword heuristics with NLP-based tagging
- Add interactive dashboards (Plotly / Altair)
- Automate keyword precision testing

---

## 📚 License
This project is for educational purposes under **STAT 386 – Data Curation Project**.

---

## 🙌 Acknowledgments
- **MusicBrainz API** for open classical metadata
- **Python open-source ecosystem** (pandas, matplotlib, dotenv)
- **BYU Statistics Department** for guidance on reproducible data curation practices

---

**(c) 2025 Jun Kim — STAT 386 Data Curation Project**
