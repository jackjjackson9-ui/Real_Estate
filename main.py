"""Run a simple real estate deal underwriter on local sample listings."""

import csv
import json
import os

from underwrite import underwrite_listing


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as infile:
        return json.load(infile)


def save_csv(rows, path: str):
    fieldnames = [
        "id",
        "address",
        "city",
        "state",
        "zip",
        "purchase_price",
        "rent_monthly_used",
        "noi",
        "cap_rate",
        "coc",
        "notes",
    ]

    with open(path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    config = load_json("config.json")
    listings = load_json("data/sample_listings.json")

    results = [underwrite_listing(listing, config) for listing in listings]

    os.makedirs("output", exist_ok=True)
    output_path = "output/deals.csv"
    save_csv(results, output_path)

    top_5 = sorted(results, key=lambda x: x["coc"], reverse=True)[:5]

    print("Top 5 deals by Cash-on-Cash return")
    print("-" * 60)
    for idx, deal in enumerate(top_5, start=1):
        print(
            f"{idx}. {deal['id']} | {deal['address']}, {deal['city']} {deal['state']} "
            f"| CoC: {deal['coc']:.2%} | Cap Rate: {deal['cap_rate']:.2%} | NOI: ${deal['noi']:,.2f}"
        )

    print("-" * 60)
    print(f"Wrote {len(results)} deals to {output_path}")


if __name__ == "__main__":
    main()
