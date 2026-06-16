# Automated Dictionary Extraction for Fuzzing (ADEF)

[![Framework](https://img.shields.io/badge/Framework-Angr-blue.svg)](https://angr.io/)
[![Fuzzer](https://img.shields.io/badge/Fuzzer-AFL++-red.svg)](https://aflplus.plus/)
[![Language](https://img.shields.io/badge/Language-Python%203-yellow.svg)](https://www.python.org/)
[![Solver](https://img.shields.io/badge/SMT_Solver-Z3-orange.svg)](https://github.com/Z3Prover/z3)

Dự án nghiên cứu và phát triển công cụ theo kiến trúc **Lai ghép (Hybrid Architecture)**, kết hợp Phân tích Đồ thị luồng điều khiển (CFG) và Thực thi biểu tượng (Symbolic Execution) để tự động trích xuất từ điển cho Fuzzer. Mục tiêu là giúp **AFL++** đâm thủng các **"Bức tường độ phủ" (Coverage Wall)** chứa các hằng số bị làm rối (Obfuscation) trong các tệp nhị phân không có mã nguồn.

---

## Tổng Quan Thách Thức (The Target)

Để chứng minh giới hạn của Fuzzing mù truyền thống, một hệ thống mục tiêu (`test_target.c`) được thiết kế với 3 lớp bảo mật ngặt nghèo, ứng dụng các kỹ thuật che giấu mật khẩu chuyên sâu:

1. **Bức tường 1 (SIGABRT) - Block Casting & XOR:** Ép kiểu 4 bytes đầu vào thành một số nguyên 32-bit nguyên khối và XOR với `0xDEADBEEF`. Triệt tiêu hoàn toàn cơ chế phản hồi từng byte (Coverage-feedback) của fuzzer.
2. **Bức tường 2 (SIGSEGV) - Hệ phương trình tuyến tính:** Fuzzer phải tìm 2 ký tự thỏa mãn đồng thời hệ phương trình `x + y = 164` và `x - y = 8` (Nghiệm: `VN`).
3. **Bức tường 3 (SIGILL) - Checksum & Inter-dependent Constraints:** Tổng 3 bytes đầu vào phải bằng `222`, kết hợp với một phép XOR ngầm định.

---

## Kiến Trúc Công Cụ ADEF (The Extractor)

Thay vì đoán mò dữ liệu ngẫu nhiên, script `adef_extractor.py` hoạt động như một hệ thống dịch ngược tự động với luồng xử lý:

1. **Khôi phục CFG (CFGFast):** Nạp tệp nhị phân đã strip, loại bỏ thư viện hệ thống (`auto_load_libs=False`) để khoanh vùng các basic blocks chứa nhánh điều kiện.
2. **Simulation Manager:** Thu thập các phép toán kiểm tra (nhân, trừ, XOR) trong mã máy và chuyển đổi thành **Hệ phương trình ràng buộc (Path Constraints)**.
3. **Z3 SMT Solver:** Tự động đảo ngược và phân giải các phương trình toán học phức tạp để tìm ra chính xác các "Magic Bytes" (`ManhU`, `UET!`, `SECUREF` hoặc các chuỗi làm rối).
4. **Dictionary Generation:** Làm sạch dữ liệu và đóng gói thành tệp `router.dict` chuẩn format của AFL++.

---

## Đánh Giá Thực Nghiệm (Evaluation)

Sức mạnh của mô hình Hybrid được chứng minh qua 2 Test Case đối chứng:

* **Test Case 1 (Fuzzing Mù - Baseline):** AFL++ bị chặn đứng hoàn toàn trước kỹ thuật ép khối 32-bit. Dù cày cuốc với tốc độ `13.4k/sec`, ném vào hệ thống tới gần **10 triệu bài test** trong suốt hơn 12 phút, AFL++ vẫn trả về **0 Crashes**.
* **Test Case 2 (Hybrid Fuzzing):** Khi được nạp từ điển `router.dict` do Z3 Solver giải mã, AFL++ lột xác hoàn toàn. Nó bốc các từ khóa, đâm thủng liên hoàn cả 3 chướng ngại vật phức tạp nhất và ghi nhận trọn vẹn **3 Crashes** (SIGABRT, SIGSEGV, SIGILL) trong thời gian tính bằng mili-giây (**Instakill**). Tốc độ phát hiện lỗ hổng tăng lên gấp hàng vạn lần.

---

## 📁 Cấu Trúc Thư Mục

```text
├── src/                    # Mã nguồn công cụ trích xuất
│   └── adef_extractor.py   # Core script sử dụng Angr và Z3 Solver
├── target/                 # Môi trường kiểm thử
│   ├── test_target.c       # Mã nguồn C mục tiêu (chứa 3 lớp Obfuscation)
│   └── test_target         # File nhị phân sau khi biên dịch (Stripped)
├── output/                 # Kết quả sinh ra từ công cụ
│   └── router.dict         # File từ điển tự động trích xuất đạt chuẩn
├── evaluation/             # Lưu trữ dữ liệu thực nghiệm AFL++
│   ├── in/                 # Chứa file seed khởi tạo
│   ├── out_no_dict/        # Log kết quả Fuzzing mù
│   ├── out_with_dict/      # Log kết quả Hybrid Fuzzing
│   └── plot_coverage.py    # Script Python (Matplotlib) vẽ biểu đồ bậc thang
└── README.md               # Tài liệu dự án
