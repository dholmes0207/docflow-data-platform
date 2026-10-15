# Task 0.0: Quy Trình Git & GitHub Với Repo DocFlow (Issue → Nhánh → Commit → Pull Request)

- **Giai đoạn:** Sprint 1 — Nền móng môi trường
- **Làm khi nào:** ngay sau khi Task 0.1 có Ubuntu (WSL2), `git` và repo đã clone về. Thứ tự Sprint 1: **0.1 → 0.0 → 0.2**.
  PR của Task 0.0 là PR đầu tiên của bạn; bài của Task 0.1 và 0.2 nộp ở các PR sau, theo đúng quy trình học ở đây.
- **Mục tiêu:** Suốt 7 tháng tới, mọi bài của bạn đi qua cùng một vòng: mở issue → tạo nhánh → commit → mở Pull Request
  → CI kiểm tra → mentor review → merge. Task này cho bạn đi trọn một vòng có chủ đích, kể cả những đoạn hay vấp
  (bị từ chối push, sửa commit sai quy ước, xử lý xung đột, dọn nhánh sau khi merge), để từ Sprint 2 bạn chỉ còn
  phải nghĩ về bài toán dữ liệu.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. **Kết nối GitHub từ WSL bằng SSH:** khóa SSH được tạo bên trong Ubuntu (không phải trên Windows) và đã thêm vào
   tài khoản GitHub; `ssh -T git@github.com` chào đúng tên tài khoản của bạn; `git remote -v` của repo dùng địa chỉ SSH.
   Email trong `git config user.email` là email bạn chấp nhận công khai (repo này public), tốt nhất là địa chỉ
   `noreply` của GitHub, và commit của bạn trên GitHub hiện đúng avatar tài khoản.
2. **Issue:** mở 1 issue cho Task 0.0 bằng mẫu **"Bắt đầu một task"**, tự assign cho mình, có checklist DoD.
   Tick dần các tiêu chí trong lúc làm.
3. **Nhánh:** tạo từ `main` mới nhất, tên đúng quy tắc trong `CONTRIBUTING.md` mục 2 (ví dụ `sprint-01/task-0.0-git-workflow`).
   Đã thử push thẳng lên `main` một lần (trên nhánh nháp, không phải nhánh bài làm), đọc được thông báo bị từ chối và giải thích vì sao.
4. **Commit:** ít nhất 3 commit nhỏ, mỗi commit một ý, message theo Conventional Commits. Đã cài hook bằng
   `pre-commit install` và thấy hook `commit-msg` chặn một message sai ngay trên máy.
5. **Nội dung PR:**
   - `docs/git_cheatsheet.md`: ít nhất 12 lệnh Git bạn **đã thực sự chạy** trong task này, mỗi lệnh 1 dòng giải thích
     bằng lời của bạn, và 1 mục "Lỗi đã gặp" (thông báo lỗi + cách xử lý).
   - Một mục "Xử lý xung đột" trong cheatsheet: bài tập xung đột ở DoD 6, gồm đoạn file còn dấu `<<<<<<<` / `=======` / `>>>>>>>`
     (dán nguyên văn) và các bước bạn đã làm.
   - `docs/learning_log.md` có mục Sprint 1; `roadmap/weekly_tracker.md` cập nhật trạng thái Task 0.0.
6. **Xung đột (trên máy, không push):** tự tạo 2 nhánh nháp cùng sửa một dòng của cùng một file, merge vào nhau,
   gặp conflict và tự giải quyết. Xóa 2 nhánh nháp sau khi xong.
7. **Pull Request:** điền đủ mẫu mô tả PR, có dòng `Closes #<số issue>`; CI xanh cả 4 check (check quy ước Git nằm trong `hygiene`).
   Nếu CI báo sai quy ước, tự sửa đến khi xanh.
8. **Vòng review:** mentor sẽ để lại ít nhất 1 góp ý. Bạn sửa bằng commit mới trên **cùng nhánh** (không mở PR mới),
   trả lời từng thread góp ý, rồi bấm **Re-request review**.
9. **Sau khi merge:** mentor merge bằng **squash merge**, issue tự đóng. Trên máy bạn: `main` đã đồng bộ, nhánh của task
   không còn ở local lẫn trên GitHub, và bạn giải thích được vì sao `git branch -d` báo nhánh "not fully merged"
   dù PR đã merge. Mentor kiểm tra tiêu chí này ở PR kế tiếp của bạn.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Ba vùng của Git:** working tree, staging area (index) và repository. `git add` và `git commit` di chuyển thay đổi
  giữa các vùng nào? Commit là "ảnh chụp" toàn bộ dự án hay chỉ là phần thay đổi?
- **Nhánh là gì:** một con trỏ nhẹ trỏ vào một commit. Vì sao tạo nhánh trong Git gần như không tốn gì?
- **Local và remote:** `origin`, `origin/main` và `main` trên máy bạn là 3 thứ khác nhau. `fetch` và `pull` khác nhau ở đâu?
- **GitHub Flow:** `main` luôn ở trạng thái chạy được; mọi thay đổi đi qua nhánh ngắn hạn và Pull Request. Repo này dùng
  ruleset để **bắt buộc** điều đó: không ai push thẳng vào `main`, PR cần CI xanh và mentor duyệt.
- **Issue ↔ nhánh ↔ commit ↔ PR:** chuỗi truy vết giúp 6 tháng sau vẫn trả lời được "dòng code này sinh ra vì yêu cầu nào".
  Từ khóa `Closes #N` trong mô tả PR nối PR với issue.
- **Conventional Commits:** quy ước `<loại>(<phạm vi>): <mô tả>`. Lợi ích là gì khi đọc lịch sử, khi sinh changelog?
- **Ba kiểu merge trên GitHub:** merge commit, squash and merge, rebase and merge. Repo này squash PR của bạn: cả PR thành
  **một** commit trên `main`, tiêu đề PR thành message của commit đó. Hệ quả với nhánh trên máy bạn là gì?
- **Xác thực với GitHub:** SSH key và HTTPS + token khác nhau thế nào? Vì sao khóa SSH nên tạo bên trong WSL thay vì dùng chung với Windows?
- **Kết thúc dòng (line ending):** Windows dùng CRLF, Linux dùng LF. File `.gitattributes` của repo quy định gì, và vì sao
  làm việc hoàn toàn trong WSL tránh được cả một nhóm lỗi?

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `pro git book branching basic branching and merging` (sách Pro Git miễn phí, chương 2–3)
- `github flow`
- `conventional commits specification 1.0.0`
- `generating a new ssh key and adding it to the ssh-agent github linux`
- `github setting your commit email address noreply`
- `linking a pull request to an issue using a keyword`
- `about merge methods on github squash`
- `resolving a merge conflict using the command line`
- `git commit amend` và `git rebase interactive reword`
- `git push force-with-lease vs force`
- `pre-commit commit-msg hook`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Repo này công khai. Nếu bạn lỡ commit file `.env` có mật khẩu và đã push lên nhánh, thì xóa file ở commit tiếp theo đã đủ chưa? Phải làm thêm những gì?*
- *Sau khi PR được squash merge, vì sao các commit trên nhánh của bạn không xuất hiện trong lịch sử `main`, và vì sao Git trên máy bạn "nghĩ" nhánh đó chưa được merge?*
- *Vì sao nên bắt đầu mỗi task bằng một nhánh mới tạo từ `main` vừa cập nhật, thay vì làm tiếp trên nhánh của task trước?*
- *`git push --force` và `git push --force-with-lease` khác nhau thế nào? Khi nào bạn được phép dùng, trên nhánh nào thì tuyệt đối không?*
- *Một commit tên `update` với một commit tên `fix(minio): tăng timeout khi tải file lớn`: 3 tháng sau, cái nào giúp bạn tìm ra nguyên nhân lỗi nhanh hơn, và vì sao?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Một Vòng Làm Việc (áp dụng cho mọi task từ nay)
1. **Issue:** tab Issues → New issue → mẫu "Bắt đầu một task". Ghi lại số issue (ví dụ `#3`).
2. **Nhánh:** đứng ở `main`, kéo bản mới nhất về, rồi tạo và chuyển sang nhánh mới (tra `git switch -c`).
   Kiểm tra tên trước khi push: `python3 scripts/check_git_conventions.py --branch "$(git branch --show-current)"`.
3. **Commit:** `git status` → `git add <file cụ thể>` (hạn chế `git add .`) → `git commit`. Mỗi commit một ý.
4. **Push lần đầu** cần tạo nhánh trên GitHub và nối nhánh local với nó (tra `git push -u`).
5. **PR:** GitHub hiện nút "Compare & pull request" sau khi push. Đặt tiêu đề theo Conventional Commits, điền mẫu, thêm `Closes #<số issue>`.
6. **CI:** tab Checks của PR. Đỏ thì bấm vào job, đọc dòng lỗi: thông báo nói rõ sai ở đâu và sửa thế nào.
7. **Review:** sửa theo góp ý → commit → push lên cùng nhánh (PR tự cập nhật) → trả lời thread → Re-request review.
8. **Sau merge:** về `main`, kéo bản mới, xóa nhánh cũ, dọn tham chiếu tới nhánh remote đã bị xóa (tra `git fetch --prune`).

### 2. SSH Và Email
- Tạo khóa loại `ed25519` bằng `ssh-keygen` **trong Ubuntu**, thêm khóa công khai (file `.pub`, không phải file còn lại)
  vào GitHub → Settings → SSH and GPG keys.
- Repo đã clone bằng HTTPS ở Task 0.1 thì đổi địa chỉ `origin` sang dạng SSH (tra `git remote set-url`).
- Email: GitHub → Settings → Emails → bật "Keep my email addresses private" để lấy địa chỉ dạng
  `...@users.noreply.github.com`, rồi đặt vào `git config --global user.email`. Commit cũ không tự đổi email.

### 3. Thử Bị Từ Chối Push Thẳng `main`
Tạo một nhánh nháp từ `main`, commit một thay đổi vô hại, thử đẩy commit đó lên `main` của GitHub (tra cú pháp
`git push origin <nhánh-local>:main`). GitHub sẽ từ chối với thông báo về **repository rule**. Chép thông báo vào cheatsheet,
rồi xóa nhánh nháp. Không cần, và không được, tìm cách vượt qua.

### 4. Bài Tập Xung Đột (chỉ trên máy)
- Từ `main`, tạo nhánh nháp A, sửa dòng thứ nhất của một file ghi chú của bạn (ví dụ `docs/learning_log.md`), commit.
- Quay lại `main`, tạo nhánh nháp B, sửa **cùng dòng đó** theo cách khác, commit.
- Đứng ở B, merge A vào. Git dừng lại và đánh dấu xung đột. Mở file trong VS Code, đọc 3 vùng đánh dấu, quyết định nội dung cuối,
  xóa dấu, rồi hoàn tất merge (tra `git add` + `git commit` sau conflict, hoặc `git merge --abort` nếu muốn làm lại).
- VS Code có giao diện "Accept Current / Incoming / Both", nhưng hãy làm lần đầu bằng tay để hiểu các dấu.

### 5. Sửa Commit Sai Quy Ước
- **Chưa push:** sửa message của commit mới nhất (tra `git commit --amend`).
- **Đã push, và nằm trên nhánh của bạn:** sửa lại message các commit cũ (tra `git rebase -i` với lệnh `reword`), rồi push đè
  bằng `--force-with-lease`. Chỉ làm trên nhánh của chính bạn, không bao giờ trên `main`.
- **Tiêu đề PR sai:** sửa trực tiếp trên GitHub (nút Edit cạnh tiêu đề). CI tự chạy lại khi bạn sửa tiêu đề hoặc mô tả PR.

### 6. Những Vấn Đề Thường Gặp
- **`Permission denied (publickey)`:** khóa chưa được thêm vào GitHub, thêm nhầm file, hoặc đang dùng khóa của Windows.
  Chạy `ssh -T git@github.com` với cờ `-v` để xem SSH đang thử khóa nào.
- **`push declined due to repository rule violations`:** bạn đang push vào `main`. Đúng như thiết kế. Push lên nhánh của bạn.
- **`Updates were rejected because the tip of your current branch is behind`:** nhánh trên GitHub có commit mà máy bạn chưa có
  (ví dụ bạn bấm "Update branch" trên GitHub). Kéo về trước, rồi push lại. Đừng dùng `--force` để "cho qua".
- **Hook `commit message` báo Failed:** commit chưa được tạo. Viết lại message cho đúng dạng rồi commit lại.
- **`hook commit-msg` không chạy:** bạn chưa chạy `pre-commit install` trong thư mục repo, hoặc chạy trước khi repo có cấu hình hook commit-msg. Chạy lại lệnh đó.
- **CI đỏ ở bước "Quy ước Git":** đọc từng dòng lỗi (tên nhánh / tiêu đề / commit / thiếu `Closes #`). Tên nhánh sai mà PR đã mở thì
  cách chắc chắn nhất là: đổi tên nhánh ở local, push nhánh tên mới, mở PR mới, đóng PR cũ kèm một dòng giải thích.
- **`git branch -d` báo `not fully merged` sau khi PR đã merge:** do squash merge tạo commit mới trên `main`. Kiểm tra lại PR đã
  merged trên GitHub, rồi mới xóa bằng cờ xóa cưỡng bức. Tự giải thích hiện tượng này trong cheatsheet.

</details>
