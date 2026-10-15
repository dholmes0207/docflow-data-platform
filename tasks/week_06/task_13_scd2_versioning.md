# Task 1.6: Quản Lý Phiên Bản Tài Liệu Theo SCD Type 2

- **Giai đoạn:** Sprint 6 — Database writer & quản lý phiên bản
- **Mục tiêu:** Khi một tài liệu bị sửa (hành động `CHANGED` của Task 1.4), không ghi đè lên bản cũ. Hãy **đóng** phiên bản cũ và **mở** phiên bản mới, lưu lại khoảng thời gian mỗi phiên bản có hiệu lực. Nhờ vậy hệ thống luôn trả lời được câu hỏi: *"Vào ngày X, quy chế đổi trả của công ty A ghi gì?"*

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Có **file migration có đánh số** (ví dụ `db/migrations/002_scd2_validity.sql`) thêm 2 cột `valid_from` và `valid_to` (kiểu thời gian có múi giờ) vào bảng `documents`.
   - Dữ liệu cũ được điền giá trị hợp lý (backfill).
   - Có cơ chế ghi nhận migration nào đã chạy, để chạy lại **không lỗi và không chạy lặp**.
   - Không sửa trực tiếp `db/schema.sql` của Task 0.4.
2. Chính database bảo đảm **2 quy tắc**:
   - `valid_to` để trống khi và chỉ khi phiên bản đang hiệu lực (`is_active`);
   - `valid_to` luôn lớn hơn `valid_from`.

   Có test cố tình ghi sai và bị database từ chối.
3. Thực thi hành động `CHANGED` trong **một transaction**: đóng phiên bản cũ (`is_active = FALSE`, `valid_to` = thời điểm thay đổi), mở phiên bản mới (`version` + 1, `valid_from` = cùng thời điểm đó), ghi chunk của phiên bản mới. Hai mốc thời gian **khớp nhau tuyệt đối**: không có khoảng hở, không chồng lấn.
4. Có hàm truy vấn **"as-of"**: cho `tenant_id`, đường dẫn tài liệu và một thời điểm T, trả về phiên bản có hiệu lực tại T. Có test với tài liệu 2 phiên bản trong `sample_data/updates/`:
   - T trước lúc sửa → phiên bản 1;
   - T sau lúc sửa → phiên bản 2;
   - T đúng bằng thời điểm sửa → phiên bản 2.
5. Truy vấn lấy chunk phục vụ tìm kiếm (chuẩn bị cho Sprint 8) **chỉ trả chunk của phiên bản đang hiệu lực**. Chunk của phiên bản cũ vẫn được giữ lại làm lịch sử.
6. Có test **2 tiến trình cùng xử lý `CHANGED` cho một tài liệu cùng lúc** (dùng 2 kết nối riêng): đúng 1 tiến trình thành công. Tiến trình còn lại bị một ràng buộc duy nhất (`UNIQUE`) trong schema của Task 0.4 chặn lại (tự quan sát xem là ràng buộc nào) và được xử lý êm: rollback, ghi log `WARNING`, không làm sập pipeline.
7. Chạy thật end-to-end:
   - Lần 1: mọi tài liệu `NEW`.
   - Thay `tenant_retail/quy_che_doi_tra.md` bằng bản trong `sample_data/updates/` rồi chạy lần 2: database có đúng 2 dòng cho file đó, đúng 1 dòng đang hiệu lực.

   Dán kết quả truy vấn vào mô tả PR.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Slowly Changing Dimension (SCD):** Các cách xử lý dữ liệu thay đổi theo thời gian.
  - Type 1: ghi đè, mất lịch sử.
  - Type 2: thêm dòng mới, giữ lịch sử kèm khoảng hiệu lực.
  - Type 3: thêm cột "giá trị trước đó".

  Vì sao trợ lý AI nội bộ cần Type 2? Ví dụ một nhân viên khiếu nại "hôm trước hệ thống trả lời 30 ngày".
- **Khoảng nửa mở `[valid_from, valid_to)`:** Phiên bản có hiệu lực từ `valid_from` (tính cả mốc này) cho tới trước `valid_to` (không tính mốc này). Vì sao cách này tránh được việc một thời điểm thuộc về 2 phiên bản cùng lúc?
- **Thời gian trong transaction:** Trong PostgreSQL, `now()` trả về **cùng một giá trị** suốt cả transaction. Tính chất này giúp gì cho DoD 3?
- **Migration có đánh số:** Database cũng có "phiên bản" giống code. Mỗi thay đổi cấu trúc là một file được chạy đúng một lần, theo đúng thứ tự, ở mọi môi trường (máy bạn, CI, sau này là Airflow).
- **Tranh chấp đồng thời (race condition):** Hai tiến trình cùng đọc "phiên bản đang hiệu lực là 1", cùng quyết định tạo phiên bản 2. Lớp nào chặn được việc này: code Python, hay ràng buộc trong database?

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `slowly changing dimension type 2 explained`
- `scd2 valid_from valid_to half open interval`
- `postgresql now() transaction timestamp vs clock_timestamp`
- `postgresql check constraint multiple columns`
- `database migrations versioning plain sql vs alembic`
- `postgresql unique violation concurrent insert handling`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Một file bị **xóa** khỏi MinIO (câu hỏi của Task 1.4). Với SCD Type 2, việc "đóng" phiên bản cuối cùng mà không mở phiên bản mới có hợp lý không? Khi đó truy vấn "as-of" trả về gì?*
- *Nếu `valid_to` của bản cũ lấy giờ trên máy chạy pipeline, còn `valid_from` của bản mới lấy giờ của database, chuyện gì có thể xảy ra?*
- *Giữ lại chunk của các phiên bản cũ thì dung lượng tăng dần theo thời gian. Khi nào nên dọn, và dọn thế nào mà không phá truy vấn "as-of"? (Liên quan Task 6.3 tùy chọn.)*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Chọn cách chạy migration:** một bảng nhỏ ghi lại tên các file đã chạy, cộng một script chạy lần lượt các file chưa có trong bảng; hoặc dùng công cụ có sẵn (tìm hiểu Alembic). Migration chạy bằng role `docflow_owner` của Task 1.5.
2. **Viết migration:** thêm cột, điền dữ liệu cũ (`valid_from` lấy từ thời điểm tạo dòng, `valid_to` để trống cho phiên bản đang hiệu lực), rồi mới thêm ràng buộc. Thêm ràng buộc trước khi điền dữ liệu sẽ bị lỗi với dữ liệu cũ.
3. **Thực thi `CHANGED`:** trong một transaction, **đóng bản cũ trước, mở bản mới sau**. Làm ngược thứ tự sẽ vi phạm ràng buộc "chỉ 1 phiên bản hiệu lực".
4. **Truy vấn as-of:** viết điều kiện theo khoảng nửa mở; nhớ trường hợp `valid_to` đang trống (phiên bản hiện tại).
5. **Test tranh chấp:** mở 2 kết nối, cả hai bắt đầu transaction và cùng đóng/mở phiên bản cho cùng một file; commit lần lượt. Quan sát lỗi mà kết nối thứ hai nhận được, rồi viết code xử lý lỗi đó.

### 2. Những Vấn Đề Thường Gặp
- **Test tranh chấp bị treo (không chạy tiếp):** Kết nối thứ hai đang **chờ khóa dòng** mà kết nối thứ nhất giữ. Đó là hành vi đúng của PostgreSQL. Hãy commit kết nối thứ nhất trước rồi mới chờ kết quả của kết nối thứ hai, hoặc tìm hiểu `lock_timeout`.
- **`valid_to` của bản cũ và `valid_from` của bản mới lệch nhau vài mili giây:** Bạn đang lấy giờ ở 2 thời điểm khác nhau. Xem lại khái niệm thời gian trong transaction.
- **Migration chạy lần 2 báo `column already exists`:** Cơ chế ghi nhận migration đã chạy chưa hoạt động, hoặc file migration chưa viết theo kiểu chạy lại được.

</details>
