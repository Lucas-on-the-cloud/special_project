# EXP-004 — Bốn full processed test datasets

Hoàn tất extension và hậu kiểm: 2026-11-16, 02:31:12 Asia/Taipei. Cả bốn full processed test cohorts đã chạy; không gộp train/validation và không tuyên bố bao phủ mọi video gốc của các dataset.

| Dataset | Frames | Clean frame AUC | FAA flips / eligible Fake | FAA ASR | Init-control ASR | PGD ASR |
|---|---:|---:|---:|---:|---:|---:|
| [FF++ c23](README.md) | 11,200 | 98.21% | 2,731/5,333 | 51.21% | 6.08% | 100.00% |
| [DFDC](full-dfdc-report.md) | 132,116 | 69.08% | 36,072/42,932 | 84.02% | 22.40% | 100.00% |
| [Celeb-DF-v2 official-direct](full-celebdf-report.md) | 16,576 | 64.70% | 7,946/8,278 | 95.99% | 18.34% | 100.00% |
| [WildDeepfake](full-wilddeepfake-report.md) | 165,662 | 70.92% | 82,059/88,521 | 92.70% | 22.91% | 100.00% |

Tổng 325.554 test frames: 133.220 Real / 192.334 Fake. Có 145.064 Fake clean-correct; baseline false-negative Fake và Real giữ nguyên. ASR là tỷ lệ mới chuyển Fake→Real trên population clean-correct riêng từng dataset, không phải tỷ lệ trên toàn bộ frames và không tự xếp hạng độ khó dataset.

Frozen EXP-002 checkpoint SHA256 `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`. Core attack/quality/diagnostics và tham số giữ nguyên qua bốn bộ. FAA là reconstruction theo Jia: block8, M=energy-proportion, DCT L∞0.1, P-step0.01, 10 updates, first-evasion stopping. PGD pixel L∞4/255, alpha1/255, 10 updates, 5 trajectories. Seed 1024, batch 32. Budget pixel/DCT khác đơn vị; không diễn giải ASR như đối chứng cùng ngân sách.

| Dataset | FAA 95% cluster-bootstrap interval | FAA finite PSNR mean (dB) | FAA SSIM mean |
|---|---:|---:|---:|
| FF++ c23 | 47.19–54.95% | 43.433 | 0.994643 |
| DFDC | 82.47–85.56% | 43.236 | 0.991080 |
| Celeb-DF-v2 official-direct | 94.86–97.02% | 43.122 | 0.993540 |
| WildDeepfake | 89.85–94.65% | 43.172 | 0.993521 |

Bootstrap 1.000 replicates: FF++ theo 70 official source pairs; external theo video/sequence IDs và intervals exploratory do thiếu original-source/identity linkage. Nhiều frames không tạo thành các quan sát độc lập. PSNR finite mean loại ảnh không đổi (vô hạn); finite counts/extrema nằm trong evidence từng bộ. SSIM không chứng minh imperceptibility.

Celeb-DF-v2: paired FAA−control tăng 77,65 điểm phần trăm; WildDeepfake tăng 69,79 điểm. Các flip tables/intervals và video-level metrics có trong báo cáo/evidence riêng. Control-only cases được giữ lại, không sửa thuật toán sau test.

Kết quả hỗ trợ việc frozen WGN có thể bị đánh lừa bởi input-DCT attack đã đặc tả trên cả bốn test cohorts. Chưa xác minh tương đương code/hyperparameters gốc của Jia; chưa quy nguyên nhân riêng cho WGSA hoặc kết luận về mọi attack/budget. Haar/gate/attention drift là liên hệ mô tả.

Đọc [bảng chi tiết đủ 16 tổ hợp và CSV full precision](tables/README.md), [checksum/provenance](tables/PROVENANCE.json) và [script xuất bảng](../reporting/export_tables.py). Các số liệu của nghiên cứu attack khác được quản lý riêng, không trộn vào EXP-004.
