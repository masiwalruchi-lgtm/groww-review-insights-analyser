# Groww Weekly Review Pulse

*Live app:* https://groww-review-insights-analyser-y2wbbtimzerbvuxxt8wfid.streamlit.app/

Turns 8-12 weeks of public App Store and Play Store reviews into a one-page weekly note and an email draft.

*Flow:* Import CSV → strip PII → group into 5 themes → generate note (max 250 words) → draft email

## How to re-run for a new week
1. Export fresh public reviews to a CSV with columns: rating, title, text, date, store.
2. Upload it in the sidebar, or replace data/reviews.csv.
3. Pick 8-12 weeks.
4. Press **Generate weekly note**, then **Generate email**.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

*Optional AI mode:* uses Groq (openai/gpt-oss-20b) for the weekly note and theme explainations. Set GROQ_API_KEY as an environment variable or Streamlit secret. Without it, the app uses rule-based grouping.

## Theme legend
- *Order Execution:* trigger/SL/limit orders, price mismatch, rejected or delayed trades, charges
- *Customer Support:* slow replies, unresolved tickets
- *Withdrawals & Funds:* slow withdrawals, deposits, refunds
- *App Stability:* crashes, lag, bugs, device compatibility
- *Account & Security:* login, OTP, KYC, verification

Short praise with no specific issue stays outside the themes and is reported as a count.

## Privacy
Only public review exports are used. Emails, links, phone numbers, long IDs and @handles are masked, and only the rating, title, text, date and store columns are kept.
