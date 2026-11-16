# EXP-004 — Full DFDC test evaluation

Ngày chạy: 2026-11-15, Asia/Taipei. Đây là toàn bộ test manifest đã restore, không phải toàn bộ kho video DFDC gốc. Không gộp train/validation.

**FAA reconstruction làm 36,072/42,932 Fake clean-correct chuyển thành Real: ASR 84.02%.**

## Phạm vi và tính liên tục

- 132.116 frames: 63.265 Real và 68.851 Fake. Cohort fingerprint, manifest và checkpoint khớp clean gate đã qua kiểm tra.
- Checkpoint EXP-002 frozen; preprocessing và bốn phương pháp giữ nguyên. Config mới chỉ đổi max_samples từ 2000 sang 0. Danh sách cohort và config được khóa trước attack.
- Có 42,932 Fake nhận diện đúng trước attack; 25,919 baseline false negatives giữ nguyên và không tính là attack success. Toàn bộ Real giữ nguyên.
- Clean ACC=0.635971, AUC=0.690770; đạt clean-reference tolerance 0,001.
- DCT attack tác động lên input RGB sau crop/decode; chưa đánh giá tái nén hoặc pipeline video đầu cuối.
- FAA là bản tái dựng theo Jia, chưa xác minh code tác giả. M=energy-proportion; block=8; DCT L∞ epsilon=0,1; P-step=0,01; 10 updates, first-evasion stopping. FGSM/PGD pixel L∞=4/255; PGD alpha=1/255, 10 updates, 5 trajectories. Seed=1024, batch=32.

## Kết quả và so sánh cohort ban đầu

| Method | Full flips / eligible | Full ASR | ASR trên cohort 2.000 ảnh | Full attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|---:|
| fgsm | 23,731/42,932 | 55.28% | 55.28% | 0.545763 |
| pgd | 42,932/42,932 | 100.00% | 100.00% | 0.155826 |
| frequency-init-control | 9,617/42,932 | 22.40% | 23.60% | 0.639967 |
| jia-faa-reconstruction | 36,072/42,932 | 84.02% | 83.50% | 0.535506 |

Cùng tham số/seed nhưng thay population sẽ thay batch composition và chuỗi random cho từng ảnh; không coi chênh lệch full/cohort là một phép so sánh paired về thuật toán. Không xếp hạng pixel attacks và FAA như ngân sách tương đương.

FAA ASR 95% video-cluster-bootstrap interval: **82.47–85.56%**. Paired FAA/control ASR tăng **61.62 điểm phần trăm**.

Paired gain interval: **60.19–63.13 điểm phần trăm**. Trong 42.932 Fake đủ điều kiện: 26.464 flips chỉ FAA đạt, 9.608 cả hai đạt, 9 chỉ control đạt, 6.851 cả hai không đạt. FAA không giữ riêng P0 trước update đầu tiên nên không bảo đảm thắng initialization control trên từng ảnh; điều này đã được khai báo trong protocol trước chạy.
Bootstrap 1.000 replicates. DFDC thiếu original-source linkage nên intervals vẫn exploratory; nhiều frames/video không phải các quan sát độc lập.

Video-level FAA: 1,272/1,540, ASR=82.60%, mean score trên toàn bộ frames được chọn của video. Tổng 4,704 video records.

## Chất lượng ảnh và chi phí

| Method | PSNR mean (dB) | SSIM mean | Runtime (s) | Peak allocated VRAM (MiB) |
|---|---:|---:|---:|---:|
| fgsm | 36.158 | 0.859158 | 404.54 | 5431.5 |
| pgd | 40.046 | 0.934710 | 5497.41 | 5505.5 |
| frequency-init-control | 42.935 | 0.990641 | 317.85 | 742.3 |
| jia-faa-reconstruction | 43.236 | 0.991080 | 1627.45 | 5720.7 |

Chất lượng chỉ tổng hợp trên Fake clean-correct; PSNR null nghĩa là vô hạn nếu ảnh không đổi, finite-count có trong JSON. SSIM cao không chứng minh nhiễu không nhìn thấy. Runtime gồm loader, attack, quality, diagnostics và ghi output.

FAA giữ nguyên clean ở 10/42.932 ảnh đủ điều kiện; PSNR trung bình hữu hạn dùng 42.922 ảnh, trong khi SSIM/MSE bao gồm đủ 42.932 ảnh. Final DCT L∞ tối đa 0,10000007, đạt tolerance FP32 của budget 0,1. Pixel L∞ tối đa FAA=0,016718; FAA không bị ràng buộc bởi pixel budget 4/255 của FGSM/PGD. Tổng thời gian bốn methods khoảng **2 giờ 11 phút**, riêng FAA khoảng **27 phút**; không gồm restore và clean gates.

## Diagnostics và giới hạn

| FAA outcome | Frames | Gate MAE mean | Attention MAE mean | Variance MAE mean |
|---|---:|---:|---:|---:|
| success | 36,072 | 0.000816 | 0.117741 | 0.116418 |
| failure | 6,860 | 0.000819 | 0.089419 | 0.060174 |

Đây là liên hệ mô tả ở feature Haar/WGSA; chưa có đối chứng causal và chưa quy nguyên nhân riêng cho WGSA. Một checkpoint, một seed và một cấu hình không bao phủ mọi attack. Không thực hiện training hoặc thay đổi kiến trúc.

Ở full dataset, attention và variance drift trung bình cao hơn trong nhóm thành công; **gate drift gần tương đương** giữa hai nhóm (0,000816 so với 0,000819). Vì vậy, quan sát gate drift cao hơn ở success trong cohort nhỏ không được xác nhận theo cùng chiều trên full. Dữ liệu hiện tại xác nhận vulnerability nhưng chưa đủ để chọn gate làm nguyên nhân hoặc mục tiêu phòng vệ riêng.

## Evidence

- [Full compact evidence](full-dfdc-evaluation.json), [kết quả cohort ban đầu](INITIAL-EVALUATION-REPORT.md).
- [Cấu hình full đã khóa](../code/configs/final_reconstruction_dfdc_full.json); [protocol](../docs/V3-PROTOCOL.md).
- Runtime: `exp04-runtime/runs/final_dfdc_full_reconstruction_001/`; có completion marker, per-frame JSONL, source snapshots/diff, metadata, video analyses và ví dụ float32/PNG. Cohort: `exp04-runtime/cohorts/full_dfdc.json`.
- Kiểm tra hậu chạy: cohort/config và source identity, unique records, paired clean scores, Real/false negatives không đổi, bounds, best-iterate và consistency counts đều qua kiểm tra. Ảnh và checkpoint giữ ngoài Git.
