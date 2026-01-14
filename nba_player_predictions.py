import pandas as pd
import os

def load_csvs(data_dir: str = "data") -> pd.DataFrame:
    files = sorted(
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.endswith(".csv")
    )
    if not files:
        raise FileNotFoundError(f"No CSV files found in: {data_dir}")

    master = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    return master

def per_predictions(master: pd.DataFrame, min_games: int = 65) -> pd.DataFrame:
    df = master[["Player", "Season", "PER", "G"]].copy()

    df["Season"] = pd.to_numeric(df["Season"], errors="coerce")
    df["PER"] = pd.to_numeric(df["PER"], errors="coerce")
    df["G"] = pd.to_numeric(df["G"], errors="coerce")

    df = df.dropna()
    df = df.sort_values(["Player", "Season"])

    g = df.groupby("Player")

    df["PER_2022"] = g["PER"].shift(1)
    df["PER_2023"] = g["PER"].shift(2)
    df["PER_2024"] = g["PER"].shift(3)

    df["G_2022"] = g["G"].shift(1)
    df["G_2023"] = g["G"].shift(2)
    df["G_2024"] = g["G"].shift(3)

    # df["Season_Diff_1"] = df["Season"] - g["Season"].shift(1)
    # df["Season_Diff_2"] = g["Season"].shift(1) - g["Season"].shift(2)
    # df["Season_Diff_3"] = g["Season"].shift(2) - g["Season"].shift(3)

    df = df[
        (df["G"] >= min_games) &
        (df["G_2022"] >= min_games) &
        (df["G_2023"] >= min_games) &
        (df["G_2024"] >= min_games)
    ]

    return df

def print_top_per_predictions(master: pd.DataFrame, n: int = 15, min_games: int = 65) -> None:
    df = per_predictions(master, min_games=min_games)

    # top = (
    #     df.sort_values("PER", ascending=False)
    #       .head(n)[[
    #           "Player",
    #           "Season_Diff_1", "PER_2022", "G_2022",
    #           "Season_Diff_2", "PER_2023", "G_2023",
    #           "Season_Diff_3", "PER_2024", "G_2024",
    #       ]]
    # )
    top = (
        df.sort_values("PER", ascending=False)
          .head(n)[[
              "Player",
              "PER_2022", "G_2022",
              "PER_2023", "G_2023",
              "PER_2024", "G_2024",
          ]]
    )

    print(f"\nTop PER improvements (min {min_games} games in both seasons):")
    print(top.to_string(index=False))

if __name__ == "__main__":
    master = load_csvs()
    print_top_per_predictions(master, n=20, min_games=65)
