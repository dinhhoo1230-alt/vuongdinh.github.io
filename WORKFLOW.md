# WORKFLOW — Portfolio Hồ Tất Vương Đình

Playbook chuẩn cho mọi đợt sửa site. Chia 7 pha, đi theo thứ tự, không nhảy cóc.

Câu thần chú: **Hiểu → Khoanh → Sửa nhỏ → Test rộng → Dọn → Deploy → Hậu kiểm**.

---

## Pha 1 — Trinh sát (5 phút, KHÔNG SKIP)

Trước khi gõ phím đầu tiên:

1. Đọc lại `CLAUDE.md`, đặc biệt mục "Gotcha về encoding" và "Patch index card".
2. `git status` + `git log --oneline -5` xem repo đang ở đâu, có gì pending.
3. Nếu là task visual: mở `http://localhost:8001/` (chạy `py admin_server.py` trước) hoặc production xem state hiện tại — đừng sửa thứ mình chưa nhìn thấy.
4. Nếu yêu cầu mơ hồ: hỏi lại. Đoán là cách nhanh nhất phá thứ đang chạy ổn.

**Câu hỏi tự đặt:** "Mình đã hiểu vấn đề chưa, hay đang giả định?"

---

## Pha 2 — Khoanh scope

Liệt kê trước khi sửa:

- Task này đụng file gì? (HTML / CSS / JS / image / `admin_server.py` / `_rebuild_projects.py`)
- Sửa cục bộ một file hay phải regen toàn bộ qua `py _rebuild_projects.py`?
- Project nào ở flat mode, project nào ở sectioned mode? Quyết định ảnh hưởng đến cách edit.
- Có touch CSS/JS không? Nếu có → cuối cùng phải bump cache `?v=N`.
- Có ảnh hưởng cả 6 project page hay chỉ 1? Nếu cả 6 → ưu tiên sửa ở generator script chứ không sửa tay 6 file.

**Nguyên tắc:** sửa root cause (generator) trước, sửa output (HTML đã gen) sau.

---

## Pha 3 — Sửa nhỏ, verify ngay

- Một thay đổi → reload browser → ok mới đi tiếp.
- **KHÔNG** bulk-edit 6 file rồi xem cuối cùng — vỡ là không biết file nào sai.
- Với tiếng Việt: dùng Edit tool (UTF-8) hoặc Python `open(..., encoding='utf-8')`. **Tuyệt đối tránh** PowerShell `Set-Content` / `Get-Content` mặc định.
- Hard refresh `Ctrl+F5` sau mỗi sửa CSS/JS để né cache trình duyệt.

---

## Pha 4 — Test rộng trước khi commit

Checklist mỗi lần đụng layout/JS:

- [ ] 5 tab SPA: home / about / timeline / projects / contact — chuyển qua lại OK
- [ ] 6 project page — mở từng cái, gallery render đủ
- [ ] Responsive: desktop / 900px / 520px breakpoint
- [ ] Keyboard nav: ← / → đổi tab, không wrap, không bị trigger khi gõ trong input
- [ ] Lightbox: click ảnh mở fullscreen, ← → chuyển, Esc đóng, counter đúng
- [ ] Curtain transition (tab) và slide transition (project → project) mượt
- [ ] Cover hero KHÔNG lazy-load, gallery thumbnail PHẢI lazy-load
- [ ] Console browser không có error/warning đỏ

---

## Pha 5 — Dọn dẹp

- Chạy `py check.py` — script tự kiểm. Pass mới đi tiếp.
- Bump cache `?v=N` nếu sửa CSS/JS. **Phải bump cả**: `index.html`, mọi `projects/*.html`, `admin_server.py` (HTML template), `_rebuild_projects.py` (HTML template). Quên một chỗ là next regen sẽ tụt version.
- Xoá comment debug, console.log, biến chết.
- Nếu vừa học gotcha mới → **viết vào `CLAUDE.md` ngay**. Mỗi session mới là tabula rasa.

Script bump version one-liner (PowerShell, dùng UTF-8 đúng cách):
```powershell
py -c "import re,glob; [open(f,'w',encoding='utf-8').write(re.sub(r'\?v=\d+','?v=20',open(f,encoding='utf-8').read())) for f in ['index.html','admin_server.py','_rebuild_projects.py']+glob.glob('projects/*.html')]"
```
(Đổi `?v=20` thành số mới.)

---

## Pha 6 — Commit & deploy

- Dùng `py deploy.py` — wrapper an toàn (chạy check, hiện diff, hỏi message, commit với author đúng, push).
- Hoặc thủ công:
  ```bash
  git add -A
  git -c user.name="Hồ Tất Vương Đình" -c user.email="dinhhoo1230@gmail.com" commit -m "<message>"
  git push origin main
  ```
- Commit message phải cụ thể: `fix(project-03): cover lệch trên mobile` chứ không phải `fix bug`.
- Sau push, đợi GitHub Pages build ~1-2 phút.

---

## Pha 7 — Hậu kiểm production

- Mở https://dinhhoo1230-alt.github.io/vuongdinh.github.io/ check thật.
- Local pass ≠ production pass:
  - Linux server **case-sensitive**: ảnh `Cover.jpg` vs `cover.jpg` là 2 file khác. Windows local sẽ tha, Pages sẽ 404.
  - CDN cache có thể giữ phiên bản cũ vài phút.
- Check ít nhất 2 thứ trên production: trang vừa sửa + một trang ngẫu nhiên (để chắc không regress).

---

## Cái KHÔNG bao giờ làm

- Deploy mà chưa mở browser xem
- Bulk-edit 6 file rồi mới test
- Dùng PowerShell `Set-Content` cho file tiếng Việt
- Xoá ảnh project mà chưa confirm — không có Recycle Bin, mất là mất
- Skip `CLAUDE.md` vì "session trước nhớ rồi"
- Sửa output (HTML đã gen) khi root cause nằm ở generator
- Bump `?v=N` rồi mới test (test xong mới bump, để khỏi tưởng đã ok)
- Push mà chưa chạy `py check.py`

---

## Thứ tự ưu tiên khi nhiều việc đến cùng lúc

1. **Logic vỡ** (trang 404, JS error) — fix trước
2. **Encoding mojibake** — fix trước, lan rộng nhanh
3. **Layout vỡ trên 1 breakpoint** — fix tiếp theo
4. **Tinh chỉnh visual** (spacing, animation) — sau cùng
5. **Refactor** (clean code, tách hàm) — chỉ khi không có bug pending

**Đẹp sau khi đúng.** Animation, easing, micro-interaction chỉ thêm khi layout đã không vỡ ở mọi breakpoint.

---

## Liên quan

- `CLAUDE.md` — context tổng cho codebase
- `check.py` — script tự kiểm trước deploy
- `deploy.py` — wrapper deploy an toàn
- `_rebuild_projects.py` — regen toàn bộ 6 project HTML từ folder ảnh
- `admin_server.py` — local dev server + admin API
