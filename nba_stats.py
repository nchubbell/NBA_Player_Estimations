import pandas as pd
import matplotlib.pyplot as plt

class Control:
    start_year = 2010
    end_year = 2024
    min_games = 65
    size_plot = 15
    sleep = .7
    w_dbpm = .6
    w_dts = .4

def build_url(season: int, table: str) -> str:
    if table == "per_game":
        return f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html"
    if table == "advanced":
        return f"https://www.basketball-reference.com/leagues/NBA_{season}_advanced.html"