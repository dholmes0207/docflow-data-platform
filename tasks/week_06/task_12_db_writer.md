# Task 1.5: Ghi Dữ Liệu Vào PostgreSQL & Tách Quyền Database (Least Privilege)

- **Giai đoạn:** Sprint 6 — Database writer & quản lý phiên bản
- **Mục tiêu:** Biến kế hoạch nạp của Task 1.4 thành dữ liệu thật trong PostgreSQL: tài liệu mới được ghi vào `documents`, các chunk của nó vào `document_chunks`, tất cả trong một transaction. Đồng thời, ứng dụng không còn chạy bằng tài khoản quản trị nữa mà chỉ có **đúng những quyền cần thiết**. Đây là nền móng để Row Level Security ở Sprint 12 thực sự có tác dụng.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Có kịch bản SQL (ví dụ `db/roles.sql`) tạo **2 role**:
   - `docflow_owner`: sở hữu các bảng, dùng để chạy schema và migration;
   - `docflow_app`: role mà ứng dụng đăng nhập hằng ngày. Role này **không** phải superuser, **không** sở hữu bảng nào, **không** có `BYPASSRLS`, và chỉ có quyền đọc/ghi dữ liệu trên đúng các bảng pipeline cần.

   Mật khẩu của 2 role **không** ghi cứng trong file SQL đã commit.
2. Ứng dụng kết nối bằng `docflow_app` (cấu hình qua `.env` / module cấu hình của Task 1.0). Có test chứng minh `docflow_app` **bị từ chối** khi:
   - xóa bảng (`DROP TABLE`);
   - sửa cấu trúc bảng (`ALTER TABLE`);
   - tạo bảng mới.
3. Có bản cài đặt PostgreSQL cho interface "trạng thái đã biết" của Task 1.4. **Hàm lập kế hoạch của Task 1.4 không bị sửa** (kiểm tra bằng `git diff`).
4. Thực thi kế hoạch cho hành động `NEW`: ghi 1 dòng `documents` (`version = 1`) cùng toàn bộ chunk của nó. Cột `embedding` tạm để trống (NULL), Sprint 7 sẽ điền. Mỗi tài liệu cùng các chunk của nó được ghi trong **một transaction**: lỗi xảy ra giữa chừng thì không để lại tài liệu "mồ côi" thiếu chunk. Có test cố tình gây lỗi giữa chừng và kiểm tra rollback.
5. Câu SQL dùng **tham số** (placeholder), không ghép chuỗi bằng f-string với dữ liệu đầu vào.
6. Chạy pipeline thật 2 lần liên tiếp trên corpus của Task 0.6: lần 2 **không ghi thêm dòng nào** (đếm số dòng 2 bảng trước và sau). Ghi lại thời gian chạy lần 1 trong mô tả PR.
7. Test tích hợp với PostgreSQL chạy được trong check CI **`unit`**. Job này có sẵn PostgreSQL + pgvector, kèm biến `DATABASE_URL` là tài khoản quản trị để test tự dựng schema và role.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Nguyên tắc đặc quyền tối thiểu (Principle of Least Privilege):** Mỗi thành phần chỉ được cấp đúng quyền nó cần. Nếu ứng dụng bị lỗi (hoặc bị tấn công SQL injection) mà đang chạy bằng superuser, thiệt hại tối đa là gì? Còn nếu chạy bằng `docflow_app`?
- **Superuser, chủ sở hữu bảng và RLS:** Trong PostgreSQL, superuser và chủ sở hữu bảng mặc định **không bị** Row Level Security chặn. Đây là lý do phải tách role ngay từ bây giờ.
- **Transaction & tính nguyên tử (atomicity):** "Tất cả hoặc không gì cả". Ghi tài liệu xong mà chưa ghi chunk thì pipeline bị tắt máy, chuyện gì xảy ra nếu không có transaction?
- **Truy vấn có tham số và SQL injection:** Vì sao `f"... WHERE tenant_id = '{tenant}'"` nguy hiểm, kể cả khi `tenant` lấy từ tên thư mục trên MinIO?
- **Ghi theo lô (batch):** Ghi từng dòng một và ghi cả lô (`executemany`, `COPY`) khác nhau thế nào về tốc độ?
- **Migration:** Thay đổi cấu trúc database phải được ghi lại thành file có thứ tự, chạy lại được, không sửa tay trên database.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `postgresql create role grant least privilege application user`
- `postgresql ALTER DEFAULT PRIVILEGES grant on future tables`
- `postgresql 15 public schema create privilege change`
- `psycopg 3 transactions context manager`
- `psycopg executemany vs copy performance`
- `sql injection parameterized query python`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Nếu `docflow_app` có quyền `DELETE` trên bảng `documents`, liệu có cần không? Thao tác nào của pipeline thật sự cần quyền đó?*
- *Pipeline bị tắt đột ngột sau khi ghi xong 50 trên 100 tài liệu. Chạy lại thì Task 1.4 sẽ quyết định gì với 50 tài liệu đã ghi và 50 tài liệu chưa ghi?*
- *Bạn đặt mật khẩu của `docflow_app` ở đâu để vừa không lộ lên Git, vừa dùng được ở máy bạn, trong CI và sau này trong Airflow?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Role trước, code sau.** Viết kịch bản tạo 2 role, chuyển quyền sở hữu bảng cho `docflow_owner`, cấp quyền tối thiểu cho `docflow_app`. Thử đăng nhập bằng `docflow_app` qua `psql` và tự tay thử những lệnh lẽ ra phải bị từ chối.
2. **Bản cài đặt PostgreSQL cho interface của Task 1.4:** chỉ cần một câu `SELECT` lấy mã băm và version của phiên bản đang hiệu lực, theo khóa `(tenant_id, file_path)`.
3. **Bộ ghi (writer):** một hàm nhận tài liệu cùng danh sách chunk, mở transaction, ghi `documents` trước để lấy `id`, rồi ghi chunk theo lô.
4. **Fixture test:** dùng `DATABASE_URL` (quyền quản trị) để tạo một database tạm, chạy `db/schema.sql` và `db/roles.sql`, rồi mở kết nối **bằng `docflow_app`** để chạy test. Có thể tham khảo cách `tests/gates/conftest.py` tạo database tạm.
5. Chạy thật với cụm Docker Compose 2 lần, đếm số dòng, ghi thời gian.

### 2. Những Vấn Đề Thường Gặp
- **`permission denied for sequence ...` khi INSERT:** Cột `id` tự tăng dùng một sequence (hoặc identity) riêng; `docflow_app` cần quyền dùng nó, không chỉ quyền trên bảng.
- **Cấp quyền xong, tạo bảng mới thì `docflow_app` lại không có quyền:** `GRANT` chỉ áp dụng cho bảng *đã có*. Tìm hiểu `ALTER DEFAULT PRIVILEGES`.
- **`must be owner of table`:** Bạn đang chạy lệnh đổi cấu trúc bảng bằng role không sở hữu bảng. Migration phải chạy bằng `docflow_owner`.
- **Dữ liệu không được lưu dù không báo lỗi:** psycopg 3 mặc định mở transaction và **không tự commit**. Kiểm tra lại cách bạn dùng `with conn.transaction():` hoặc `conn.commit()`.
- **Test chạy được ở máy nhưng đỏ trên CI:** CI dùng database trống, không có schema nào. Test phải tự dựng schema và role của nó, không dựa vào database có sẵn trên máy bạn.

</details>
