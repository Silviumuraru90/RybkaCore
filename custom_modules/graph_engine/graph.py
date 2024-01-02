import shutil

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def generate_graph(image_name, currency, timeframe, dates, usd_prices, eur_prices):
    fig, ax = plt.subplots()

    ax.set_facecolor("black")
    fig.patch.set_facecolor("#988558")

    (usd_line,) = ax.plot(dates, usd_prices, label="USD", color="green")
    (eur_line,) = ax.plot(dates, eur_prices, label="EUR", color="blue")

    ax.set_title(f"[{currency.upper()}] price over the past [{timeframe.upper()}]", color="yellow")
    ax.set_xlabel("Date", color="yellow")
    ax.set_ylabel("Price", color="yellow")

    # Format the x-axis labels as dates
    date_format = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    # Add adnotations only for week graphs
    if timeframe == "week":
        for date, price in zip(dates, usd_prices):
            ax.text(date, price, f"${price}", color="cyan")

        for date, price in zip(dates, eur_prices):
            ax.text(date, price, f"€{price}", color="cyan")

    ax.legend()

    plt.savefig(f"{image_name}.png")
    shutil.move(f"{image_name}.png", f"custom_modules/telegram/data/pics/{image_name}.png")
