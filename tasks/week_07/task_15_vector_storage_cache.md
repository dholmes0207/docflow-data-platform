# Task 2.2: Lưu Vector Vào pgvector & Bộ Nhớ Đệm Embedding Theo Mã Băm Chunk

- **Giai đoạn:** Sprint 7 — Vector embedding & lưu trữ pgvector
- **Mục tiêu:** Điền vector của Task 2.1 vào cột `embedding` của các chunk đã ghi ở Sprint 6, và **không bao giờ tính lại** embedding cho một đoạn văn đã tính rồi. Khi tài liệu được sửa (phiên bản mới ở Task 1.6), phần lớn chunk thường giữ nguyên nội dung. Hệ thống tốt chỉ tính embedding cho phần thực sự thay đổi.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Có **migration có đánh số** (tiếp nối Task 1.6) bổ sung những gì cần cho bộ nhớ đệm, tối thiểu gồm:
   - **mã băm nội dung của từng chunk**;
   - **tên + phiên bản mô hình** đã tạo ra vector.

   Bạn tự chọn thiết kế: thêm cột vào `document_chunks`, hay tạo bảng cache riêng. Giải thích lựa chọn trong `docs/embedding.md`.
2. Có bước "điền embedding": tìm các chunk chưa có vector, tính theo lô, ghi theo lô, chạy bằng role `docflow_app` (Task 1.5).
3. **Khóa của bộ nhớ đệm gồm cả mã băm nội dung lẫn mô hình.** Có test chứng minh:
   - **chạy lại** bước điền embedding lần 2 → **0** lần gọi mô hình (đếm số lần gọi trên bản giả của Task 2.1);
   - **sửa tài liệu** bằng bản trong `sample_data/updates/` → số lần gọi mô hình **bằng đúng số chunk có nội dung mới**, không phải toàn bộ chunk của tài liệu;
   - **đổi mô hình** (hoặc đổi phiên bản mô hình) trong cấu hình → vector cũ **không** bị dùng lại.
4. Trước khi ghi, code kiểm tra số chiều vector của mô hình khớp với cột trong database. Không khớp thì dừng ngay với thông báo rõ ràng, không ghi một nửa rồi mới lỗi.
5. Chạy thật trên corpus với mô hình thật. Mọi chunk của phiên bản đang hiệu lực đều có vector. Dán vào mô tả PR: số chunk đã tính, số chunk lấy từ bộ nhớ đệm, thời gian chạy lần 1 và lần 2.
6. Thử 3 câu hỏi trong bộ câu hỏi của Task 0.6 bằng một câu SQL tìm 5 chunk gần nhất (toán tử cosine `<=>`, **lọc theo đúng tenant**), dán kết quả vào PR. Chỉ cần quan sát, chưa cần đo điểm: việc đo điểm là của Sprint 8.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Content-addressable cache:** Dùng *chính nội dung* (qua mã băm) làm khóa. Hai chunk có nội dung giống hệt nhau, dù thuộc 2 phiên bản khác nhau của cùng tài liệu, thì dùng chung một vector.
- **Vì sao khóa phải gồm cả mô hình:** Cùng một đoạn văn, hai mô hình khác nhau (hoặc hai phiên bản của cùng mô hình) cho ra hai vector **không so sánh được với nhau**. Trộn chúng trong cùng một lần tìm kiếm sẽ cho kết quả vô nghĩa mà không báo lỗi.
- **Ghi theo lô và chi phí index:** Mỗi lần ghi vector vào bảng có index HNSW, database phải cập nhật cả index. Ghi từng dòng một và ghi theo lô khác nhau thế nào?
- **Toán tử khoảng cách của pgvector:** `<->` (Euclid), `<#>` (tích vô hướng âm), `<=>` (cosine). Index HNSW được tạo với `vector_cosine_ops` (Task 0.4) chỉ giúp tăng tốc cho toán tử tương ứng.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `content addressable storage hash as key`
- `embedding cache invalidation model version`
- `pgvector insert update vector python psycopg`
- `pgvector distance operators cosine inner product`
- `postgresql explain analyze index scan hnsw`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Hai tenant khác nhau có một đoạn văn giống hệt nhau (ví dụ câu chào chuẩn trong hợp đồng). Dùng chung một vector từ bộ nhớ đệm cho cả hai có làm lộ dữ liệu giữa các tenant không? Nếu bộ nhớ đệm là một bảng riêng không có `tenant_id`, Row Level Security ở Sprint 12 sẽ áp lên nó thế nào?*
- *Chạy câu SQL tìm 5 chunk gần nhất với `EXPLAIN`, database có dùng index HNSW không? Nếu không, vì sao? (Gợi ý: bảng còn quá ít dòng.)*
- *Khi đổi sang mô hình mới, bạn phải tính lại vector cho toàn bộ corpus. Làm sao để trong lúc đang tính lại, hệ thống tìm kiếm vẫn chạy được bằng vector cũ?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Chọn thiết kế cache** và viết migration. Nếu thêm cột mã băm vào bảng chunk, nhớ điền giá trị cho các chunk đã có từ Sprint 6.
2. **Tính mã băm chunk** bằng đúng cách của Task 1.4, trên nội dung chunk đã làm sạch.
3. **Bước điền embedding:**
   - lấy danh sách chunk chưa có vector;
   - với mỗi mã băm, tra bộ nhớ đệm theo cặp (mã băm, mô hình);
   - chỉ gửi những mã băm **chưa có** cho mô hình;
   - ghi tất cả theo lô.
4. **Viết test bằng bản giả có bộ đếm** số lần được gọi, đi qua 3 kịch bản của DoD 3.
5. **Chạy thật**, rồi thử truy vấn tìm kiếm theo tenant.

### 2. Những Vấn Đề Thường Gặp
- **`expected 384 dimensions, not 768`:** Mô hình bạn đang dùng không phải mô hình 384 chiều, hoặc cấu hình trỏ nhầm mô hình. Đây chính là tình huống DoD 4 muốn bắt sớm.
- **Lỗi kiểu dữ liệu khi truyền vector từ Python sang PostgreSQL:** Tìm hiểu gói hỗ trợ `pgvector` cho Python (đăng ký kiểu `vector` với psycopg), hoặc cách truyền vector dưới dạng chuỗi.
- **Lần chạy thứ 2 vẫn gọi mô hình:** Mã băm chunk không ổn định giữa 2 lần chạy (xem lại tính tất định của Task 1.2 và 1.3), hoặc khóa tra cứu đang gồm cả thứ không nên gồm (ví dụ `chunk_id`).
- **Bước điền embedding bị `permission denied`:** `docflow_app` chưa có quyền trên cột / bảng mới tạo trong migration. Xem lại `ALTER DEFAULT PRIVILEGES` (Task 1.5).

</details>
