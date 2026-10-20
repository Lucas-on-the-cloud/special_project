# Kế hoạch WGN trên máy mới — đêm 18/10/2026 (UTC+7)

## Máy và nguyên tắc

- RTX 5060 Ti 16 GB; Python portable tại `C:/sp/.tools/py311/python.exe`.
- PyTorch 2.7.1 + CUDA 12.8, torchvision 0.22.1, FP32, batch 32.
- Giữ nguyên toàn bộ code/config/kết quả trong `reproduction/`.
- Implementation mới ở `improvements/`; dữ liệu, log và optimizer checkpoint ở ngoài Git.
- Control mới là chuẩn so sánh trên môi trường mới; không kết luận từ việc so pilot 5 epochs với baseline cũ 25 epochs.
- Seed 1024, MobileViT-S ImageNet, input 256, Adam 1e-4, cosine 25 epochs. Chọn best theo validation accuracy.
- Mọi cấu hình được ấn định trước. Không đổi hyperparameter dựa vào test AUC.

## Dữ liệu

1. FF++ c23: 5.000 video từ EU2 theo danh sách/layout của official v4 downloader, có retry/resume, MP4 header, byte count và SHA256. Crop bằng MTCNN code cũ, detector size 512, 40 real/10 fake frames. Kiểm tra chính thức 720/140/140 video mỗi nhóm, không overlap source-video IDs, file ảnh decode được.
2. Celeb-DF v2 và DFDC: RGB ZIP + JSON do người dùng tải. Giải nén, giữ JSON nguồn, chỉ dùng test; map đường dẫn rõ ràng và từ chối match mơ hồ. Celeb-DF phải có đúng 518 test videos. Không cần Celeb-DF v1.
3. WildDeepfake: danh sách công khai của DeepfakeBench không liệt kê WildDeepfake. Dùng mirror của tác giả `xingjunm/WildDeepfake` trên Hugging Face, chỉ `real_test` và `fake_test`. Đã tải 157 shards, tạo 806 sequences/165.662 frames; không tải train, không chạy face detection lại.
4. C40 và FaceShifter được chuẩn bị sau main training để ưu tiên kết quả đầu tiên. Test C40/FaceShifter dùng cùng FF++ c23 checkpoint, nhằm so sánh khả năng generalize giữa control mới và ứng viên. Không đánh đồng với checkpoint train riêng C40/FaceShifter của lịch sử reproduction.

## Queue chính (một GPU job tại một thời điểm)

| Thứ tự | Job | Điều kiện và đầu ra |
|---|---|---|
| 1 | Synthetic CUDA smoke cho 5 cấu hình | Forward/backward, gradient finite, optimizer update, checkpoint round-trip, sampler invariants |
| 2 | Download + preprocess FF++ c23 | Resume từ dữ liệu đã tải, kiểm tra đầy đủ dữ liệu |
| 3 | External-data smoke + real-data smoke cho 5 cấu hình | Không dùng test metrics để tuning; nếu preflight lỗi thì dừng trước final training |
| 4 | Baseline control, 25 epochs | `baseline_final/best.pt`; checkpoint này dùng chấm độ khó |
| 5 | Gradient pilot 5 → fresh final 25 epochs | Pilot chỉ dùng train/val; final khởi tạo lại seed/pretrained, không tiếp tục scheduler pilot |
| 6 | Curriculum pilot 5 → fresh final 25 epochs | Độ khó được tính bằng control trên train split, lưu hash checkpoint/manifest |
| 7 | Temporal control λ=0, 25 epochs | Hai frame/anchor, cùng loss/sampling với temporal, kiểm soát chi phí train hai frame |
| 8 | Temporal pilot 5 → fresh final 25 epochs | `BCE(t)+BCE(t')+0.1*MSE(sigmoid logits)` |
| 9 | C40 + FaceShifter data và đánh giá bổ sung | Không fine-tune target |

Sau mỗi final run: upload checkpoint vào Hugging Face public, xác minh SHA-256, đánh giá các test set sẵn có rồi push metadata và kết quả lên GitHub. Thứ tự/cấu hình các run tiếp theo không phụ thuộc kết quả test. Sau giai đoạn chính, hoàn tất các cột robustness còn thiếu.

## A — Gradient fusion

- Sobel cố định, depthwise trên feature map MobileViT-S, magnitude `sqrt(gx²+gy²+eps)`.
- 1x1 projection; ba nhánh spatial/WGSA/gradient được gated bằng softmax từ global-pooled features, concatenate rồi 1x1 fusion.
- BCE giữ nguyên. Đây là cách cụ thể hóa phần "3-way gated fusion" chưa được định nghĩa chi tiết trong proposal.
- So A1 với control mới A0. Ghi số parameters, VRAM và thời gian; không khẳng định chi phí inference trước khi đo.

## B — Difficulty curriculum

- Frozen baseline inference, `eval()`, không augmentation; BCE từng training frame làm difficulty.
- Epoch 1–8 dùng 50%, 9–16 dùng 75%, 17–25 dùng 100% training records.
- Chọn phần dễ **trong từng class/manipulation** để giữ tỷ lệ nhóm và tránh giai đoạn đầu chỉ còn một class. Đây là chi tiết bổ sung có chủ ý so với sort toàn cục trong proposal.
- Shuffle tập đã chọn trong từng epoch; val/test không thay đổi. Không dùng proxy nếu control lỗi: curriculum được ghi blocked, các phương án độc lập vẫn có thể chạy.
- Final khởi tạo từ ImageNet như control; không warm-start từ FF++ control checkpoint.

## C — Temporal consistency

- Hai frame khác nhau cùng `(manipulation, video, label)`. Tránh ghép nhầm video có cùng tên ở hai nhóm.
- Inference giữ frame-level. Không giả định hai frame được sample là hai frame liền kề về thời gian.
- C0 paired λ=0 và C1 paired λ=0.1 có cùng số anchor, optimizer steps và sampling. So thêm với baseline frame-level.

## Queue sau giai đoạn chính

Cross-manipulation cho baseline và curriculum: lần lượt train độc lập trên DF/F2F/FS/NT, mỗi run 25 epochs rồi test 4 nhóm. Tổng 8 run bổ sung, báo cả mean 16 cells (có diagonal) và unseen mean (không diagonal). Mỗi curriculum dùng checkpoint control **cùng manipulation** để chấm độ khó training split.

Giai đoạn này có thể kéo dài qua sáng hôm sau; không hứa hoàn tất toàn bộ queue trong một đêm. Xem thời gian thực sau epoch đầu thay vì suy từ RTX 5090 cũ.

## Khả năng tiếp tục và báo lỗi

- `last.pt` có model, optimizer, scheduler, epoch và RNG, ghi atomically mỗi epoch; `best.pt` riêng cho inference.
- Cấu hình và manifest hash phải giữ nguyên để resume; metrics chưa có checkpoint tương ứng sẽ được loại trước khi chạy tiếp.
- Pilot yêu cầu 5 metric records hữu hạn và train loss cuối thấp hơn đầu. Không đạt thì không chạy final của ứng viên đó.
- Một job train lỗi được thử tiếp từ checkpoint một lần; lỗi độc lập không làm mất các run đã xong.
- Hugging Face upload retry riêng, không xóa local checkpoint khi lỗi. Chỉ ghi pointer sau khi SHA-256 remote khớp file local; sau đó kiểm tra commit metadata trên GitHub.
- Queue giữ máy không sleep khi tiến trình sống, không đổi thiết lập nguồn toàn hệ thống.
- `C:/sp/runs/wgn_overnight/STATUS.md`, `queue-status.json`, `events.jsonl`, `logs/` là nơi kiểm tra sáng hôm sau.
- Tạo file `C:/sp/runs/wgn_overnight/STOP_AFTER_CURRENT` để dừng sau job hiện tại. Không tắt máy nếu muốn job tiếp tục.

## Lưu checkpoint public trên Hugging Face

Theo quyết định ngày 20-10-2026, mọi `best.pt` được lưu trong model repo public `lucashwang0102/wgn-checkpoints` để chuyển máy không cần đăng nhập. GitHub chỉ lưu `CHECKPOINT.json`, checksum, config, metrics, log và kết quả trong experiment tương ứng trên nhánh `main`. Không upload `last.pt`/optimizer state hay credentials. Không báo hoàn tất nếu chưa xác minh SHA-256 trên Hugging Face và commit metadata trên GitHub.

## Cách chạy lại

```powershell
& C:\sp\.tools\py311\python.exe C:\sp\special_project\experiments\EXP-003-IMPROVEMENT-WGN\code\run_queue.py
```

Queue có khóa để từ chối hai bản chạy đồng thời và bỏ qua stage đã hoàn tất. Các thư viện được pin trong `../code/requirements.txt`; facenet-pytorch 2.6.0 cài `--no-deps` vì pin torch cũ chưa hỗ trợ Blackwell. MTCNN trên GPU thật đã được kiểm tra trước khi dùng.
