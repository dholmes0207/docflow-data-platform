# Task 0.6: Mở Rộng Bộ Dữ Liệu (Corpus) & Bộ Câu Hỏi Đánh Giá

- **Giai đoạn:** Sprint 3 — Khung dự án & bộ dữ liệu thật sự
- **Mục tiêu:** Bộ dữ liệu mẫu hiện tại chỉ có vài tài liệu ngắn, mỗi tài liệu vài trăm byte: quá nhỏ để luyện chunking (Sprint 5) và để đo chất lượng tìm kiếm (Sprint 8). Trong task này, bạn xây một bộ tài liệu đủ lớn, có cấu trúc và có chủ đích chứa "bẫy", kèm một bộ câu hỏi đánh giá có đáp án chuẩn (ground truth).

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Mỗi tenant (`tenant_retail`, `tenant_tech`) có **ít nhất 8 tài liệu** dạng `.md` hoặc `.txt`. Phần lớn tài liệu dài khoảng **800–3.000 từ** và có **ít nhất 2 cấp tiêu đề** (ví dụ `#` và `##`).
2. Có **ít nhất 3 cặp tài liệu "gần giống nhau" giữa 2 tenant**: cùng chủ đề (ví dụ cả hai công ty đều có quy định nghỉ phép) nhưng khác con số hoặc điều khoản. Đây là bẫy kiểm tra rò rỉ dữ liệu giữa các tenant.
3. Có **ít nhất 3 tài liệu chứa "rác" có chủ đích** để luyện làm sạch ở Task 1.2. Ví dụ: tiếng Việt viết ở dạng Unicode tổ hợp (NFD), ký tự vô hình (zero-width), khoảng trắng và dòng trống thừa, xuống dòng kiểu Windows (CRLF), ký tự BOM ở đầu file. Ghi rõ file nào chứa bẫy gì trong mô tả PR.
4. Có file câu hỏi đánh giá trong `sample_data/eval/` gồm **ít nhất 20 câu hỏi**. Mỗi câu ghi rõ: tenant hỏi, câu hỏi, đáp án mong đợi, file nguồn, **đoạn trích nguyên văn** chứa đáp án. Trong 20 câu phải có:
   - Ít nhất 4 câu **bẫy rò rỉ**: hỏi với tư cách tenant A về thông tin chỉ có ở tenant B, đáp án đúng là "không tìm thấy".
   - Ít nhất 2 câu mà **không tenant nào** có thông tin.
5. Toàn bộ là dữ liệu **giả lập**: không có tên, email, số điện thoại hay tài liệu thật của người hoặc công ty nào. Mỗi file nhỏ hơn 1 MB.
6. Các bẫy cũ của Task 0.5 vẫn còn nguyên: file rỗng, tài liệu có 2 phiên bản trong `sample_data/updates/` (CI kiểm tra điều này).

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Corpus đại diện (representative corpus):** Kết quả đánh giá chỉ đáng tin khi dữ liệu thử giống dữ liệu thật: độ dài, cấu trúc, cách viết, và cả những chỗ "bẩn". Một bộ tài liệu toàn câu ngắn, sạch sẽ sẽ khiến mọi thuật toán trông đều tốt.
- **Dữ liệu tổng hợp (synthetic data) bằng LLM:** Bạn được phép dùng ChatGPT, Claude, Gemini... để sinh tài liệu nháp. Nhưng LLM hay tạo nội dung lặp lại, mâu thuẫn hoặc quá "trơn tru". Vai trò của bạn là người biên tập: kiểm tra, sửa số liệu cho nhất quán và cố tình cài bẫy vào.
- **Ground truth gắn với văn bản, không gắn với chunk:** Ở Sprint 5 bạn sẽ thay đổi cách cắt đoạn nhiều lần, khiến `chunk_id` thay đổi theo. Nếu đáp án chuẩn ghi theo `chunk_id` thì mỗi lần đổi cách cắt lại phải làm lại toàn bộ bộ câu hỏi. Ghi theo **file nguồn + đoạn trích nguyên văn** thì bộ câu hỏi dùng được mãi.
- **Unicode dựng sẵn (NFC) và tổ hợp (NFD):** Chữ "ệ" có thể được lưu bằng 1 ký tự, hoặc bằng chữ "e" cộng 2 dấu riêng. Mắt thường thấy giống hệt nhau, nhưng máy tính coi là 2 chuỗi khác nhau. Đây là lỗi kinh điển khi xử lý tiếng Việt.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `synthetic data generation for RAG evaluation`
- `RAG evaluation dataset ground truth question answer`
- `unicode normalization NFC NFD vietnamese`
- `zero width space byte order mark BOM text cleaning`
- `CRLF vs LF line endings git`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Nếu toàn bộ 20 câu hỏi đều là câu "dễ" (từ khóa trong câu hỏi xuất hiện y nguyên trong tài liệu), bài so sánh Full-Text Search với Vector Search ở Sprint 8 sẽ cho kết luận gì? Kết luận đó có đúng với thực tế không?*
- *Vì sao câu hỏi "không có đáp án" lại quan trọng với một trợ lý AI nội bộ? Điều gì xảy ra nếu hệ thống luôn cố trả về "đoạn gần nhất"?*
- *Hai file trông giống hệt nhau trên màn hình nhưng mã băm SHA-256 lại khác nhau. Những nguyên nhân nào có thể gây ra điều này?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Lên danh sách chủ đề trước khi viết.** Với mỗi tenant, liệt kê 8–10 chủ đề tài liệu nội bộ (chính sách nhân sự, quy trình, hướng dẫn kỹ thuật, FAQ khách hàng...). Đánh dấu những chủ đề cả 2 công ty cùng có: đó là các cặp "gần giống" của DoD 2.
2. **Chốt "sự thật" cho từng tenant.** Ghi ra một bảng nhỏ các con số quan trọng (số ngày phép, mức hoa hồng, giờ làm việc...) của từng công ty. Khi sinh tài liệu bằng LLM, đưa bảng này vào yêu cầu để số liệu nhất quán giữa các tài liệu.
3. **Sinh nháp rồi biên tập.** Đọc lại từng tài liệu, sửa chỗ mâu thuẫn, xóa đoạn lặp, giữ cấu trúc tiêu đề rõ ràng.
4. **Cài bẫy làm sạch có kiểm soát.** Đừng gõ tay ký tự vô hình. Hãy viết một script nhỏ (tìm hiểu module `unicodedata` của Python) để chuyển một vài file sang NFD hoặc chèn ký tự đặc biệt. Sau đó kiểm tra lại bằng cách in mã của từng ký tự.
5. **Viết bộ câu hỏi sau cùng**, khi tài liệu đã ổn định, để đoạn trích nguyên văn không bị lệch.

### 2. Gợi Ý Định Dạng File Câu Hỏi
Bạn tự chọn định dạng (`.csv`, `.yaml` hoặc `.jsonl`), miễn là máy đọc được và có tối thiểu các trường sau:
- `id`, `tenant_id`, `question`
- `expected_answer` (để trống hoặc ghi "không tìm thấy" với câu bẫy)
- `source_file`, `source_quote`
- `type`: `normal` / `leak` / `no_answer`

### 3. Những Vấn Đề Thường Gặp
- **Git hoặc trình soạn thảo tự "sửa" bẫy của bạn:** Một số trình soạn thảo tự xóa khoảng trắng cuối dòng, tự đổi CRLF thành LF, hoặc tự xóa BOM khi lưu. Sau khi commit, hãy kiểm tra lại file trong repo (ví dụ dùng `file <tên file>` hoặc `hexdump -C <tên file> | head`) xem bẫy còn nguyên không. Repo đã cấu hình `.gitattributes` để Git **không** tự đổi xuống dòng của mọi file trong `sample_data/`, nên nếu bẫy vẫn mất thì thủ phạm là trình soạn thảo (xem cấu hình "files.eol" và "files.trimTrailingWhitespace" của VS Code).
- **Đoạn trích trong bộ câu hỏi không khớp tài liệu:** Thường do bạn sửa tài liệu sau khi đã viết câu hỏi. Có thể viết một script nhỏ kiểm tra mọi `source_quote` đều xuất hiện trong `source_file` tương ứng.

</details>
