# Task 1.1: Python Client Kết Nối MinIO & Quét File Theo Tenant

- **Giai đoạn:** Sprint 4 — Trích xuất & làm sạch văn bản
- **Mục tiêu:** Viết bước đầu tiên của pipeline: kết nối vào MinIO, quét bucket `raw-documents` và trả về danh sách tài liệu cần xử lý. Mỗi tài liệu gắn đúng `tenant_id` và các file không hợp lệ được loại ra một cách có kiểm soát.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Module kết nối MinIO lấy địa chỉ và khóa truy cập từ module cấu hình của Task 1.0, không ghi cứng trong code.
2. Có hàm liệt kê tài liệu trong bucket `raw-documents`, có thể lọc theo tenant. Mỗi phần tử trả về có ít nhất: `tenant_id`, object key, kích thước, thời điểm sửa đổi cuối (hoặc ETag).
3. `tenant_id` được tách từ **object key** theo quy ước `<tenant_id>/<tên file>`. Các key sai quy ước bị loại ra và ghi log `WARNING` nêu rõ key và lý do, ví dụ: file nằm ngay gốc bucket, hoặc tenant không có trong danh sách cho phép.
4. File rỗng (0 byte) và file có đuôi chưa hỗ trợ (ngoài `.txt`, `.md`) bị bỏ qua có ghi log. **Một file lỗi không làm dừng cả lần quét.**
5. Phần logic tách tenant, lọc đuôi file, lọc file rỗng có **unit test chạy không cần MinIO thật**, và check `unit` trên CI xanh.
6. Có bằng chứng chạy thật với cụm Docker Compose của Task 0.3, ví dụ output log dán trong mô tả PR: liệt kê đúng toàn bộ tài liệu của Task 0.5 và 0.6, đồng thời loại đúng file rỗng.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **S3 API:** MinIO nói "cùng ngôn ngữ" với AWS S3. Có thể dùng thư viện `minio` (SDK riêng của MinIO) hoặc `boto3` (SDK của AWS). So sánh ưu nhược điểm: nếu sau này chuyển sang AWS S3 thật thì cái nào ít phải sửa code hơn?
- **Phân trang (pagination):** S3 không trả về một lúc hàng triệu object, mà trả theo từng trang (mặc định tối đa 1.000 object mỗi lần). Thư viện bạn chọn xử lý việc này thế nào?
- **Prefix & delimiter:** Cách S3 "giả lập" thư mục bằng tiền tố của key (đã gặp ở Task 0.5). Quét theo prefix `tenant_retail/` khác gì so với quét toàn bucket rồi lọc trong Python?
- **Tách I/O khỏi logic (testability):** Phần nói chuyện với mạng khó test; phần quyết định "file này hợp lệ không, thuộc tenant nào" là logic thuần, test dễ. Tách 2 phần này ra là chìa khóa của DoD 5.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `minio python sdk list_objects recursive`
- `boto3 s3 client endpoint_url minio`
- `s3 list objects pagination continuation token`
- `python dependency injection testing without network`
- `pytest fake vs mock`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Một file có key `tenant_tech/../tenant_retail/bao_cao.md` hoặc `Tenant_Retail/a.md` thì hệ thống nên xử lý thế nào? Vì sao không được "tin" bất kỳ key nào cũng hợp lệ?*
- *Vì sao `tenant_id` phải lấy từ vị trí lưu trữ (object key) mà không lấy từ nội dung bên trong file?*
- *Nếu bucket có 100.000 file và lần quét bị mất mạng ở file thứ 50.000, lần chạy lại nên bắt đầu từ đâu? (Gợi ý: Task 1.4 sẽ giải bài toán này bằng mã băm.)*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. Thêm thư viện S3 bạn chọn vào `pyproject.toml`. Thêm các biến MinIO (endpoint, access key, secret key, tên bucket) vào module cấu hình và `.env.example`.
2. Viết một hàm thuần nhận vào *thông tin một object* (key, kích thước) và trả về *quyết định*: hợp lệ kèm `tenant_id`, hoặc bị loại kèm lý do. Viết unit test cho hàm này trước, với đủ loại key hợp lệ và không hợp lệ.
3. Viết phần gọi MinIO: duyệt toàn bộ object (nhớ phân trang), đưa từng object qua hàm ở bước 2, ghi log các file bị loại.
4. Chạy thử với cụm Docker Compose, dán output vào PR.

### 2. Những Vấn Đề Thường Gặp
- **Kết nối vào cổng 9001 thay vì 9000:** 9001 là Web Console dành cho người dùng, code phải gọi cổng API 9000 (câu hỏi tư duy của Task 0.3).
- **Lỗi SSL / `wrong version number`:** MinIO chạy local dùng `http`, không phải `https`. Tìm tham số `secure` (thư viện `minio`) hoặc dùng `endpoint_url` bắt đầu bằng `http://` (thư viện `boto3`).
- **`SignatureDoesNotMatch` hoặc `AccessDenied`:** Sai access key / secret key, hoặc code đang đọc nhầm file `.env`. In ra (đã che bớt) giá trị cấu hình lúc khởi động để kiểm tra.
- **Code chạy trong container không thấy `localhost:9000`:** Bên trong mạng Docker Compose, các service gọi nhau bằng tên service (ví dụ `minio:9000`), không phải `localhost`.

</details>
