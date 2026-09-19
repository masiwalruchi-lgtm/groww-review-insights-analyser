Groww Weekly Review Pulse
Live app: 
Turns 8-12 weeks of public App Store and Play Store reviews into a weekly one-page note and an email draft.
Flow
Import CSV -> strip PII -> group into 5 themes -> generate note (max 250 words) -> draft email
Re-run for a new week
Export fresh public reviews to a CSV with columns: rating, title, text, date, store.
Upload it in the sidebar, or replace data/reviews.csv.
Pick 8-12 weeks, then press Generate weekly note and Generate email.
Run locally: pip install -r requirements.txt then streamlit run app.py.
Optional AI mode: set ANTHROPIC_API_KEY as an environment variable or Streamlit secret. Without it the app uses rule-based grouping.
Theme legend
Order Execution: trigger/SL/limit orders, price mismatch, rejected or delayed trades
Withdrawals & Funds: slow withdrawals, deposits, refunds, charges
Customer Support: slow replies, unresolved tickets
App Stability: crashes, lag, bugs, device compatibility
Account & Security: login, OTP, KYC, verification
Short praise with no specific issue stays outside the themes and is reported as a count.
Privacy
Only public review exports are used. Emails, links, phone numbers, long IDs and @handles are masked, and only rating, title, text, date, store columns are kept.
