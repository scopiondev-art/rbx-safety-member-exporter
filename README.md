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

## Version Information

The most up-to-date build of this project is always available in the **Releases** section of this repository.

Please use the **latest release** unless you specifically need an older version for testing, comparison, or compatibility purposes.

Previous releases are kept available so users and developers can review, compare, and work with earlier versions when needed.
```
---

## License

This project is licensed under the Apache License 2.0.

Copyright 2026 RealScorpionDev.

See the [LICENSE](LICENSE) and [NOTICE](NOTICE) files for more information.

---

## Official Project

This is the official repository for this project.

Official creator: **RealScorpionDev**  
Official repository: https://github.com/RealScorpionDev/rbx-safety-member-exporter  
Official GitHub profile: https://github.com/RealScorpionDev

Forks and modified versions are allowed under the Apache License 2.0, but they must preserve the required license and notice information and must not claim to be the original official project or impersonate the original creator.

---

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Roblox Corporation.

Roblox is a trademark of Roblox Corporation. This project is an independent open-source tool created for educational and safety-focused purposes.
