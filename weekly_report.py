#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
import oracledb
oracledb.init_oracle_client(lib_dir = r"C:\oracle\instantclient_19_29")
conn = oracledb.connect(
     user = "HR",
     password = "hr",
      dsn = "localhost:1521/XE"
)
df = pd.read_sql("""
    SELECT category, SUM(amount) AS total_amount
    FROM family_expenses
    WHERE expense_date >= TRUNC(SYSDATE) - 7
    GROUP BY category
""", conn)

conn.close()
print(df)


# In[16]:


thresholds = {
    "groceries": 1500,
    "outside": 500,
    "non_veg": 400,
    "snacks": 300,
    "appliances": 500,
    "medicines": 200,
    "diaries": 150
}

report_lines = []
for _, row in df.iterrows():
    category = row["CATEGORY"]
    amount = row["TOTAL_AMOUNT"]
    if category in thresholds:
        status = "✅ Within limit" if amount <= thresholds[category] else f"⚠️ Exceeded by {amount - thresholds[category]}"
        report_lines.append(f"{category}: spent {amount}, threshold {thresholds[category]} → {status}")

weekly_report = "\n".join(report_lines)


# In[18]:


from datetime import datetime

from twilio.rest import Client

account_sid = "ACccb53c88b4b5b32a435106014c99c01a"
auth_token = "552337045197aad22f697aab86d35213"
client = Client(account_sid, auth_token)

from_whatsapp = "whatsapp:+14155238886"   # Twilio sandbox number
family_numbers = [
    "whatsapp:+918940116430",  # your number
    "whatsapp:+919894609112"   # spouse
]

for member in family_numbers:
    message = client.messages.create(
        body=f"📊 Weekly Expense Report ({datetime.now().strftime('%Y-%m-%d')}):\n\n{weekly_report}",
        from_=from_whatsapp,
        to=member
    )
    print(f"Report sent to {member}: {message.sid}")


# In[22]:
import oracledb
oracledb.init_oracle_client(lib_dir = r"C:\oracle\instantclient_19_29")
conn = oracledb.connect(
     user = "HR",
     password = "hr",
      dsn = "localhost:1521/XE"
)
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO expense_reports (report_text, sent_to)
    VALUES (:report_text, :sent_to)
""", {"report_text": weekly_report, "sent_to": member})
conn.commit()
cursor.close()
conn.close()



# In[ ]:




