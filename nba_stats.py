import pandas as pd
import matplotlib.pyplot as plt
import time

class Control:
    start_year = 2010
    end_year = 2024
    min_games = 65
    size_plot = 15
    sleep = .7
    w_dbpm = .6
    w_dts = .4

ADV_DUPLICATES = [
    "Rk", "Pos", "Age", "Tm", "G", "MP", "GS"
]

def build_url(season: int, table: str) -> str:
    if table == "per_game":
        return f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html"
    if table == "advanced":
        return f"https://www.basketball-reference.com/leagues/NBA_{season}_advanced.html"
    
def read_table(url: str) -> pd.DataFrame:
    tables = pd.read_html(url)
    return tables[0]

def load_data(season: int, sleep_s: float = 0.0):
    per_game_url = build_url(season, "per_game")
    adv_url = build_url(season, "advanced")

    per_game = read_table(per_game_url)
    advanced = read_table(adv_url)

    if sleep_s > 0:
        time.sleep(sleep_s)

    return per_game, advanced

def merge_season(season: int) -> pd.DataFrame:
    pg, adv = load_data(season, sleep_s=0.0)

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
    pg, adv = load_data(season, sleep_s=0.0)

    print("Per-game columns:", list(pg.columns))
    print(pg[["Player", "G", "PTS"]].head())

    print("\nAdvanced columns:", list(adv.columns))
    print(adv[["Player", "TS%", "BPM"]].head())


if __name__ == "__main__":
    test_scrape_one_season()
    test_columns_no_duplicates()

