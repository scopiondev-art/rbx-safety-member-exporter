# RBX Safety Member Exporter

A small open-source Tkinter app that exports **public Roblox group** member **UserIDs** to **TXT** or **CSV**.
Designed for moderation workflows (banlists, audits, safety tools).

✅ Public groups only  
🚫 No bypassing private/hidden member lists (403)

---

## Features

- Export member **UserIDs** from a Roblox group
- Save as **TXT** (IDs only) or **CSV** (UserID + username + displayName)
- Choose **save folder**, **file name**, and **file type**
- Automatically organizes exports into: `group_<GROUPID>/`
- Handles rate limits (429) and retries on temporary network/DNS issues

---

## Requirements

- **Python 3.10+** (3.11/3.12 also works)
- `requests`

Install dependencies:

```bash
pip install -r requirements.txt
