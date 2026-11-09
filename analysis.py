"""Turn the saved BigQuery results into rate tables, charts and the numbers used in the brief.

The SQL in sql/ was run in the BigQuery console on Google's public GA4 sample dataset
(bigquery-public-data.ga4_obfuscated_sample_ecommerce). Each query's result is saved
as JSON in data/. This script only reads those files, so it runs without a Google account.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG = OUT / "figures"

FUNNEL_STEPS = ["view_item", "add_to_cart", "begin_checkout", "add_shipping_info", "add_payment_info", "purchase"]
STEP_LABELS = ["Viewed item", "Added to cart", "Began checkout", "Added shipping", "Added payment", "Purchased"]
INK = "#2A2A2A"
ACCENT = "#C8553D"
MUTED = "#B9B4AE"


def load(name):
    df = pd.DataFrame(json.loads((DATA / f"{name}.json").read_text()))
    for col in df.columns:
        if col not in ("month", "medium", "device"):
            df[col] = pd.to_numeric(df[col])
    return df


def funnel_table():
    row = load("purchase_funnel").iloc[0]
    users = [int(row[s]) for s in FUNNEL_STEPS]
    table = pd.DataFrame({"step": STEP_LABELS, "users": users})
    table["share_of_all_users_pct"] = (table["users"] / row["all_users"] * 100).round(2)
    table["kept_from_previous_step_pct"] = (table["users"] / table["users"].shift(1) * 100).round(1)
    return table, int(row["all_users"])


def rate_table(name, key):
    df = load(name)
    df["cart_rate_pct"] = (df["cart_users"] / df["users"] * 100).round(2)
    df["purchase_rate_pct"] = (df["purchasers"] / df["users"] * 100).round(2)
    df["cart_to_purchase_pct"] = (df["purchasers"] / df["cart_users"] * 100).round(1)
    df["revenue_per_user_usd"] = (df["revenue_usd"] / df["users"]).round(2)
    return df.set_index(key)


def monthly_table():
    df = load("monthly_overview")
    df["revenue_per_session_usd"] = (df["revenue_usd"] / df["sessions"]).round(2)
    df["avg_order_value_usd"] = (df["revenue_usd"] / df["transactions"]).round(2)
    return df.set_index("month")


def quality_table():
    q = load("data_quality").iloc[0]
    with_id = q["purchase_events"] - q["purchase_no_txn_id"]
    medium = load("traffic_medium").set_index("medium")
    hidden = int(medium.loc[["<Other>", "(data deleted)"], "users"].sum())
    return {
        "purchase_events": int(q["purchase_events"]),
        "purchase_events_without_transaction_id": int(q["purchase_no_txn_id"]),
        "share_without_transaction_id_pct": round(q["purchase_no_txn_id"] / q["purchase_events"] * 100, 1),
        "repeated_purchase_events_with_same_id": int(with_id - q["distinct_txn_ids"]),
        "purchase_events_with_zero_revenue": int(q["purchase_zero_revenue"]),
        "users_with_hidden_medium": hidden,
        "share_users_hidden_medium_pct": round(hidden / q["users"] * 100, 1),
    }


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=INK)


def chart_funnel(table):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    worst = table["kept_from_previous_step_pct"].iloc[1:].idxmin()
    colors = [ACCENT if i == worst else INK for i in table.index]
    ax.barh(table["step"][::-1], table["users"][::-1], color=colors[::-1])
    for i, (users, kept) in enumerate(zip(table["users"][::-1], table["kept_from_previous_step_pct"][::-1])):
        label = f"{users:,}" + ("" if pd.isna(kept) else f"  ({kept:.0f}% of previous step)")
        ax.text(users + 600, i, label, va="center", fontsize=9, color=INK)
    ax.set_xlabel("Users who reached the step (Nov 2020 - Jan 2021)")
    ax.set_xlim(0, table["users"].max() * 1.45)
    ax.set_title("Most users who view a product never add it to the cart", loc="left", fontsize=11, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(FIG / "funnel.png", dpi=160)
    plt.close(fig)


def chart_medium(df):
    known = df.drop(index=["<Other>", "(data deleted)"]).sort_values("purchase_rate_pct")
    names = {"(none)": "Direct", "organic": "Organic search", "referral": "Referral", "cpc": "Paid search (cpc)"}
    fig, ax = plt.subplots(figsize=(8, 3.4))
    colors = [ACCENT if m == "referral" else INK for m in known.index]
    ax.barh([names[m] for m in known.index], known["purchase_rate_pct"], color=colors)
    for i, v in enumerate(known["purchase_rate_pct"]):
        ax.text(v + 0.03, i, f"{v:.2f}%", va="center", fontsize=9, color=INK)
    ax.set_xlabel("Share of users who purchased")
    ax.set_title("Referral users convert best; the other sources are close", loc="left", fontsize=11, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(FIG / "purchase_rate_by_medium.png", dpi=160)
    plt.close(fig)


def chart_monthly(df):
    fig, ax = plt.subplots(figsize=(8, 3.4))
    labels = {"202011": "Nov 2020", "202012": "Dec 2020", "202101": "Jan 2021"}
    ax.bar([labels[m] for m in df.index], df["revenue_usd"], color=[INK, INK, ACCENT])
    for i, v in enumerate(df["revenue_usd"]):
        ax.text(i, v + 3000, f"${v:,.0f}", ha="center", fontsize=9, color=INK)
    ax.set_ylabel("Purchase revenue (USD)")
    ax.set_title("Revenue fell 64% from December to January", loc="left", fontsize=11, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(FIG / "monthly_revenue.png", dpi=160)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(exist_ok=True)
    funnel, all_users = funnel_table()
    medium = rate_table("traffic_medium", "medium")
    device = rate_table("device", "device")
    monthly = monthly_table()
    quality = quality_table()

    funnel.to_csv(OUT / "tables" / "funnel.csv", index=False)
    medium.to_csv(OUT / "tables" / "traffic_medium.csv")
    device.to_csv(OUT / "tables" / "device.csv")
    monthly.to_csv(OUT / "tables" / "monthly.csv")
    (OUT / "data_quality.json").write_text(json.dumps(quality, indent=2))

    chart_funnel(funnel)
    chart_medium(medium)
    chart_monthly(monthly)

    print(f"All users: {all_users:,}")
    print(funnel.to_string(index=False))
    print(medium[["users", "purchasers", "purchase_rate_pct", "cart_to_purchase_pct", "revenue_per_user_usd"]])
    print(device[["users", "purchasers", "purchase_rate_pct", "cart_to_purchase_pct", "revenue_per_user_usd"]])
    print(monthly)
    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()
