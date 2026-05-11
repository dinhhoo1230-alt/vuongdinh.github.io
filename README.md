# Portfolio Kiến Trúc — Nguyễn Văn A

Portfolio web tĩnh, phong cách tối giản, accent màu cam đất `#ef6c00`. Dựng bằng HTML + CSS + JS thuần — không cần build tool, không cần Node.

---

## Cấu trúc thư mục

```
portfolio/
├── index.html              # Trang chủ (hero + about + projects + skills + experience + contact)
├── projects/
│   ├── project-01.html     # Nhà An Phú
│   ├── project-02.html     # Bảo tàng Ánh Sáng
│   ├── project-03.html     # Căn hộ Phố Cổ
│   ├── project-04.html     # Villa Bãi Dài
│   ├── project-05.html     # Tháp Tre
│   └── project-06.html     # Nhà cộng đồng Yên Bái
├── css/
│   ├── reset.css           # CSS reset
│   ├── style.css           # Tokens (màu, font, spacing) + layout chung
│   └── project.css         # Override cho trang chi tiết
├── js/
│   └── main.js             # Sticky header, mobile nav, scroll reveal, project filter
├── assets/
│   ├── images/
│   │   ├── hero/           # Ảnh portrait / hero
│   │   └── projects/       # Ảnh từng dự án
│   └── cv.pdf              # File CV (cần thay bằng CV thật)
└── README.md
```

---

## Chạy thử local

Cách đơn giản nhất:

1. **Mở trực tiếp**: double-click `index.html` (vài trình duyệt sẽ chặn font Google — nên dùng cách 2).
2. **Live server qua Python**:
   ```powershell
   cd D:\portfolio
   python -m http.server 8000
   ```
   Mở `http://localhost:8000` trên trình duyệt.
3. **VS Code Live Server extension**: chuột phải `index.html` → *Open with Live Server*.

---

## Thay nội dung thật

### 1. Thông tin cá nhân
Mở `index.html` và sửa các chỗ sau (search & replace):

| Tìm | Thay bằng |
|---|---|
| `Nguyễn Văn A` | Tên thật của bạn |
| `dinhhoo1230@gmail.com` | Email thật |
| `+84 000 000 000` | SĐT thật |
| `Hà Nội · 2020 — nay` | Thành phố · năm bắt đầu nghề |

Cập nhật cùng các giá trị này trong cả 6 trang `projects/project-XX.html` (header brand + footer).

### 2. Ảnh chân dung & ảnh dự án
- Bỏ ảnh portrait vào `assets/images/hero/portrait.jpg`, sau đó sửa `index.html`:
  ```html
  <img src="assets/images/hero/portrait.jpg" alt="Chân dung ...">
  ```
- Bỏ ảnh từng dự án vào `assets/images/projects/project-01/`, `project-02/`, ...
- Trong file project-XX.html, thay các URL `https://images.unsplash.com/...` thành đường dẫn tương đối `../assets/images/projects/project-01/hero.jpg`.

### 3. Nội dung dự án
Mỗi `projects/project-XX.html` có 4 phần cần sửa:
- **Title + meta** (khách hàng, địa điểm, diện tích, năm) — trong block `.proj-meta`.
- **Tên dự án + concept** — trong block `.proj-intro`.
- **Gallery** — block `.gallery` với 4 figure (full / split / narrow). Thêm hoặc bớt figure tùy nhu cầu.
- **Bản vẽ kỹ thuật** (chỉ project-01 và project-02 có sẵn) — block `.drawings`. Copy từ project-01 nếu cần thêm cho dự án khác.

### 4. CV PDF
Đặt file CV vào `assets/cv.pdf`. Nút "Tải CV (PDF)" ở section Experience sẽ tự link tới đó.

### 5. Skills (số năm kinh nghiệm)
Sửa block `.skills__grid` trong `index.html`:
- Số năm: `<span class="skill-row__years">6 năm</span>`
- Độ dài thanh cam: `style="--level:95%"` (giảm nếu chưa thành thạo).

### 6. Experience timeline
Sửa các `<li class="timeline__item">` trong section Experience.

---

## Deploy lên GitHub Pages (miễn phí)

1. Cài Git ([git-scm.com](https://git-scm.com)) nếu chưa có.
2. Mở PowerShell tại `D:\portfolio`:
   ```powershell
   git init
   git add .
   git commit -m "Initial portfolio"
   ```
3. Lên [github.com](https://github.com) tạo repo mới, đặt tên `username.github.io` (thay `username` bằng tên GitHub của bạn). **Không** tick "Initialize with README".
4. Liên kết và push:
   ```powershell
   git remote add origin https://github.com/username/username.github.io.git
   git branch -M main
   git push -u origin main
   ```
5. Vào *Settings → Pages*, chọn branch `main` / folder `/ (root)`, lưu.
6. Đợi 1-2 phút, mở `https://username.github.io` — đó là portfolio của bạn.

**Lưu ý**: nếu repo có tên khác (vd `my-portfolio`), URL sẽ là `https://username.github.io/my-portfolio/`. Trong trường hợp đó, mọi đường dẫn nên giữ tương đối (đã làm sẵn — không bắt đầu bằng `/`).

### Custom domain (tùy chọn)
Nếu mua được domain (vd `nguyenvana.com`):
1. Tạo file `CNAME` ở thư mục gốc với 1 dòng: `nguyenvana.com`.
2. Tại nhà cung cấp domain, trỏ A record về 4 IP của GitHub Pages: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
3. Trong *Settings → Pages → Custom domain*, nhập `nguyenvana.com` rồi tick *Enforce HTTPS*.

---

## Tinh chỉnh thiết kế

### Đổi màu nhấn
Trong `css/style.css`, sửa giá trị `--color-accent`:
```css
:root{
  --color-accent: #ef6c00;       /* màu cam hiện tại */
  --color-accent-soft: #FFF4E6;  /* nền nhạt theo cùng tone */
}
```

### Đổi font
File `index.html` (và mỗi project-XX.html) đang load `Fraunces` + `Inter` từ Google Fonts. Muốn đổi:
1. Thay link `<link href="https://fonts.googleapis.com/css2?...">`.
2. Sửa `--ff-serif` và `--ff-sans` trong `css/style.css`.

### Bỏ hiệu ứng scroll fade
Xóa class `reveal` ra khỏi các element trong HTML, hoặc xóa block IntersectionObserver trong `js/main.js`.

---

## Tối ưu trước khi deploy

1. **Nén ảnh**: dùng [tinypng.com](https://tinypng.com) hoặc [squoosh.app](https://squoosh.app), giữ chiều rộng max 1800px cho ảnh hero, 1200px cho ảnh gallery.
2. **Lighthouse**: mở DevTools (F12) → tab *Lighthouse* → Run. Mục tiêu cả 4 chỉ số ≥ 90.
3. **Kiểm tra link**: click thử mọi nav link, nút CTA, link "Quay lại danh sách dự án" trong từng project page.
4. **Test mobile**: F12 → toggle device toolbar → thử iPhone SE (375px), iPad (768px).

---

## Khi cần thêm dự án mới (project-07, 08...)

1. Copy `projects/project-06.html` thành `projects/project-07.html`.
2. Sửa nội dung (meta, gallery, concept).
3. Sửa link "next project" ở cuối project-06 trỏ tới project-07.
4. Trong `index.html`, copy 1 block `<a class="project-card">` trong `.projects__grid`, đổi href + ảnh + tên + meta.

---

## Liên hệ

Nếu cần điều chỉnh thêm (đổi layout, thêm trang Blog, đa ngôn ngữ Anh-Việt, dark mode...), nói tôi biết.
