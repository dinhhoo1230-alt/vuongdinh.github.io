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
js/main.js                     ← Tab switching + curtain animation + slide transition + lightbox + keyboard nav
assets/images/project-{01..06}/← Ảnh dự án (flat mode) HOẶC 4 subfolder con (sectioned mode)
  └── ban-ve/, render-3d/, thi-cong/, thuc-te/  ← optional subfolder cho sectioned gallery
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

**Hoặc** chạy `py _rebuild_projects.py` để regenerate cả 6 project từ folder (dùng khi cần reset, sửa bug encoding, hoặc đổi nội dung text qua source). Script là **flat-mode only**: project nào có subfolder (sectioned) sẽ bị skip kèm warning.

## Sectioned gallery mode (4 mục: bản vẽ / 3D / thi công / thực tế)

Mỗi project có thể bật **sectioned mode** để chia gallery thành 4 mục có heading riêng. Activation: tạo bất kỳ subfolder nào trong `assets/images/project-XX/`:

| Slug subfolder | Heading hiển thị | Ý nghĩa |
|---------------|------------------|---------|
| `ban-ve/` | Bản vẽ khai triển | Output AutoCAD/Revit |
| `render-3d/` | Hình 3D render | V-Ray/Lumion, trước khi xây |
| `thi-cong/` | Thi công thực tế | Ảnh quá trình thi công |
| `thuc-te/` | Hình ảnh thực tế | Ảnh dự án sau hoàn thiện |

**Workflow:**
1. Tạo subfolder qua Windows Explorer → server tự detect mode = `sectioned`.
2. Copy ảnh vào đúng subfolder (subfolder rỗng → section bị ẩn hoàn toàn ở trang dự án).
3. **Cover** vẫn ở folder root `project-XX/` (không thuộc section nào). Nếu muốn pick cover từ ảnh trong subfolder, server fallback tìm ảnh trong subfolder.
4. Mở admin → admin tự render 5 vùng (cover pool + 4 sections), drag-drop scoped per-section (không kéo file giữa nhóm — phải move qua Explorer).
5. Save → server gen HTML có `<section class="gallery-section">` cho mỗi nhóm có ảnh, numbering 01/02/... tính theo sections không rỗng.

**Lightbox** không cần đổi — duyệt qua tất cả ảnh xuyên 4 sections theo DOM order, counter tổng.

**Backwards compat:** project chưa có subfolder → flat mode (như cũ, không có `<section>` wrapper). Migration không bắt buộc — chuyển từng project khi rảnh.

**Slug ASCII** (`ban-ve` chứ không `bản-vẽ`) để né mojibake Windows-1252. Label tiếng Việt nằm trong dict `SECTION_LABELS` ở `admin_server.py` và `admin.html`.

## ⚠️ Gotcha về encoding (QUAN TRỌNG)
KHÔNG dùng PowerShell `Get-Content / Set-Content` để chỉnh file HTML chứa tiếng Việt. Windows PowerShell 5.1 đọc/ghi với mã trang Windows-1252 mặc định → tiếng Việt thành mojibake (`Nhà` → `NhÃ`).

Dùng:
- Edit tool (UTF-8 by default), HOẶC
- Python script (`open(..., encoding='utf-8')`), HOẶC
- PowerShell với `Out-File -Encoding utf8` VÀ `Get-Content -Encoding UTF8` (BỚT cũng dễ sai)

## Cache busters
CSS/JS dùng query `?v=N` (hiện tại `v=19`). Bump N khi sửa CSS/JS để force reload. Bump qua Python (regex sub trên `index.html` + tất cả `projects/*.html` + 2 generator script `admin_server.py` & `_rebuild_projects.py`).

`admin.html` được serve với `Cache-Control: no-store` (config trong `admin_server.py` `end_headers`) — không cần bump.

## Hiệu ứng (đã có)
- **Curtain transition** (tab → tab): màn cam quét ngang, hướng phụ thuộc thứ tự `TAB_ORDER` trong `main.js`. Quay lui = quét ngược.
- **Slide transition** (project → project): trang cũ trượt trái + mờ; trang mới trượt vào từ phải. Áp dụng cho mọi `<a>` trong `.proj-detail`.
- **Next-tab arrow**: nút mũi tên xám nhỏ cố định ở góc dưới-phải của tab About/Timeline/Projects (CSS `.next-arrow`, position:fixed).
- **Lightbox gallery**: click ảnh trong `.gallery` → mở fullscreen với prev/next + counter. Esc đóng, ←/→ chuyển ảnh (wrap quanh), click backdrop hoặc ảnh cũng đóng. JS tự inject `.lightbox` vào `<body>` lúc init nếu page có ảnh gallery.
- **Keyboard nav**: ← / → chuyển tab SPA (theo `TAB_ORDER`), không wrap. Bị disable khi lightbox đang mở, mobile menu open, hoặc đang gõ trong input/textarea/select. Phải defensive-check `e.target.matches` (target có thể là Document, không có method `.matches()`).
- **Lazy loading**: ảnh gallery đều có `loading="lazy"`. Cover ảnh ở hero KHÔNG lazy (above-the-fold). Generators trong `admin_server.py` + `_rebuild_projects.py` đều tự thêm.
- **Sectioned gallery**: project có subfolder `ban-ve/render-3d/thi-cong/thuc-te/` → gallery render thành các `<section class="gallery-section">` có heading + numbering 01/02/... Section rỗng bị skip. Style heading ở `.gallery-section__label` trong `style.css`. Lightbox tự duyệt xuyên sections nhờ chung wrapper `.gallery`. Xem mục "Sectioned gallery mode" ở trên.

## Layout convention
- `.proj-detail__hero`: grid `1fr 2fr` — text trái, cover phải.
- `.proj-detail__desc`: cùng grid `1fr 2fr`, đoạn text nằm cột 2 → căn lề trái thẳng với mép trái của cover.
- Mobile (≤768px): cả hai collapse về 1 cột.
- `.projects-grid`: 3 cột (desktop) / 2 cột (≤900px) / 1 cột (≤520px).

## Server API (admin_server.py)
- `GET /api/folder?id=XX` → trả về `{mode:"flat"|"sectioned", rootFiles[], sections{ban-ve,render-3d,thi-cong,thuc-te}, files[], info}`.
- `POST /api/save-folder` accept 2 shape:
  - **Flat**: `{id, cover, gallery[], title, meta, desc, prev, hasNext}` → gen flat HTML
  - **Sectioned**: `{id, cover, sections{ban-ve,render-3d,thi-cong,thuc-te}, title, meta, desc, prev, hasNext}` → gen HTML có `<section>` (skip section rỗng)
- `POST /api/delete-image` `{id, name, section?}` → xoá file (vĩnh viễn, không vào Recycle Bin). `section` optional (cho sectioned mode); null = xoá ở folder root. Có path-traversal guard mở rộng cho subfolder.
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
