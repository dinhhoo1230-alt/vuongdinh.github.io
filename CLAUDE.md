# Portfolio — Hồ Tất Vương Đình

Portfolio kiến trúc tĩnh, tiếng Việt. HTML/CSS/JS thuần — không build tool.

## Stack
- HTML + CSS + JS thuần. Không bundler.
- Font: **Jost** (Google Fonts) — Futura-style sans. Cả `index.html` lẫn `projects/project-*.html` phải dùng Jost (KHÔNG được dùng Inter).
- Màu accent: `#EF6C00` (cam đất). Token: `--color-accent` trong `css/style.css`.
- Deploy: GitHub Pages tại https://dinhhoo1230-alt.github.io/vuongdinh.github.io/ (repo `dinhhoo1230-alt/vuongdinh.github.io`, branch `main`).

## Cấu trúc
```
index.html                     ← SPA 5 tab (home/about/timeline/projects/contact)
projects/project-{01..06}.html ← Trang chi tiết từng dự án
css/{reset,style}.css          ← Reset + tokens + layout
js/main.js                     ← Tab switching + curtain animation + slide transition project
assets/images/project-{01..06}/← Ảnh từng dự án
admin.html                     ← Admin UI v2 (đọc folder, drag-drop, chọn cover, xoá ảnh)
admin_server.py                ← HTTP server + API (port 8001)
_rebuild_projects.py           ← Script regenerate toàn bộ HTML từ folder ảnh
.claude/launch.json            ← Preview server config (chạy admin_server.py)
```

## Dev server
- Chạy `py admin_server.py` ở D:\portfolio (port 8001).
- Hoặc dùng MCP preview: `preview_start` name=`portfolio`.
- **Gotcha**: nếu start báo "Port 8001 in use", có process Python cũ còn sống. Kill bằng `Stop-Process -Id <pid>` (tìm pid qua `netstat -ano | findstr :8001`).

## Image management — workflow chuẩn ("cách 3")
1. Copy file ảnh thật vào `assets/images/project-XX/` qua Windows Explorer (KHÔNG upload qua admin.html).
2. Mở `http://localhost:8001/admin.html`.
3. Chọn project từ dropdown → server đọc folder qua `GET /api/folder?id=XX`.
4. Click **★** trên thumb để chọn cover; kéo-thả để sắp xếp; click **×** để xoá ảnh khỏi disk.
5. Sửa text (title/meta/desc) nếu cần.
6. Bấm **💾 Lưu dự án** → POST `/api/save-folder` → server tự viết `projects/project-XX.html` (gallery chia rows of 3) + thay card trong `index.html`.

**Hoặc** chạy `py _rebuild_projects.py` để regenerate cả 6 project từ folder (dùng khi cần reset, sửa bug encoding, hoặc đổi nội dung text qua source).

## ⚠️ Gotcha về encoding (QUAN TRỌNG)
KHÔNG dùng PowerShell `Get-Content / Set-Content` để chỉnh file HTML chứa tiếng Việt. Windows PowerShell 5.1 đọc/ghi với mã trang Windows-1252 mặc định → tiếng Việt thành mojibake (`Nhà` → `NhÃ`).

Dùng:
- Edit tool (UTF-8 by default), HOẶC
- Python script (`open(..., encoding='utf-8')`), HOẶC
- PowerShell với `Out-File -Encoding utf8` VÀ `Get-Content -Encoding UTF8` (BỚT cũng dễ sai)

## Cache busters
CSS/JS dùng query `?v=N`. Bump N khi sửa CSS/JS để force reload. Bump qua Python (regex sub trên `index.html` + tất cả `projects/*.html`).

`admin.html` được serve với `Cache-Control: no-store` (config trong `admin_server.py` `end_headers`) — không cần bump.

## Hiệu ứng (đã có)
- **Curtain transition** (tab → tab): màn cam quét ngang, hướng phụ thuộc thứ tự `TAB_ORDER` trong `main.js`. Quay lui = quét ngược.
- **Slide transition** (project → project): trang cũ trượt trái + mờ; trang mới trượt vào từ phải. Áp dụng cho mọi `<a>` trong `.proj-detail`.
- **Next-tab arrow**: nút mũi tên xám nhỏ cố định ở góc dưới-phải của tab About/Timeline/Projects (CSS `.next-arrow`, position:fixed).

## Layout convention
- `.proj-detail__hero`: grid `1fr 2fr` — text trái, cover phải.
- `.proj-detail__desc`: cùng grid `1fr 2fr`, đoạn text nằm cột 2 → căn lề trái thẳng với mép trái của cover.
- Mobile (≤768px): cả hai collapse về 1 cột.
- `.projects-grid`: 3 cột (desktop) / 2 cột (≤900px) / 1 cột (≤520px).

## Server API (admin_server.py)
- `GET /api/folder?id=XX` → liệt kê file trong `assets/images/project-XX/`.
- `POST /api/save-folder` `{id, cover, gallery[], title, meta, desc, prev, hasNext}` → ghi HTML + patch index card.
- `POST /api/delete-image` `{id, name}` → xoá file (vĩnh viễn, không vào Recycle Bin). Có path-traversal guard.
- `POST /api/save` — endpoint cũ (upload base64). Còn nhưng KHÔNG khuyến khích — UI v2 không dùng.

## Patch index card — gotcha
`patch_index()` dùng regex non-greedy match `<a ... class="proj-card">...</a>` đầu tiên trùng href. Nếu file đã có orphan tail từ bug cũ thì regex không tự dọn được → tail còn sót, layout vỡ. Cách check: grep `index.html` xem có 2 lần `</a>` cho cùng project-XX không.

## Git workflow
- Solo project, push thẳng `main`. Không PR.
- Commit author: `Hồ Tất Vương Đình <dinhhoo1230@gmail.com>` (đã set qua `-c user.name=... -c user.email=...` mỗi commit, không global).

## Không xoá / không phá
- `.gitignore` đang exclude `admin.html`, `*.pdf`, vài file ảnh test, `_pdf_preview/`, `Thumbs.db`.
- `admin.html` không được deploy lên Pages (gitignored). Đây là tool local dev.
- `admin_server.py` và `_rebuild_projects.py` cũng là local-only — không cần deploy.

## Nếu site bị broken sau khi sửa source
1. Hard refresh (Ctrl+F5) hoặc bump cache `?v=N`.
2. Nếu tiếng Việt mojibake: regenerate qua `py _rebuild_projects.py`.
3. Nếu index card duplicate/orphan: edit tay xoá tail, hoặc rerun rebuild script.
4. Nếu server không trả JSON cho /api/*: kill process Python cũ trên port 8001, restart.
