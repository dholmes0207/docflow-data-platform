# Task 1.3: Cắt Đoạn Văn Bản (Chunking) & Đính Kèm Metadata

- **Giai đoạn:** Sprint 5 — Semantic chunking & nạp dữ liệu không trùng lặp
- **Mục tiêu:** Chia văn bản sạch (đầu ra của Task 1.2) thành các đoạn (chunk) đủ nhỏ để mô hình embedding ở Sprint 7 xử lý trọn vẹn, nhưng vẫn đủ ngữ cảnh để người đọc hiểu được khi chỉ nhìn thấy đúng đoạn đó. Mỗi chunk mang theo metadata cho biết nó thuộc tenant nào, nằm ở đâu trong tài liệu và dưới tiêu đề mục nào.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Có hàm chunking **tự cài đặt** (không gọi thư viện chunking có sẵn như LangChain), nhận văn bản đã làm sạch và trả về danh sách chunk. Mỗi chunk có ít nhất:
   - `chunk_index`: liên tục từ 0;
   - `content`;
   - vị trí bắt đầu và kết thúc trong văn bản gốc (`char_start`, `char_end`);
   - metadata: `tenant_id`, đường dẫn tài liệu, và **đường dẫn tiêu đề** chứa đoạn (ví dụ `Chính sách nghỉ phép > Nghỉ phép năm`).
2. Kích thước chunk và tỷ lệ chồng lấn (overlap, khoảng **15–20%**) là tham số, đọc từ module cấu hình của Task 1.0, không ghi cứng trong hàm.
3. Thuật toán ưu tiên cắt ở ranh giới tự nhiên theo thứ tự: tiêu đề Markdown → đoạn văn → câu → từ. **Không cắt giữa một từ**, trừ khi bản thân một "từ" đã dài hơn kích thước chunk (ví dụ một URL rất dài).
4. **Không mất chữ nào:** với mọi chunk, `text[char_start:char_end] == content`, và hợp các khoảng `[char_start, char_end)` phủ kín toàn bộ phần văn bản có nội dung. Có unit test chứng minh điều này.
5. Không có chunk rỗng hoặc chỉ toàn khoảng trắng. Tài liệu rỗng cho ra 0 chunk kèm log `WARNING`.
6. **Tất định (deterministic):** chạy 2 lần trên cùng đầu vào cho ra kết quả giống hệt nhau. Task 1.4 và Sprint 7 dựa vào tính chất này.
7. Có file `docs/chunking.md` gồm:
   - kích thước chunk bạn chọn và lý do, có tính đến **giới hạn số token đầu vào** của mô hình embedding dự kiến dùng ở Sprint 7;
   - bảng thống kê trên corpus Task 0.6: số chunk mỗi tenant, độ dài nhỏ nhất / trung vị / lớn nhất;
   - so sánh **2 cấu hình** (ví dụ chunk nhỏ và chunk lớn) bằng cách đọc cùng 3–5 đoạn cụ thể và nhận xét.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Vì sao phải chunking:** Mô hình embedding chỉ đọc được một số lượng token giới hạn. Phần vượt quá bị **cắt bỏ âm thầm**, không báo lỗi. Ngoài ra, một vector đại diện cho cả tài liệu dài sẽ "loãng" nghĩa, khó khớp với câu hỏi cụ thể.
- **Ký tự và token:** Mô hình đếm theo token, không theo ký tự. Với tiếng Việt, tokenizer đa ngôn ngữ thường tách một từ thành nhiều token. Một chunk 1.000 ký tự tiếng Việt có thể chiếm nhiều token hơn bạn nghĩ.
- **Recursive splitting:** Thử cắt bằng dấu phân tách "lớn" trước (tiêu đề, dòng trống); đoạn nào vẫn còn quá dài thì cắt tiếp bằng dấu phân tách "nhỏ" hơn (dấu chấm câu, khoảng trắng).
- **Overlap:** Phần chồng lấn giữa 2 chunk liền kề giúp một ý nằm vắt qua ranh giới không bị cắt mất ngữ cảnh. Đổi lại, dữ liệu bị lưu trùng và có thể sinh kết quả tìm kiếm lặp.
- **Metadata tiêu đề:** Một đoạn chỉ ghi "được hưởng 12 ngày" sẽ vô nghĩa nếu không biết nó nằm dưới mục "Nghỉ phép năm" của công ty nào.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `chunking strategies for RAG`
- `recursive character text splitter how it works`
- `chunk size overlap trade off retrieval quality`
- `sentence-transformers max_seq_length truncation`
- `markdown header based chunking`
- `tokenizer vietnamese subword tokens`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Chunk quá nhỏ (1–2 câu) và chunk quá lớn (cả trang) mỗi loại gây ra vấn đề gì khi tìm kiếm? Bạn sẽ dùng bộ câu hỏi của Task 0.6 thế nào để chọn kích thước?*
- *Nếu chunking không tất định (mỗi lần chạy cắt hơi khác nhau), chuyện gì xảy ra với cơ chế chống trùng lặp ở Task 1.4 và với bộ nhớ đệm embedding ở Sprint 7?*
- *Câu hỏi bẫy rò rỉ của Task 0.6 hỏi về "chính sách nghỉ phép" của tenant khác. Metadata nào của chunk giúp hệ thống chặn được trường hợp này?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Viết test cho các tính chất trước khi viết thuật toán:** không mất chữ (DoD 4), không chunk rỗng (DoD 5), tất định (DoD 6), không chunk nào dài quá giới hạn. Những test này đúng với *mọi* thuật toán, nên bạn có thể đổi thuật toán thoải mái mà test vẫn bảo vệ bạn.
2. **Bước 1: tách theo tiêu đề.** Duyệt văn bản, ghi nhận các dòng tiêu đề Markdown và cấp của chúng (`#`, `##`, ...) để biết mỗi đoạn văn nằm dưới đường dẫn tiêu đề nào.
3. **Bước 2: trong mỗi mục, gom đoạn văn** cho tới khi gần đạt kích thước chunk. Đoạn nào tự nó đã quá dài thì cắt tiếp theo câu, rồi theo từ.
4. **Bước 3: thêm overlap** bằng cách lùi điểm bắt đầu của chunk sau về một ranh giới từ (hoặc câu) nằm trong khoảng 15–20% cuối của chunk trước.
5. **Làm việc với vị trí (offset), không với chuỗi đã cắt:** thuật toán tính các cặp `(char_start, char_end)` trên văn bản gốc, rồi mới lấy `content = text[char_start:char_end]`. Cách này giúp DoD 4 gần như tự đúng.
6. Chạy trên toàn bộ corpus, in thống kê, đọc tận mắt vài chunk để viết `docs/chunking.md`.

### 2. Kiểm Tra Giới Hạn Token
- Bạn không bắt buộc phải cài mô hình embedding ở sprint này. Nhưng nên tìm hiểu giới hạn `max_seq_length` của mô hình dự kiến (xem Sprint 7 trong `roadmap/overview.md`) và ước lượng số token của chunk dài nhất bằng tokenizer của chính mô hình đó.
- Nếu chunk dài nhất vượt giới hạn, phần đuôi sẽ không bao giờ được tìm thấy. Hãy giảm kích thước chunk.

### 3. Những Vấn Đề Thường Gặp
- **Vòng lặp vô hạn khi overlap:** Nếu điểm bắt đầu của chunk sau không tiến lên so với chunk trước (overlap lớn hơn hoặc bằng chính độ dài chunk), thuật toán sẽ lặp mãi. Luôn đảm bảo mỗi bước tiến ít nhất 1 ký tự.
- **Chunk cuối cùng quá ngắn:** Ví dụ chỉ còn vài chữ. Cân nhắc gộp nó vào chunk liền trước.
- **Đường dẫn tiêu đề sai khi gặp tiêu đề cấp thấp hơn rồi quay lại cấp cao:** Ví dụ `##` → `###` → `##`. Dùng một ngăn xếp (stack) theo cấp tiêu đề.

</details>
