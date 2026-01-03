import os
import pandas as pd

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


def per_load_csvs_changes(master: pd.DataFrame) -> pd.DataFrame:
    df = master[["Player", "Season", "PER"]].copy()

    df["Season"] = pd.to_numeric(df["Season"], errors="coerce")
    df["PER"] = pd.to_numeric(df["PER"], errors="coerce")

    df = df.dropna(subset=["Player", "Season", "PER"])
    df = df.sort_values(["Player", "Season"])

    g = df.groupby("Player")

    df["Prev_Season"] = g["Season"].shift(1)
    df["Prev_PER"] = g["PER"].shift(1)

    df["Seasons_Diff"] = df["Season"] - df["Prev_Season"]
    df["PER_change"] = df["PER"] - df["Prev_PER"]

    return df


def print_top_per_improvements(master: pd.DataFrame, n: int = 15) -> None:
    df = per_load_csvs_changes(master)

    top = (
        df.dropna(subset=["PER_change"])
          .sort_values("PER_change", ascending=False)
          .head(n)[[
              "Player",
              "Prev_Season",
              "Season",
              "Seasons_Diff",
              "Prev_PER",
              "PER",
              "PER_change"
          ]]
    )

    print("\nTop single-season PER improvements:")
    print(top.to_string(index=False))



def save_per_changes_csv(master: pd.DataFrame, out_path: str = "per_changes.csv") -> None:
    df = per_load_csvs_changes(master)
    df.to_csv(out_path, index=False)
    print(f"\nSaved PER changes to: {out_path}")


if __name__ == "__main__":
    master = load_csvs()
    print_top_per_improvements(master, n=20)
    save_per_changes_csv(master, out_path="per_changes.csv")
