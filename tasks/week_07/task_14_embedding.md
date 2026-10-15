# Task 2.1: Tạo Vector Embedding Đa Ngôn Ngữ Chạy Cục Bộ (CPU)

- **Giai đoạn:** Sprint 7 — Vector embedding & lưu trữ pgvector
- **Mục tiêu:** Biến mỗi chunk văn bản (Task 1.3) thành một vector 384 chiều bằng mô hình embedding **hiểu tiếng Việt**, chạy hoàn toàn trên CPU máy bạn, chi phí $0. Đây là "bộ não ngữ nghĩa" giúp Sprint 8 tìm được đoạn văn đúng nghĩa dù câu hỏi không dùng đúng từ trong tài liệu.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Có module embedding dùng một trong hai mô hình đa ngôn ngữ của roadmap (`paraphrase-multilingual-MiniLM-L12-v2` hoặc `multilingual-e5-small`). Tên mô hình, **phiên bản (revision) được ghim cố định** và kích thước lô (batch size) đọc từ module cấu hình, không ghi cứng.
2. Mô hình được nạp **một lần** cho cả lần chạy, không nạp lại cho từng chunk. Embedding được tính **theo lô**.
3. Dùng mô hình **đúng cách theo model card** của nó:
   - nếu mô hình yêu cầu tiền tố riêng cho câu hỏi và cho đoạn văn, code phải thêm đúng tiền tố;
   - vector đầu ra được chuẩn hóa (độ dài bằng 1), để khoảng cách cosine ở Sprint 8 có ý nghĩa.

   Ghi rõ lựa chọn của bạn trong `docs/embedding.md`.
4. Kiểm tra **cắt cụt âm thầm**: đếm số token của từng chunk bằng tokenizer của chính mô hình; chunk nào vượt giới hạn đầu vào thì ghi log `WARNING` kèm định danh chunk. Báo cáo trên corpus có bao nhiêu chunk bị vượt. Nếu nhiều, quay lại điều chỉnh kích thước chunk của Task 1.3.
5. Module embedding được dùng qua một **interface**. Unit test dùng một bản giả (fake embedder) tất định, chạy trong mili giây, **không tải mô hình và không cần mạng**. Test với mô hình thật được đánh dấu riêng và chỉ chạy khi bật cờ (ví dụ biến môi trường `RUN_MODEL_TESTS=1`), để check CI `unit` không phải tải hàng trăm MB.
6. Có test với mô hình thật (chạy trên máy bạn, dán output vào PR) kiểm tra ngữ nghĩa cơ bản. Ví dụ: câu "được nghỉ phép bao nhiêu ngày?" phải gần đoạn nói về nghỉ phép **hơn** đoạn nói về hoa hồng bán hàng.
7. `docs/embedding.md` có số đo tốc độ trên CPU của bạn (chunk/giây) với **2 kích thước lô khác nhau**, và thời gian ước tính để embed toàn bộ corpus.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Embedding là gì:** Một cách biểu diễn văn bản thành điểm trong không gian nhiều chiều, sao cho các văn bản *cùng nghĩa* nằm gần nhau, kể cả khi không dùng chung từ nào.
- **Model card:** Trang mô tả đi kèm mỗi mô hình (trên Hugging Face). Nó cho biết mô hình được huấn luyện trên dữ liệu gì, giới hạn số token đầu vào, có cần tiền tố đặc biệt không, nên dùng khoảng cách nào. Đọc model card **trước** khi viết code.
- **Ghim phiên bản mô hình:** Mô hình trên Hugging Face có thể được tác giả cập nhật. Không ghim phiên bản thì cùng một code, chạy vào 2 thời điểm khác nhau, có thể cho vector khác nhau, và bộ nhớ đệm ở Task 2.2 sẽ sai.
- **Chuẩn hóa vector:** Khi mọi vector có độ dài 1, tích vô hướng và độ tương đồng cosine cho cùng thứ hạng. Vì sao điều này quan trọng khi chọn toán tử khoảng cách của pgvector?
- **Tách interface khỏi mô hình thật:** Giống Task 1.4. Logic xung quanh (gom lô, kiểm tra token, ghi log) test được bằng bản giả; chỉ phần "gọi mô hình" cần mô hình thật.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `sentence-transformers quickstart encode batch_size normalize_embeddings`
- `multilingual-e5-small model card query passage prefix`
- `paraphrase-multilingual-MiniLM-L12-v2 model card`
- `huggingface model revision pin commit hash`
- `pytorch cpu only install pip index-url`
- `pytest custom marker skip unless environment variable`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Nếu bạn quên thêm tiền tố mà mô hình yêu cầu, chương trình có báo lỗi không? Bạn sẽ phát hiện ra bằng cách nào?*
- *Câu hỏi của người dùng ở Sprint 8 có cần đi qua **cùng** hàm làm sạch (Task 1.2) và **cùng** mô hình, cùng phiên bản, như các chunk không? Điều gì xảy ra nếu không?*
- *Embedding toàn bộ corpus mất vài phút trên máy bạn. Với 1 triệu tài liệu thì sao? Bạn sẽ làm gì để không phải tính lại những chunk đã tính rồi? (Đây chính là Task 2.2.)*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Gợi Ý
1. **Đọc model card** của 2 mô hình, chọn 1, ghi lý do vào `docs/embedding.md`: giới hạn token, có cần tiền tố không, kích thước tải về.
2. **Định nghĩa interface** (ví dụ `embed_passages(texts) -> list[vector]` và `embed_query(text) -> vector`), viết bản giả tất định cho test: cùng chuỗi luôn ra cùng vector, đúng 384 chiều, đã chuẩn hóa.
3. **Viết bản thật** dùng `sentence-transformers`: nạp mô hình một lần, ghim revision, encode theo lô, bật chuẩn hóa.
4. **Kiểm tra token:** lấy tokenizer từ chính mô hình, đếm token từng chunk, so với giới hạn đầu vào của mô hình.
5. **Đo tốc độ:** chạy trên toàn bộ chunk của corpus với 2 kích thước lô, ghi kết quả.

### 2. Những Vấn Đề Thường Gặp
- **Cài `sentence-transformers` tải về vài GB và rất lâu:** Trên Linux, `torch` mặc định kéo theo bản hỗ trợ GPU (CUDA). Máy bạn chỉ chạy CPU, nên hãy cài `torch` bản CPU trước (xem từ khóa `pytorch cpu only`), rồi mới cài `sentence-transformers`.
- **Lần chạy đầu rất chậm, các lần sau nhanh:** Lần đầu phải tải mô hình về thư mục cache trên máy. Tìm hiểu biến môi trường điều khiển thư mục cache của Hugging Face nếu ổ WSL của bạn ít dung lượng.
- **WSL bị treo hoặc hết RAM khi encode:** Kích thước lô quá lớn. Giảm batch size, và kiểm tra lại giới hạn RAM trong `.wslconfig` (Task 0.2).
- **Test với mô hình thật đỏ trên CI:** CI không có mô hình và không nên tải. Kiểm tra lại cơ chế đánh dấu và bỏ qua test cần mô hình thật (DoD 5).

</details>
