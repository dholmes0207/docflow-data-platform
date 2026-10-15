# Task 1.4: Nạp Dữ Liệu Bất Biến (Idempotent) Bằng Mã Băm SHA-256

- **Giai đoạn:** Sprint 5 — Semantic chunking & nạp dữ liệu không trùng lặp
- **Mục tiêu:** Pipeline sẽ chạy đi chạy lại nhiều lần: theo lịch hằng đêm, khi bị lỗi giữa chừng, khi bạn sửa code. Task này xây "bộ não" quyết định cho mỗi tài liệu: **mới** (cần nạp), **không đổi** (bỏ qua) hay **đã sửa** (cần tạo phiên bản mới). Nhờ vậy, chạy bao nhiêu lần thì kết quả trong database vẫn như chạy một lần. Phần ghi thật vào PostgreSQL sẽ làm ở Sprint 6 (Task 1.5, 1.6).

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Có hàm tính **mã băm SHA-256** của một tài liệu, trả về chuỗi hex 64 ký tự (khớp cột `file_hash` trong schema của bạn). Mã băm được tính trên **văn bản đã chuẩn hóa ở Task 1.2**, và có unit test chứng minh:
   - hai bản của cùng một tài liệu, chỉ khác nhau ở xuống dòng (CRLF/LF) hoặc dạng Unicode (NFD/NFC), cho **cùng** mã băm;
   - sửa một chữ trong nội dung thì mã băm **khác**.
2. Có **hàm thuần lập kế hoạch nạp**. Đầu vào: danh sách tài liệu vừa quét (từ Task 1.1, kèm mã băm) và trạng thái đã biết (với mỗi tài liệu: mã băm và `version` của phiên bản đang hiệu lực). Đầu ra: một hành động cho từng tài liệu:
   - `NEW`: chưa từng thấy → nạp với `version = 1`;
   - `UNCHANGED`: mã băm trùng phiên bản đang hiệu lực → bỏ qua;
   - `CHANGED`: cùng đường dẫn nhưng mã băm khác → nạp phiên bản mới, `version` = cũ + 1.
3. Một tài liệu được nhận diện bằng cặp **(`tenant_id`, đường dẫn file)**. Hai tenant cùng có file `noi_quy.txt` là hai tài liệu độc lập.
4. "Trạng thái đã biết" được đọc qua một **interface** (ví dụ `typing.Protocol`), có sẵn một bản cài đặt lưu trong bộ nhớ (in-memory) để dùng trong test. Ở Sprint 6, bạn chỉ cần viết thêm bản cài đặt đọc từ PostgreSQL, **không sửa** hàm lập kế hoạch.
5. Có test kịch bản đầu-cuối chạy trên dữ liệu mẫu, mô phỏng nhiều lần chạy liên tiếp:
   - **Lần 1:** mọi tài liệu đều là `NEW`.
   - **Lần 2, không đổi gì:** mọi tài liệu đều là `UNCHANGED`, không sinh thao tác ghi nào.
   - **Lần 3, thay `tenant_retail/quy_che_doi_tra.md` bằng bản trong `sample_data/updates/`:** đúng **1** tài liệu `CHANGED` với `version = 2`, còn lại `UNCHANGED`.
   - **Lần 4, một file chỉ đổi kiểu xuống dòng:** vẫn là `UNCHANGED`.
6. Mỗi lần lập kế hoạch ghi một dòng log tổng kết: số tài liệu `NEW` / `UNCHANGED` / `CHANGED`.
7. Có mục ngắn trong `docs/` giải thích **bạn tính mã băm trên byte gốc hay trên văn bản đã chuẩn hóa, và vì sao** (câu hỏi tư duy của Task 1.2).

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Idempotency:** Một thao tác được gọi là idempotent nếu thực hiện 1 lần hay N lần đều cho cùng kết quả. Đây là tính chất quan trọng bậc nhất của data pipeline, vì pipeline *chắc chắn* sẽ bị chạy lại.
- **Mã băm nội dung (content hash):** SHA-256 biến nội dung bất kỳ thành một "dấu vân tay" 256 bit. Nội dung giống nhau luôn cho cùng dấu vân tay; khác nhau dù một bit thì cho dấu vân tay khác hoàn toàn. Vì sao so sánh mã băm tốt hơn so sánh thời điểm sửa file (`last_modified`) hay kích thước file?
- **Tách "quyết định" khỏi "thực thi":** Hàm lập kế hoạch chỉ *quyết định* cần làm gì và không đụng vào database, nên test được dễ dàng và chạy thử (dry-run) được. Phần *thực thi* kế hoạch (ghi database) để riêng, làm ở Sprint 6.
- **Lớp phòng thủ cuối cùng:** Nếu 2 tiến trình pipeline chạy song song cùng lúc, cả hai có thể cùng quyết định `CHANGED` cho một file. Ràng buộc "chỉ 1 phiên bản đang hiệu lực" bạn viết trong schema ở Task 0.4 chính là thứ chặn được trường hợp này.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `idempotent data pipeline design`
- `python hashlib sha256 hexdigest`
- `content hash change detection etl`
- `python typing Protocol dependency inversion`
- `dry run pattern data pipeline`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Một file bị **xóa** khỏi MinIO thì lần chạy sau nên làm gì với bản ghi của nó trong database: không làm gì, đánh dấu hết hiệu lực, hay xóa hẳn? Mỗi lựa chọn ảnh hưởng thế nào đến kết quả tìm kiếm?*
- *Hai file **khác đường dẫn** nhưng **nội dung giống hệt** nhau trong cùng một tenant thì có nên coi là một tài liệu không? Còn nếu chúng nằm ở hai tenant khác nhau thì sao? (Gợi ý: nghĩ về cách ly dữ liệu.)*
- *Nếu bạn đổi cách làm sạch văn bản ở Task 1.2 (ví dụ xử lý thêm một loại ký tự lạ), mọi mã băm cũ sẽ thay đổi. Lần chạy kế tiếp sẽ coi mọi tài liệu là `CHANGED`. Đó là lỗi hay là hành vi đúng?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Định nghĩa dữ liệu trước:** một kiểu cho "tài liệu đã quét" (tenant, đường dẫn, mã băm), một kiểu cho "trạng thái đã biết" (mã băm và version của phiên bản đang hiệu lực), một kiểu cho "hành động" (loại hành động + version mới). Tìm hiểu `dataclasses` hoặc `enum` của Python.
2. **Viết hàm băm:** nối với hàm làm sạch của Task 1.2, chú ý mã hóa chuỗi sang byte UTF-8 trước khi băm.
3. **Viết interface trạng thái + bản in-memory:** bản in-memory chỉ cần một dict, khóa là `(tenant_id, đường dẫn)`.
4. **Viết hàm lập kế hoạch:** với từng tài liệu đã quét, tra trạng thái và trả về hành động. Hàm này không ghi gì cả.
5. **Viết test kịch bản (DoD 5):** sau mỗi "lần chạy", tự cập nhật bản in-memory như thể đã ghi database thành công, rồi chạy lần kế tiếp.

### 2. Những Vấn Đề Thường Gặp
- **Lần chạy thứ 2 vẫn báo mọi tài liệu `CHANGED`:** Gần như chắc chắn là hàm làm sạch hoặc chunking chưa tất định, hoặc bạn băm trên dữ liệu có chứa thông tin thay đổi theo lần chạy (thời gian, đường dẫn tạm...). In mã băm của cùng một file ở 2 lần chạy ra để so sánh.
- **Mã băm khác nhau giữa máy bạn và CI:** Thường do khác nhau về xuống dòng hoặc encoding khi đọc file. Đây chính là lý do nên băm trên văn bản đã chuẩn hóa.
- **Test kịch bản phụ thuộc thứ tự tài liệu:** Danh sách object từ MinIO không đảm bảo luôn cùng thứ tự. Hãy so sánh kết quả theo khóa `(tenant_id, đường dẫn)`, không so theo vị trí trong danh sách.

</details>
