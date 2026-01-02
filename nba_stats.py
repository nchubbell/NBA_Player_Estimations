import pandas as pd
import matplotlib.pyplot as plt
import time
import urllib.request
import urllib.error
import random
from io import StringIO


class Control:
    start_year = 2021
    end_year = 2024
    min_games = 65
    size_plot = 15
    sleep = 3.0
    w_dbpm = .6
    w_dts = .4

ADV_DUPLICATES = [
    "Rk", "Pos", "Age", "Tm", "G", "MP", "GS"
]

def polite_sleep(base: float):
    time.sleep(base + random.uniform(0.5, 1.5))

def build_url(season: int, table: str) -> str:
    if table == "per_game":
        return f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html"
    if table == "advanced":
        return f"https://www.basketball-reference.com/leagues/NBA_{season}_advanced.html"
    
def read_table(url: str, max_retries: int = 6) -> pd.DataFrame:
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            tables = pd.read_html(StringIO(html))
            if not tables:
                raise RuntimeError(f"No tables found at {url}")
            return tables[0]

        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (2 ** attempt) + random.uniform(0.0, 1.5)
                print(f"[429] Too many requests. Waiting {wait:.1f}s then retrying... ({attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            raise

    raise RuntimeError(f"Still rate-limited after {max_retries} retries: {url}")

def load_data(season: int, sleep_s: float = Control.sleep):
    per_game_url = build_url(season, "per_game")
    adv_url = build_url(season, "advanced")

    per_game = read_table(per_game_url)
    polite_sleep(Control.sleep)

    advanced = read_table(adv_url)
    polite_sleep(Control.sleep)

    return per_game, advanced


def merge_season(season: int) -> pd.DataFrame:
    pg, adv = load_data(season, sleep_s=Control.sleep)

    pg["Season"] = season
    adv["Season"] = season

    adv_clean = adv.drop(
        columns=[c for c in ADV_DUPLICATES if c in adv.columns],
        errors="ignore"
    )

    merged = pd.merge(
        pg,
        adv_clean,
        on=["Player", "Season"],
        how="inner",
    )
    return merged

def build_total_dataset() -> pd.DataFrame:
    all_seasons = []

    for season in range(Control.start_year, Control.end_year + 1):
        print(f"Processing season {season}...")
        df_season = merge_season(season)
        all_seasons.append(df_season)
        print("  rows:", len(df_season))

    master = pd.concat(all_seasons, ignore_index=True)
    print("\nMASTER shape:", master.shape)
    return master

def test_columns_no_duplicates():
    df = merge_season(2024)

    duplicates = df.columns[df.columns.duplicated()]
    print("Duplicate columns:", list(duplicates))

    cols = ["Player", "Pos", "Tm", "G", "PTS", "TS%", "BPM", "Season"]
    cols = [c for c in cols if c in df.columns]
    print("\nKey columns preview:")
    print(df[cols].head())


def test_scrape_one_season() -> None:
    season = 2024
    pg, adv = load_data(season, sleep_s=Control.sleep)

    print("Per-game columns:", list(pg.columns))
    print(pg[["Player", "G", "PTS"]].head())

    print("\nAdvanced columns:", list(adv.columns))
    print(adv[["Player", "TS%", "BPM"]].head())

def test_master_dataset():
    master = build_total_dataset()

    print("\nColumns count:", len(master.columns))
    print("First 15 columns:")
    print(list(master.columns)[:15])

    print("\nPreview rows:")
    print(master.head())

def points_improvement(master: pd.DataFrame):
    pts_df = master[["Player", "Season", "PTS"]].copy()
    pts_df = pts_df.sort_values(["Player", "Season"])
    pts_df["ΔPTS"] = pts_df.groupby("Player")["PTS"].diff()

    print(pts_df.head(15))

    print("\nBiggest single-season improvements:")
    print(
        pts_df.sort_values("ΔPTS", ascending=False)
              .head(10)
              [["Player", "Season", "PTS", "ΔPTS"]]
    )

def player_improvement(master: pd.DataFrame):
    per_df = master[["Player", "Season", "PER"]].copy()
    per_df = per_df.sort_values(["Player", "Season"])
    per_df["ΔPER"] = per_df.groupby("Player")["PER"].diff()

    print(per_df.head(15))

    print("\nBiggest single-season improvements:")
    print(
        per_df.sort_values("ΔPER", ascending=False)
              .head(10)
              [["Player", "Season", "PER", "ΔPER"]]
    )



if __name__ == "__main__":

    master = build_total_dataset()
    points_improvement(master)
    player_improvement(master)


