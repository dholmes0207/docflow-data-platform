# Task 1.0: Khung Dự Án Python & Quy Ước Code

- **Giai đoạn:** Sprint 3 — Khung dự án & bộ dữ liệu thật sự
- **Mục tiêu:** Từ Sprint 4 bạn bắt đầu viết code pipeline thật. Trước khi viết dòng code nghiệp vụ đầu tiên, hãy dựng một "bộ khung" đúng chuẩn: code đặt ở đâu, cấu hình đọc từ đâu, log ghi thế nào, test chạy ra sao. Bộ khung tốt giúp các sprint sau không phải đập đi làm lại.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Code pipeline nằm trong một package Python theo **src layout** (`src/docflow/`). File `pyproject.toml` ở gốc repo khai báo tên dự án, phiên bản Python tối thiểu và các thư viện phụ thuộc.
2. Cài được dự án ở chế độ phát triển (editable) trong môi trường ảo, và `import docflow` chạy được từ bất kỳ thư mục nào.
3. Có **một module cấu hình duy nhất** đọc thông tin kết nối (Postgres, MinIO) từ biến môi trường hoặc file `.env`. Không có mật khẩu hay địa chỉ kết nối nào ghi cứng trong code. Nếu thêm biến mới, cập nhật luôn `.env.example`.
4. Dùng module `logging` của Python thay cho `print`. Mỗi dòng log có thời gian, mức độ (INFO/WARNING/ERROR) và tên module.
5. Có thư mục `tests/unit/` với **ít nhất 2 test** chạy được bằng `pytest`, ví dụ: test module cấu hình báo lỗi rõ ràng khi thiếu biến bắt buộc.
6. Trên Pull Request, check CI **`unit`** chạy test của bạn và xanh. Ba check cũ `hygiene`, `schema`, `secrets` vẫn xanh.
7. README có mục ngắn hướng dẫn cài đặt và chạy test cho người mới clone repo.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **`pyproject.toml`:** File khai báo dự án Python theo chuẩn hiện đại (PEP 621), thay thế cho `setup.py` và một phần `requirements.txt`. Phân biệt *thư viện dự án cần để chạy* với *công cụ chỉ dùng khi phát triển* (pytest, ruff...).
- **src layout và flat layout:** Vì sao nhiều dự án đặt code trong `src/` thay vì để thư mục package ngay ở gốc repo? Liên quan gì đến việc "test chạy được trên máy mình nhưng hỏng khi người khác cài"?
- **Cấu hình theo môi trường (12-Factor App, mục Config):** Cùng một đoạn code chạy ở máy bạn, trong CI và trên server, chỉ khác biến môi trường. Vì sao không nên ghi cứng `localhost:5432` vào code?
- **Logging thay cho print:** Log có mức độ, có thể bật/tắt, ghi ra file, gửi về hệ thống giám sát. Với pipeline chạy tự động lúc nửa đêm (Airflow ở Sprint 10), log là thứ duy nhất cho bạn biết chuyện gì đã xảy ra.
- **Unit test & pytest:** Test một hàm nhỏ, độc lập, chạy trong vài mili giây, không cần database hay MinIO thật.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `python packaging user guide pyproject.toml`
- `src layout vs flat layout python`
- `pip install editable mode -e`
- `12 factor app config environment variables`
- `pydantic-settings` hoặc `python-dotenv`
- `python logging basicConfig format best practices`
- `pytest getting started fixtures monkeypatch`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Khi thiếu biến `POSTGRES_PASSWORD`, chương trình nên báo lỗi ngay lúc khởi động, hay đợi đến lúc kết nối database mới hỏng? Cách nào giúp bạn tìm ra lỗi nhanh hơn khi pipeline chạy lúc 2 giờ sáng?*
- *Vì sao file `.env` không được commit nhưng `.env.example` thì phải commit? Người mới clone repo sẽ gặp khó khăn gì nếu thiếu `.env.example`?*
- *Một hàm vừa kết nối MinIO, vừa đọc file, vừa làm sạch văn bản thì khó viết unit test ở chỗ nào? Bạn sẽ chia nhỏ nó thế nào để test được phần làm sạch mà không cần MinIO?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Gợi Ý Cấu Trúc Thư Mục
Bạn tự quyết định chi tiết, đây chỉ là một hướng tham khảo:
```text
pyproject.toml
src/docflow/
├── __init__.py
├── config.py          # đọc biến môi trường, một nơi duy nhất
├── logging_setup.py   # cấu hình logging dùng chung
├── storage/           # Sprint 4: làm việc với MinIO
└── text/              # Sprint 4: trích xuất & làm sạch văn bản
tests/unit/
└── test_config.py
```

### 2. Luồng Các Bước
1. Tạo môi trường ảo, viết `pyproject.toml` tối thiểu (tên, phiên bản, `requires-python`, dependencies), rồi cài dự án ở chế độ editable.
2. Viết module cấu hình: đọc biến môi trường, kiểm tra biến bắt buộc, báo lỗi dễ hiểu khi thiếu.
3. Viết hàm cấu hình logging, gọi một lần ở điểm khởi động chương trình. Các module khác chỉ cần `logging.getLogger(__name__)`.
4. Viết test cho module cấu hình. Tìm hiểu `monkeypatch` của pytest để giả lập biến môi trường trong test.
5. Mở PR và xem check `unit` trên CI. Check này tự cài dự án của bạn (dựa trên `pyproject.toml`) rồi chạy mọi test trong `tests/`, trừ `tests/gates/`.

### 3. Những Vấn Đề Thường Gặp
- **`ModuleNotFoundError: No module named 'docflow'` khi chạy pytest:** Thường do chưa cài dự án ở chế độ editable vào đúng môi trường ảo, hoặc đang chạy `pytest` của Python hệ thống thay vì của môi trường ảo. Kiểm tra bằng `which python` và `which pytest`.
- **CI báo `ruff` lỗi dù máy bạn chạy được:** Hãy chạy `pre-commit install` (xem `CONTRIBUTING.md`) để ruff tự kiểm tra mỗi lần commit, đúng phiên bản CI đang dùng.
- **Check `unit` báo "no tests ran":** Check này yêu cầu đã có `pyproject.toml` thì phải có test. Kiểm tra tên file test bắt đầu bằng `test_`.

</details>
