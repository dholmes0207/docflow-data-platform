# Task 0.5: Tạo Bộ Dữ Liệu Kiểm Thử Giả Lập (Mock Data & Edge Cases)

- **Giai đoạn:** Giai đoạn 0 — Khởi tạo nền tảng
- **Thời lượng ước tính:** 1 – 2 ngày (2 – 4 giờ làm việc)
- **Mục tiêu:** U chuẩn bị sẵn bộ tài liệu giả lập cho 2 doanh nghiệp (Tenant) với đầy đủ các tình huống dữ liệu chuẩn và các tình huống bẫy (edge cases: file rỗng, file trùng tên, file chỉnh sửa) để phục vụ việc kiểm thử pipeline tự động sau này.

---

## 🎯 Tiêu Chí Hoàn Thành (Definition of Done - DoD)
1. Thư mục `sample_data/` trong repo có đầy đủ các file tài liệu dạng `.txt` và `.md` được phân chia theo tenant.
2. Có ít nhất 1 file "bẫy" rỗng (0 bytes) để kiểm tra cơ chế Data Quality validation.
3. Có 1 cặp file minh họa việc cập nhật nội dung (phiên bản 1 và phiên bản 2) để kiểm thử cơ chế Idempotent & Versioning.
4. Đã tải (upload) thành công dữ liệu này lên bucket `raw-documents` trên MinIO theo đúng cấu trúc thư mục phân chia theo tenant.

---

## 🟢 MỨC 1: TỰ KHÁM PHÁ (U làm phần này trước)

### 1. Từ Khóa Tìm Kiếm (Search Keywords)
- `data engineering synthetic test data edge cases`
- `minio web console upload files and create folders`
- `s3 key prefix naming conventions multi-tenant`

### 2. Câu Hỏi Định Hướng Tư Duy
- *Trong Object Storage (S3 / MinIO), thực tế có khái niệm "thư mục" thật sự như trên ổ cứng máy tính không, hay chỉ là tiền tố tên file (Key Prefix)?*
- *Nếu một người dùng cố tình tải lên một file hoàn toàn rỗng, pipeline của Data Engineer nên ứng xử thế nào: báo lỗi dừng cả hệ thống hay ghi log cảnh báo và bỏ qua file đó?*
- *Làm sao để chắc chắn nhân viên công ty A không bao giờ nhìn thấy hoặc tìm kiếm ra tài liệu của công ty B?*

---

## 🟡 MỨC 2: HƯỚNG DẪN CHI TIẾT & PHAO CỨU SINH (Chỉ mở khi bị tắc)

<details>
<summary>👉 <b>Bấm vào đây để xem hướng dẫn chi tiết từng bước</b></summary>

### Bước 1: Tạo cấu trúc file trong thư mục `sample_data/`

#### 1. Tenant 1: Công ty Bán Lẻ (`tenant_retail`)
Tạo thư mục `sample_data/tenant_retail/`:
- **File 1:** `sample_data/tenant_retail/quy_che_doi_tra.md`
  ```markdown
  # CHÍNH SÁCH ĐỔI TRẢ HÀNG HÓA
  1. Thời hạn đổi trả: Khách hàng được đổi trả sản phẩm trong vòng 30 ngày kể từ ngày nhận hàng.
  2. Điều kiện sản phẩm: Hàng hóa còn nguyên tem mác, chưa qua sử dụng, có hóa đơn mua hàng.
  3. Chi phí vận chuyển: Miễn phí đổi trả nếu lỗi từ nhà sản xuất. Khách chịu phí 30.000 VNĐ nếu đổi theo nhu cầu cá nhân.
  ```
- **File 2:** `sample_data/tenant_retail/chinh_sach_hoa_hong.txt`
  ```text
  CHÍNH SÁCH HOA HỒNG NHÂN VIÊN KINH DOANH
  - Doanh số dưới 50 triệu/tháng: Hoa hồng 3%.
  - Doanh số từ 50 - 100 triệu/tháng: Hoa hồng 5%.
  - Doanh số trên 100 triệu/tháng: Hoa hồng 7% và thưởng nóng 2 triệu đồng.
  Tiền hoa hồng được thanh toán vào ngày 10 hàng tháng cùng lương cứng.
  ```
- **File 3 (File bẫy - File rỗng):** `sample_data/tenant_retail/empty_document.txt`
  *(Tạo file không có bất kỳ ký tự nào, dung lượng 0 bytes).*

#### 2. Tenant 2: Công ty Công Nghệ Phần Mềm (`tenant_tech`)
Tạo thư mục `sample_data/tenant_tech/`:
- **File 1:** `sample_data/tenant_tech/onboarding_developer.md`
  ```markdown
  # HƯỚNG DẪN ONBOARDING KỸ THUẬT CHO DEVELOPER MỚI
  1. Yêu cầu môi trường: Cài đặt Docker, Git, và cấu hình SSH key vào GitHub công ty.
  2. Quy trình làm việc: Mọi task đều phải tạo nhánh theo định dạng `feature/JIRA-ID`, tạo PR và cần ít nhất 2 approvals để merge vào nhánh main.
  3. Giờ làm việc: Core hours từ 09:30 đến 16:30. Có thể làm việc từ xa (Remote) 2 ngày/tuần sau thời gian thử việc.
  ```
- **File 2:** `sample_data/tenant_tech/chinh_sach_bao_mat.txt`
  ```text
  QUY ĐỊNH BẢO MẬT VÀ SỬ DỤNG DỮ LIỆU
  Tuyệt đối không đưa mã nguồn nội bộ hoặc dữ liệu khách hàng lên các công cụ AI công cộng nếu chưa được cấp phép.
  Mọi mật khẩu và API Key phải được lưu trữ trong HashiCorp Vault, cấm hardcode trong mã nguồn.
  Vi phạm quy định bảo mật có thể bị chấm dứt hợp đồng lao động ngay lập tức.
  ```

### Bước 2: Tải dữ liệu lên MinIO Console
1. Truy cập trình duyệt: `http://localhost:9001` (Đăng nhập: `minioadmin` / `minioadmin_secret`).
2. Nhấp vào bucket `raw-documents`.
3. Bấm **Create Folder** -> Đặt tên: `tenant_retail`.
4. Bấm vào thư mục `tenant_retail` vừa tạo -> Bấm **Upload** -> **Upload Files** -> Tải 3 file trong thư mục `sample_data/tenant_retail/` lên.
5. Tương tự, quay lại thư mục gốc của bucket, tạo folder `tenant_tech` và upload 2 file của công nghệ lên.

### Bước 3: Kiểm tra cấu trúc đường dẫn (Object Keys)
Đảm bảo trên MinIO hiển thị danh sách các object với đường dẫn chuẩn:
- `raw-documents/tenant_retail/quy_che_doi_tra.md`
- `raw-documents/tenant_retail/chinh_sach_hoa_hong.txt`
- `raw-documents/tenant_retail/empty_document.txt`
- `raw-documents/tenant_tech/onboarding_developer.md`
- `raw-documents/tenant_tech/chinh_sach_bao_mat.txt`

</details>
