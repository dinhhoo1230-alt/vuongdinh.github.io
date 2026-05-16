# -*- coding: utf-8 -*-
"""
deploy.py — Wrapper deploy có safety net cho portfolio.

Chạy: py deploy.py

Các bước:
  1. Chạy check.py — abort nếu fail
  2. Hiện git status + diff summary
  3. Hỏi commit message
  4. git add -A
  5. git commit với author Hồ Tất Vương Đình <dinhhoo1230@gmail.com>
  6. git push origin main
  7. In URL production để mở verify

Mọi bước có thể abort bằng Ctrl+C hoặc trả lời 'n' khi được hỏi.
"""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

AUTHOR_NAME = "Hồ Tất Vương Đình"
AUTHOR_EMAIL = "dinhhoo1230@gmail.com"
REMOTE = "origin"
BRANCH = "main"
PROD_URL = "https://dinhhoo1230-alt.github.io/vuongdinh.github.io/"

# ANSI
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def step(n: int, total: int, label: str) -> None:
    print(f"\n{BOLD}{CYAN}[{n}/{total}] {label}{RESET}")


def info(msg: str) -> None:
    print(f"  {msg}")


def ok(msg: str) -> None:
    print(f"  {GREEN}✓ {msg}{RESET}")


def fail(msg: str) -> None:
    print(f"  {RED}✗ {msg}{RESET}")


def confirm(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    try:
        ans = input(f"  {prompt}{suffix} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    if not ans:
        return default
    return ans in ("y", "yes")


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Chạy lệnh, trả CompletedProcess. Raise nếu check=True và non-zero."""
    kwargs = dict(cwd=ROOT, text=True, encoding="utf-8")
    if capture:
        kwargs["capture_output"] = True
    return subprocess.run(cmd, check=check, **kwargs)


def abort(msg: str, code: int = 1) -> "None":
    print(f"\n{RED}{BOLD}✗ ABORT{RESET} — {msg}")
    sys.exit(code)


# ----------------------------------------------------------------------------
# Steps
# ----------------------------------------------------------------------------
def step_1_check() -> None:
    step(1, 6, "Chạy check.py")
    check_path = ROOT / "check.py"
    if not check_path.exists():
        fail("Không tìm thấy check.py")
        if not confirm("Tiếp tục mà KHÔNG chạy check?", default=False):
            abort("user huỷ")
        return
    result = run([sys.executable, str(check_path)], check=False)
    if result.returncode != 0:
        abort("check.py fail — fix lỗi trước khi deploy")
    ok("check.py PASS")


def step_2_status() -> None:
    step(2, 6, "Git status")
    r = run(["git", "status", "--short"], capture=True)
    output = (r.stdout or "").strip()
    if not output:
        abort("Working tree sạch — không có gì để deploy", code=0)
    print()
    for line in output.splitlines():
        print(f"  {DIM}{line}{RESET}")
    # Diff summary
    r2 = run(["git", "diff", "--stat", "HEAD"], capture=True, check=False)
    diff_out = (r2.stdout or "").strip()
    if diff_out:
        print()
        print(f"  {DIM}--- Diff summary ---{RESET}")
        for line in diff_out.splitlines():
            print(f"  {DIM}{line}{RESET}")
    print()
    if not confirm("Tiếp tục commit & push?", default=True):
        abort("user huỷ")


def step_3_message() -> str:
    step(3, 6, "Commit message")
    print(f"  {DIM}Mẹo: dạng 'fix(scope): mô tả ngắn' — vd: 'fix(project-03): cover lệch mobile'{RESET}")
    try:
        msg = input(f"  {BOLD}> {RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        abort("user huỷ")
    if not msg:
        abort("commit message rỗng")
    if len(msg) < 6:
        if not confirm(f"Message '{msg}' rất ngắn. Vẫn dùng?", default=False):
            abort("user huỷ")
    return msg


def step_4_commit(message: str) -> None:
    step(4, 6, "git add + commit")
    run(["git", "add", "-A"])
    ok("git add -A xong")
    commit_cmd = [
        "git",
        "-c", f"user.name={AUTHOR_NAME}",
        "-c", f"user.email={AUTHOR_EMAIL}",
        "commit",
        "-m", message,
    ]
    r = run(commit_cmd, check=False)
    if r.returncode != 0:
        abort("git commit fail")
    ok(f"Committed as {AUTHOR_NAME} <{AUTHOR_EMAIL}>")


def step_5_push() -> None:
    step(5, 6, f"git push {REMOTE} {BRANCH}")
    if not confirm(f"Push lên {REMOTE}/{BRANCH}?", default=True):
        info("Bỏ qua push. Commit đã lưu local — push tay khi sẵn sàng.")
        return
    r = run(["git", "push", REMOTE, BRANCH], check=False)
    if r.returncode != 0:
        abort("git push fail — check credentials hoặc kết nối mạng")
    ok(f"Pushed lên {REMOTE}/{BRANCH}")


def step_6_verify() -> None:
    step(6, 6, "Hậu kiểm production")
    info(f"GitHub Pages cần ~1-2 phút để build.")
    info(f"Mở {BOLD}{PROD_URL}{RESET} sau đó kiểm:")
    info(f"  · Trang vừa sửa render đúng")
    info(f"  · Một trang ngẫu nhiên khác (chống regress)")
    info(f"  · Console không có 404 ảnh (Linux server case-sensitive)")


def main() -> int:
    if os.name == "nt":
        os.system("")
    print(f"{BOLD}deploy.py — Portfolio deploy wrapper{RESET}")
    print(f"{DIM}Root: {ROOT}{RESET}")

    # Sanity: đang ở repo git?
    if not (ROOT / ".git").exists():
        abort(f"{ROOT} không phải git repo")

    try:
        step_1_check()
        step_2_status()
        msg = step_3_message()
        step_4_commit(msg)
        step_5_push()
        step_6_verify()
    except KeyboardInterrupt:
        print()
        abort("user nhấn Ctrl+C")

    print(f"\n{GREEN}{BOLD}✓ DONE.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
