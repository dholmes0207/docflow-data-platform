# Task 0.5: Xây Dựng Bộ Dữ Liệu Thử Nghiệm & Các Trường Hợp Biên (Mock Data & Edge Cases)

- **Giai đoạn:** Tuần 2 — Hạ tầng & Mô hình dữ liệu
- **Mục tiêu:** Hiểu tầm quan trọng của việc chuẩn bị dữ liệu kiểm thử (Test Data) trong Data Engineering; tự tay tạo bộ tài liệu giả lập cho 2 doanh nghiệp kèm các "bẫy" có chủ đích để kiểm tra độ tin cậy của pipeline xử lý sau này.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Bạn đã chuẩn bị được bộ dữ liệu giả lập đại diện cho ít nhất 2 doanh nghiệp thuộc hai lĩnh vực khác nhau (ví dụ: một công ty bán lẻ và một công ty công nghệ), mỗi công ty có từ 2–3 tài liệu nội bộ dạng văn bản (`.txt` hoặc `.md`).
2. Có chủ đích tạo ra ít nhất 2 trường hợp kiểm thử đặc biệt (Edge Cases):
   - Một tài liệu rỗng (kích thước 0 bytes) để kiểm tra xem hệ thống có phát hiện và chặn dữ liệu lỗi hay không.
   - Một tài liệu có 2 phiên bản (nội dung sửa đổi) để phục vụ việc kiểm tra tính năng cập nhật phiên bản (Versioning & Idempotency).
3. Tải (upload) thành công toàn bộ dữ liệu này lên bucket `raw-documents` trên MinIO, tổ chức theo cấu trúc tiền tố đường dẫn (Object Key Prefix) phân biệt rõ ràng giữa các doanh nghiệp.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Test Data Design trong Data Engineering:** Tại sao một kỹ sư dữ liệu giỏi luôn thiết kế dữ liệu kiểm thử có "bẫy" trước khi viết code xử lý? Nếu chỉ test với dữ liệu hoàn hảo (happy path), điều gì sẽ xảy ra khi hệ thống vận hành thực tế?
- **Khái niệm "Thư mục" trong Object Storage (S3 / MinIO):** Trong MinIO hoặc AWS S3, thực chất không có khái niệm cây thư mục vật lý như trên ổ đĩa máy tính. Tất cả chỉ là các chuỗi ký tự gọi là **Object Key** (ví dụ: `tenant_retail/chinh_sach.md`). Cơ chế này giúp ích gì cho việc phân chia vùng dữ liệu của từng khách hàng?
- **Data Quality & Schema Validation:** Khi một file hỏng hoặc file rỗng đi vào pipeline, hệ thống nên phản ứng thế nào? Dừng toàn bộ pipeline hay ghi nhận log lỗi và tiếp tục xử lý các file hợp lệ khác?

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `data quality testing edge cases in data pipelines`
- `s3 key naming best practices folder structure multi tenant`
- `handling empty or corrupted files in data ingestion`
- `synthetic data generation for rag testing`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Nếu hai công ty khác nhau cùng có một file tên là `noi_quy.txt`, làm sao để hệ thống lưu trữ trên MinIO và Database không bao giờ ghi đè dữ liệu của nhau?*
- *Để kiểm tra tính năng "Cách ly doanh nghiệp (Tenant Isolation)", bạn sẽ thiết kế câu hỏi thử nghiệm như thế nào? (Gợi ý: Một câu hỏi chỉ có trong tài liệu của công ty A nhưng mang sang hỏi với tư cách là nhân viên công ty B).*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Gợi Ý Cấu Trúc Thư Mục Dữ Liệu
Bạn có thể tự do sáng tạo nội dung văn bản liên quan đến các chủ đề gần gũi (nhân sự, chính sách, hướng dẫn kỹ thuật), tổ chức thành các thư mục con trong thư mục `sample_data/` của dự án:
- **Nhóm 1: Doanh nghiệp bán lẻ (`tenant_retail`)**
  - Tài liệu chính sách đổi trả hàng hóa (nêu rõ các mốc ngày, điều kiện).
  - Tài liệu quy chế hoa hồng bán hàng (nêu các mức doanh số và tỷ lệ %).
  - Một file rỗng (0 bytes) để làm dữ liệu bẫy.
- **Nhóm 2: Doanh nghiệp công nghệ phần mềm (`tenant_tech`)**
  - Tài liệu hướng dẫn onboarding cho lập trình viên mới (quy trình Git, quy định giờ làm việc).
  - Quy định an toàn bảo mật thông tin và sử dụng công cụ AI.

*(Bạn có thể tham khảo một số nội dung văn bản mẫu có sẵn trong thư mục [`sample_data/`](../../sample_data/) của repo để lấy ý tưởng).*

### 2. Thao Tác Đưa Dữ Liệu Lên MinIO
- Mở MinIO Console trên trình duyệt (`http://localhost:9001`).
- Đăng nhập vào bucket `raw-documents`.
- Sử dụng tính năng tạo folder trên MinIO UI để tạo 2 folder tương ứng: `tenant_retail/` và `tenant_tech/`.
- Tải các file văn bản tương ứng vào từng thư mục.
- Kiểm tra danh sách đường dẫn hiển thị trên MinIO để đảm bảo tên tenant luôn nằm ở đầu đường dẫn file (ví dụ: `tenant_retail/quy_che_doi_tra.md`).

### 3. Chuẩn Bị Câu Hỏi Kiểm Thử Nghiệp Vụ (Ground Truth Questions)
Sau khi có dữ liệu, hãy ghi chú lại khoảng 3–5 câu hỏi kèm đáp án mong muốn để sau này dùng cho task kiểm thử tìm kiếm ở Tuần 7:
- *Ví dụ 1 (Câu hỏi bình thường):* "Khách hàng được đổi trả sản phẩm trong bao nhiêu ngày?" -> Kỳ vọng tìm thấy đoạn văn trong file của `tenant_retail`.
- *Ví dụ 2 (Câu hỏi bẫy rò rỉ dữ liệu):* Đứng ở quyền `tenant_tech` và hỏi: "Tỷ lệ hoa hồng doanh số trên 100 triệu là bao nhiêu?" -> Kỳ vọng hệ thống trả về: *Không tìm thấy thông tin* (bởi vì thông tin này chỉ thuộc về `tenant_retail`).

</details>
