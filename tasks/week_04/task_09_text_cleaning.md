# Task 1.2: Trích Xuất & Làm Sạch Văn Bản (Text Extractor & Normalizer)

- **Giai đoạn:** Sprint 4 — Trích xuất & làm sạch văn bản
- **Mục tiêu:** Biến các file thô (đầy "rác" bạn cài vào ở Task 0.6) thành văn bản sạch, thống nhất, nhưng **vẫn giữ cấu trúc tiêu đề**. Văn bản sạch là đầu vào cho chunking (Sprint 5) và cho mã băm chống trùng lặp (Task 1.4).

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Đọc được nội dung file `.txt` và `.md` dạng UTF-8, kể cả file có BOM ở đầu. File không giải mã được bằng UTF-8 sẽ bị bỏ qua và ghi log `ERROR`, không làm dừng cả lô xử lý.
2. Văn bản được chuẩn hóa Unicode về dạng **NFC**. Có unit test chứng minh: một chuỗi tiếng Việt viết dạng NFD, sau khi làm sạch, **bằng đúng** chuỗi NFC tương ứng.
3. Làm sạch được các loại rác:
   - ký tự vô hình (zero-width) và ký tự điều khiển;
   - khoảng trắng thừa cuối dòng;
   - nhiều dòng trống liên tiếp;
   - xuống dòng kiểu Windows (CRLF → LF).
4. **Giữ nguyên cấu trúc:** dòng tiêu đề Markdown (`#`, `##`, ...) và danh sách (`-`, `1.`) vẫn còn sau khi làm sạch.
5. Hàm làm sạch là **hàm thuần** (nhận chuỗi, trả chuỗi) và **idempotent**: làm sạch 2 lần cho kết quả giống làm sạch 1 lần. Có unit test cho tính chất này.
6. Chạy được trên toàn bộ corpus của Task 0.6 và in báo cáo tổng kết: số file xử lý thành công, số file bị bỏ qua và lý do. Dán báo cáo vào mô tả PR.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Các dạng chuẩn hóa Unicode (NFC, NFD, NFKC, NFKD):** Khác nhau thế nào? Vì sao với tiếng Việt thường chọn NFC? NFKC "mạnh tay" hơn ở điểm nào và có thể làm hỏng gì?
- **Encoding và BOM:** UTF-8, UTF-8 có BOM (`utf-8-sig`) và UTF-16 khác nhau thế nào? Vì sao file lưu bằng một số công cụ trên Windows hay có BOM ở đầu?
- **Ký tự vô hình:** Zero-width space (U+200B), zero-width joiner, non-breaking space... Chúng lọt vào văn bản từ đâu (copy từ web, từ Word) và gây hại gì cho tìm kiếm?
- **Idempotency ở mức hàm:** Vì sao một bước làm sạch không idempotent sẽ khiến mã băm SHA-256 (Task 1.4) thay đổi mỗi lần pipeline chạy lại, dẫn tới nạp trùng dữ liệu?

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `python unicodedata normalize NFC NFD`
- `vietnamese unicode precomposed vs decomposed`
- `python open encoding utf-8-sig BOM`
- `remove zero width characters python regex`
- `property based testing idempotent function` (tìm hiểu thêm: thư viện `hypothesis`)

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Mã băm SHA-256 ở Task 1.4 nên tính trên **byte gốc** của file hay trên **văn bản đã làm sạch**? Mỗi lựa chọn dẫn tới hành vi gì khi người dùng tải lại một file chỉ khác nhau ở kiểu xuống dòng (CRLF/LF)?*
- *Nếu làm sạch "quá tay", ví dụ xóa mọi ký tự `#`, thì Sprint 5 mất thông tin gì khi muốn cắt đoạn theo tiêu đề mục?*
- *Một câu hỏi người dùng gõ dạng NFD tìm trong kho văn bản dạng NFC thì Full-Text Search có tìm thấy không? Vậy câu hỏi của người dùng có cần đi qua cùng hàm làm sạch không?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Tách 2 phần:** phần *đọc byte → chuỗi* (xử lý encoding, BOM, lỗi giải mã) và phần *chuỗi → chuỗi sạch* (hàm thuần). Unit test tập trung vào phần thứ hai.
2. **Viết test trước** cho từng loại rác của Task 0.6: mỗi loại một test nhỏ, đầu vào là chuỗi có rác, đầu ra là chuỗi mong muốn.
3. **Thứ tự các bước làm sạch có ý nghĩa.** Ví dụ: chuẩn hóa xuống dòng trước rồi mới gộp dòng trống, chuẩn hóa Unicode trước khi xử lý khoảng trắng. Hãy tự thử đổi thứ tự rồi xem test nào đỏ.
4. **Kiểm tra idempotent:** với mọi file trong corpus, so sánh `clean(x)` với `clean(clean(x))`.
5. Viết một lệnh chạy cả lô trên thư mục `sample_data/` và in báo cáo tổng kết.

### 2. Những Vấn Đề Thường Gặp
- **Test so sánh chuỗi báo khác nhau dù in ra trông giống hệt:** Gần như chắc chắn là khác dạng Unicode hoặc có ký tự vô hình. In `repr()` của chuỗi, hoặc in mã của từng ký tự để thấy sự khác biệt.
- **Regex xóa khoảng trắng làm mất thụt đầu dòng của danh sách con hoặc khối code trong Markdown:** Thu hẹp regex chỉ áp dụng cho khoảng trắng *cuối dòng*, không đụng khoảng trắng đầu dòng.
- **File đọc trên Windows bị lỗi `UnicodeDecodeError`:** Luôn chỉ định rõ `encoding=` khi mở file. Đừng phụ thuộc vào encoding mặc định của hệ điều hành.

</details>
