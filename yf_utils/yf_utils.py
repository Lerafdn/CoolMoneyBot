from datetime import datetime, timedelta

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

IMG_PATH = "img.png"


mpl.use("Agg")


class TickerInfo:
    def __init__(self, ticker_name: str):
        self.ticker_name = ticker_name
        self.info = None
        self.img_path = IMG_PATH

    def check_ticker(self):
        self.info = yf.Ticker(self.ticker_name).info
        return self.info

    def get_basic_info(self):
        items = {
            "longName": "*Название*",
            "country": "*Страна*",
            "website": "*Сайт*",
            "industry": "*Отрасль*",
            "operatingCashflow": "*Operating cashflow, $*",
            "ebitda": "*EBITDA, $*",
            "returnOnAssets": "*ROI*",
            "recommendationKey": "*Recommendation*",
            "currentPrice": "*Current price, $*",
            "trailingPE": "*Price/Earnings Ratio*",
        }
        tab = " " * 10
        s = ""
        for c in items:
            s = s + f"\n{items[c]}:\n{tab}{self.info[c]}"
        return s

    def get_fresh_report(self):
        dt_start = (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%d")
        df = yf.download(self.ticker_name, start=dt_start)
        df = df.reset_index().iloc[-1]

        items = {
            "Open": "*Цена открытия, $*",
            "High": "*Максимальная цена, $*",
            "Low": "*Минамальная цена, $*",
            "Close": "*Цена закрытия, $*",
            "Volume": "*Объем торгов, ед.*",
        }
        tab = " " * 10
        s = f"\n*Дата торгов*:\n{tab}{df['Date'].strftime('%Y-%m-%d')}"
        for i in items:
            s += f"\n{items[i]}:\n{tab}{df[i]}"
        return s

    def get_chart(self, df: pd.DataFrame):
        data = df.Close.values
        doublediff = np.diff(np.sign(np.diff(data)))
        peak_locations = np.where(doublediff == -2)[0] + 1

        doublediff2 = np.diff(np.sign(np.diff(-1 * data)))
        trough_locations = np.where(doublediff2 == -2)[0] + 1
        with plt.ioff():
            with plt.style.context("dark_background"):
                plt.figure(figsize=(12, 6))

                plt.plot(df.Close, marker="+", color="green", label="Цена закрытия")
                plt.plot(df.High, ls='--', color="orange", label="Максимальная цена", alpha=0.4)
                plt.plot(df.Low, ls='--', color="blue", label="Минимальная цена", alpha=0.4)
                # plt.fill_between(
                #     df.index,
                #     df.High,
                #     df.Low,
                #     color="cyan",
                #     alpha=0.2,
                #     label="Диапазон дневных торгов",
                # )

                plt.scatter(
                    df.index[peak_locations],
                    df.Close[peak_locations],
                    marker=mpl.markers.CARETUPBASE,
                    color="tab:green",
                    s=100,
                    label="Пики",
                )
                plt.scatter(
                    df.index[trough_locations],
                    df.Close[trough_locations],
                    marker=mpl.markers.CARETDOWNBASE,
                    color="tab:red",
                    s=100,
                    label="Провалы",
                )

                plt.legend(fontsize="large")

                plt.xlabel("Дата")
                plt.ylabel("Стоимость, $")
                plt.xticks(rotation=25, size=8)

                plt.grid(axis="y", ls="-.", color="grey")

                plt.gca().spines["top"].set_alpha(0.0)
                plt.gca().spines["bottom"].set_alpha(0.3)
                plt.gca().spines["right"].set_alpha(0.0)
                plt.gca().spines["left"].set_alpha(0.3)

                plt.title(f"История торгов `{self.ticker_name}`".upper(), color="cyan")

                plt.savefig(self.img_path, dpi=200)

    def get_history_data(self, td_kwargs):
        dt_start = (datetime.utcnow() - timedelta(**td_kwargs)).strftime("%Y-%m-%d")
        df = yf.download(self.ticker_name, start=dt_start)

        self.get_chart(df=df)
