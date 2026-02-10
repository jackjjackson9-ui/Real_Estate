# Real Estate New Listing Text Notifier (08742)

Very simple Python app that:

1. Pulls listings from Realtor.com for ZIP `08742`.
2. Compares against previously seen listing IDs in `seen_listings.json`.
3. Sends one daily SMS with **only new listings** (address + link) to `+1-732-610-9003`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your Twilio credentials.

## Run once

```bash
python listing_notifier.py
```

## Daily scheduling (cron)

Example: run every day at 9:00 AM server time.

```bash
crontab -e
```

Add:

```cron
0 9 * * * cd /workspace/Real_Estate && /usr/bin/python3 listing_notifier.py >> cron.log 2>&1
```

## Notes

- First run treats every currently visible listing as "new" and texts all of them.
- If there are no new listings, it sends: `No new 08742 listings today.`
