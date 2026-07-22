# -*- coding: utf-8 -*-
"""
check.py — Kiểm tra portfolio trước khi commit/deploy.

Chạy: py check.py

Kiểm:
  1. Mojibake tiếng Việt (kí tự Ã, Æ°, áº trong file đã encode UTF-8 đúng)
  2. Cache version ?v=N đồng bộ giữa index.html, projects/*.html,
     admin_server.py, _rebuild_projects.py
  3. Ảnh được reference trong HTML có tồn tại trên disk
  4. Orphan </a> liền nhau trong index.html (bug patch_index cũ)
  5. <html lang="vi"> và <meta charset="UTF-8"> trong mọi HTML

Exit code:
  0 = pass (có thể có warning, không có error)
  1 = fail
"""

from __future__ import annotations
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# Màu ANSI cho terminal (Windows 10+ hỗ trợ qua VT)
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)
    print(f"{RED}  ✗ {msg}{RESET}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"{YELLOW}  ⚠ {msg}{RESET}")


def ok(msg: str) -> None:
    print(f"{GREEN}  ✓ {msg}{RESET}")


def section(name: str) -> None:
    print(f"\n{BOLD}{CYAN}[{name}]{RESET}")


# ----------------------------------------------------------------------------
# Check 1: Mojibake
# ----------------------------------------------------------------------------
def check_mojibake() -> None:
    section("1/5  Encoding / mojibake")
    # Trong tiếng Việt UTF-8 đã encode đúng, KHÔNG bao giờ xuất hiện
    # các kí tự sau ở dạng bare (chúng chỉ xuất hiện khi UTF-8 bị
    # decode lại bằng Windows-1252):
    #   Ã  — A-tilde
    #   Æ°  — A-with-hook + degree sign (mojibake của ư)
    #   áº  — small a + circle (mojibake của ạ, ậ, ấ, ...)
    #   Ä‘  — A-diaeresis + apostrophe (mojibake của đ)
    bad_markers = [
        ("Ã", "A-tilde (mojibake của à á ã ...)"),
        ("Æ°", "Æ° (mojibake của ư)"),
        ("Ä‘", "Ä‘ (mojibake của đ)"),
    ]

    html_files = [ROOT / "index.html"] + sorted((ROOT / "projects").glob("*.html"))
    found = False
    for f in html_files:
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            err(f"{f.relative_to(ROOT)}: không decode được UTF-8 ({e})")
            found = True
            continue
        for marker, desc in bad_markers:
            count = text.count(marker)
            if count > 0:
                err(f"{f.relative_to(ROOT)}: thấy {count}x '{marker}' — {desc}")
                found = True

    if not found:
        ok(f"Không có dấu hiệu mojibake trong {len(html_files)} file HTML")


# ----------------------------------------------------------------------------
# Check 2: Cache version sync
# ----------------------------------------------------------------------------
def check_cache_version() -> None:
    section("2/5  Cache version ?v=N đồng bộ")
    pattern = re.compile(r"\?v=(\d+)")
    files = [
        ROOT / "index.html",
        ROOT / "admin_server.py",
        ROOT / "_rebuild_projects.py",
    ] + sorted((ROOT / "projects").glob("*.html"))

    # version -> [list of files containing this version]
    versions: dict[str, list[str]] = {}
    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        matches = pattern.findall(text)
        for v in set(matches):
            versions.setdefault(v, []).append(str(f.relative_to(ROOT)))

    if not versions:
        warn("Không tìm thấy ?v=N ở đâu cả — có thể đã đổi convention?")
        return

    if len(versions) == 1:
        v = next(iter(versions))
        ok(f"Tất cả file dùng ?v={v} ({sum(len(x) for x in versions.values())} file)")
    else:
        err(f"Cache version KHÔNG đồng bộ — tìm thấy {len(versions)} version khác nhau:")
        for v, file_list in sorted(versions.items(), key=lambda x: -len(x[1])):
            print(f"      ?v={v}  →  {len(file_list)} file")
            for fn in file_list[:5]:
                print(f"         · {fn}")
            if len(file_list) > 5:
                print(f"         · ... +{len(file_list)-5} file nữa")


# ----------------------------------------------------------------------------
# Check 3: Broken image / asset refs
# ----------------------------------------------------------------------------
def check_broken_refs() -> None:
    section("3/5  Asset references (ảnh, CSS, JS)")
    html_files = [ROOT / "index.html"] + sorted((ROOT / "projects").glob("*.html"))
    # Tách src="..." và href="...{css|js|jpg|png|...}"
    src_pattern = re.compile(r'src="([^"]+)"')
    href_asset_pattern = re.compile(
        r'href="([^"]+\.(?:css|js|jpg|jpeg|png|webp|gif|svg|pdf|ico))"',
        re.IGNORECASE,
    )

    total_refs = 0
    broken = 0
    for f in html_files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        refs: set[str] = set()
        refs.update(src_pattern.findall(text))
        refs.update(href_asset_pattern.findall(text))

        for ref in refs:
            # Bỏ URL ngoài và data:
            if ref.startswith(("http://", "https://", "//", "data:", "mailto:", "#")):
                continue
            # Bỏ query string ?v=N
            ref_clean = ref.split("?", 1)[0]
            # Resolve relative to file's parent
            target = (f.parent / ref_clean).resolve()
            total_refs += 1
            if not target.exists():
                err(f"{f.relative_to(ROOT)} → '{ref}' (không tồn tại)")
                broken += 1

    if broken == 0:
        ok(f"Cả {total_refs} asset reference đều hợp lệ")


# ----------------------------------------------------------------------------
# Check 4: Orphan </a> trong index.html
# ----------------------------------------------------------------------------
def check_orphan_anchors() -> None:
    section("4/5  Orphan </a> trong index.html (bug patch_index cũ)")
    idx = ROOT / "index.html"
    if not idx.exists():
        warn("Không có index.html?")
        return

    text = idx.read_text(encoding="utf-8")

    # Mỗi project chỉ được xuất hiện 1 lần ở dạng card
    card_pattern = re.compile(
        r'<a\s+href="projects/project-(\d{2})\.html"\s+class="proj-card"'
    )
    counts: dict[str, int] = {}
    for m in card_pattern.finditer(text):
        pid = m.group(1)
        counts[pid] = counts.get(pid, 0) + 1

    dup = [pid for pid, c in counts.items() if c > 1]
    if dup:
        for pid in dup:
            err(f"project-{pid} xuất hiện {counts[pid]}x trong index.html (mong đợi 1)")
    else:
        n_pages = len(list((ROOT / "projects").glob("project-*.html")))
        if len(counts) != n_pages:
            warn(f"Tìm thấy {len(counts)} project card trong index.html (mong đợi {n_pages} theo số trang dự án)")

    # Phát hiện cấu trúc </a></a> kế tiếp nhau
    orphan_pattern = re.compile(r"</a>\s*</a>")
    orphans = orphan_pattern.findall(text)
    if orphans:
        err(f"Tìm thấy {len(orphans)} cặp </a></a> liền nhau — có thể là orphan tail")

    if not dup and len(counts) == 6 and not orphans:
        ok("6 project card duy nhất, không có orphan </a>")


# ----------------------------------------------------------------------------
# Check 5: <html lang="vi"> và charset UTF-8
# ----------------------------------------------------------------------------
def check_html_meta() -> None:
    section("5/5  <html lang='vi'> + charset UTF-8")
    html_files = [ROOT / "index.html"] + sorted((ROOT / "projects").glob("*.html"))
    issues = 0
    for f in html_files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        if not re.search(r'<html[^>]*\blang\s*=\s*"vi"', text, re.IGNORECASE):
            err(f"{f.relative_to(ROOT)}: thiếu <html lang=\"vi\">")
            issues += 1
        if not re.search(r'<meta[^>]*charset\s*=\s*"?utf-?8"?', text, re.IGNORECASE):
            err(f"{f.relative_to(ROOT)}: thiếu <meta charset=\"UTF-8\">")
            issues += 1
    if issues == 0:
        ok(f"Tất cả {len(html_files)} file có lang=vi và charset utf-8")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> int:
    # Enable VT mode trên Windows
    if os.name == "nt":
        os.system("")

    print(f"{BOLD}check.py — Portfolio pre-deploy checks{RESET}")
    print(f"{DIM}Root: {ROOT}{RESET}")

    check_mojibake()
    check_cache_version()
    check_broken_refs()
    check_orphan_anchors()
    check_html_meta()

    print()
    print(f"{BOLD}═══ Tổng kết ═══{RESET}")
    if errors:
        print(f"  {RED}{len(errors)} lỗi{RESET}")
    else:
        print(f"  {GREEN}0 lỗi{RESET}")
    if warnings:
        print(f"  {YELLOW}{len(warnings)} cảnh báo{RESET}")

    if errors:
        print(f"\n{RED}{BOLD}✗ FAIL{RESET} — fix lỗi trên trước khi deploy.")
        return 1
    print(f"\n{GREEN}{BOLD}✓ PASS{RESET} — sẵn sàng deploy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
