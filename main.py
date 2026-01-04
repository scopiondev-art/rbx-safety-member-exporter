import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import time
import threading
import os
import sys
import csv


# ---------- Paths ----------
def app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def default_exports_folder() -> str:
    folder = os.path.join(app_dir(), "exports")
    os.makedirs(folder, exist_ok=True)
    return folder


def ensure_ext(filename: str, filetype: str) -> str:
    ext = ".txt" if filetype == "TXT" else ".csv"
    if not filename.lower().endswith(ext):
        filename += ext
    return filename


def safe_ui(root: tk.Tk, fn, *args, **kwargs):
    root.after(0, lambda: fn(*args, **kwargs))


# ---------- Saving ----------
def save_txt(path: str, members):
    with open(path, "w", encoding="utf-8") as f:
        for m in members:
            f.write(str(m["userId"]) + "\n")


def save_csv(path: str, members):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["userId", "username", "displayName"])
        for m in members:
            w.writerow([m["userId"], m["username"], m["displayName"]])


# ---------- Fetch (with offline auto-retry + resume) ----------
def fetch_members_with_resume(group_id: str, update_status, delay: float = 0.5):
    """
    Returns: (members, error_message_or_None)
    - Auto-retries on network/DNS issues, continuing from the same cursor.
    - Stops on 403 (private) and returns error message.
    """
    base_url = f"https://groups.roblox.com/v1/groups/{group_id}/users"
    cursor = None
    members = []
    seen_ids = set()

    while True:
        params = {"sortOrder": "Asc", "limit": 100}
        if cursor:
            params["cursor"] = cursor

        # Network loop: keep retrying until request succeeds or a hard-stop condition occurs
        while True:
            try:
                r = requests.get(base_url, params=params, timeout=15)
                break  # success reaching server
            except requests.RequestException:
                # Offline / DNS / temporary fail -> keep retrying
                update_status("Offline / DNS error. Please check internet. Retrying in 3 seconds...")
                time.sleep(3)

        # Hard stops / handling
        if r.status_code == 403:
            return [], "This group's member list is private/hidden (403)."

        if r.status_code == 429:
            update_status("Rate limited (429). Waiting 3 seconds...")
            time.sleep(3)
            continue

        if not r.ok:
            return members, f"HTTP {r.status_code}: {r.text[:150]}"

        payload = r.json()

        # add members
        for item in payload.get("data", []):
            user = item.get("user", {})
            uid = user.get("userId")
            if uid is None:
                continue
            uid = int(uid)
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            members.append({
                "userId": uid,
                "username": str(user.get("username", "")),
                "displayName": str(user.get("displayName", "")),
            })

        cursor = payload.get("nextPageCursor")
        update_status(f"Collected {len(members)} members...")

        if not cursor:
            break

        time.sleep(delay)

    # Sort by userId for neat output
    members.sort(key=lambda x: x["userId"])
    return members, None


# ---------- Worker ----------
def worker(root, group_id, filetype, folder, filename_base, status_label, progress, fetch_btn):
    def update_status(text: str):
        safe_ui(root, status_label.config, text=text)

    safe_ui(root, fetch_btn.config, state="disabled")
    safe_ui(root, progress.start, 10)
    update_status("Starting...")

    members, err = fetch_members_with_resume(group_id, update_status)

    def finish():
        progress.stop()
        fetch_btn.config(state="normal")

        if err:
            status_label.config(text=err)
            messagebox.showwarning("Stopped", err)
            return

        if not members:
            status_label.config(text="No members saved (empty/private/error).")
            return

        # Organize per group
        group_folder = os.path.join(folder, f"group_{group_id}")
        os.makedirs(group_folder, exist_ok=True)

        filename = f"{filename_base}_{group_id}"
        filename = ensure_ext(filename, filetype)
        out_path = os.path.join(group_folder, filename)

        try:
            if filetype == "TXT":
                save_txt(out_path, members)
            else:
                save_csv(out_path, members)
        except Exception as e:
            status_label.config(text=f"Save error: {e}")
            messagebox.showerror("Save error", str(e))
            return

        status_label.config(text=f"Saved {len(members)} members:\n{out_path}")
        messagebox.showinfo("Success", f"Saved {len(members)} members!\n\n{out_path}")

    safe_ui(root, finish)


# ---------- GUI ----------
def main():
    root = tk.Tk()
    root.title("RBX Safety Member Exporter")
    root.geometry("580x370")
    root.resizable(False, False)

    bg = "#20232A"
    root.configure(bg=bg)

    title = tk.Label(root, text="RBX Safety Member Exporter", font=("Segoe UI", 16, "bold"),
                     fg="#61DAFB", bg=bg)
    title.pack(pady=10)

    form = tk.Frame(root, bg=bg)
    form.pack(padx=14, pady=8, fill="x")

    tk.Label(form, text="Group ID:", font=("Segoe UI", 11), fg="white", bg=bg)\
        .grid(row=0, column=0, sticky="w", pady=6)
    group_entry = tk.Entry(form, font=("Segoe UI", 11), width=22)
    group_entry.grid(row=0, column=1, sticky="w", pady=6)

    tk.Label(form, text="File type:", font=("Segoe UI", 11), fg="white", bg=bg)\
        .grid(row=1, column=0, sticky="w", pady=6)
    filetype_var = tk.StringVar(value="TXT")
    filetype_box = ttk.Combobox(form, textvariable=filetype_var, values=["TXT", "CSV"],
                                state="readonly", width=19)
    filetype_box.grid(row=1, column=1, sticky="w", pady=6)

    tk.Label(form, text="Filename (base):", font=("Segoe UI", 11), fg="white", bg=bg)\
        .grid(row=2, column=0, sticky="w", pady=6)
    filename_var = tk.StringVar(value="members")
    filename_entry = tk.Entry(form, font=("Segoe UI", 11), textvariable=filename_var, width=22)
    filename_entry.grid(row=2, column=1, sticky="w", pady=6)

    tk.Label(form, text="Save folder:", font=("Segoe UI", 11), fg="white", bg=bg)\
        .grid(row=3, column=0, sticky="w", pady=6)
    folder_var = tk.StringVar(value=default_exports_folder())
    folder_entry = tk.Entry(form, font=("Segoe UI", 10), textvariable=folder_var, width=44)
    folder_entry.grid(row=3, column=1, sticky="w", pady=6)

    def browse_folder():
        chosen = filedialog.askdirectory(initialdir=folder_var.get() or app_dir())
        if chosen:
            folder_var.set(chosen)

    browse_btn = tk.Button(form, text="Browse", command=browse_folder, bg="#61DAFB",
                           fg="black", relief="flat")
    browse_btn.grid(row=3, column=2, padx=8, pady=6)

    progress = ttk.Progressbar(root, mode="indeterminate", length=540)
    progress.pack(pady=12)

    status_label = tk.Label(root, text="", font=("Segoe UI", 10), fg="white", bg=bg, justify="left")
    status_label.pack(pady=6)

    def start():
        group_id = group_entry.get().strip()
        if not group_id.isdigit():
            messagebox.showerror("Invalid input", "Group ID must be a number.")
            return

        filetype = filetype_var.get()
        folder = folder_var.get().strip()
        filename_base = filename_var.get().strip()

        if not folder:
            messagebox.showerror("Invalid input", "Save folder can't be empty.")
            return
        if not filename_base:
            messagebox.showerror("Invalid input", "Filename can't be empty.")
            return

        t = threading.Thread(
            target=worker,
            args=(root, group_id, filetype, folder, filename_base, status_label, progress, fetch_btn),
            daemon=True
        )
        t.start()

    fetch_btn = tk.Button(root, text="Fetch & Save", font=("Segoe UI", 11, "bold"),
                          command=start, bg="#61DAFB", fg="black", relief="flat", width=18)
    fetch_btn.pack(pady=8)

    footer = tk.Label(root, text="Public groups only • For ethical moderation use",
                      font=("Segoe UI", 9, "italic"), fg="#888", bg=bg)
    footer.pack(side="bottom", pady=8)

    root.mainloop()


if __name__ == "__main__":
    main()
