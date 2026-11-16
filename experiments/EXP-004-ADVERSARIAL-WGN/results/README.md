# EXP-004 — Kết quả đánh giá đầu tiên

**Cập nhật 2026-11-16:** Đã hoàn tất cả bốn full test cohorts. Xem [tổng quan](cross-dataset-overview.md), [đủ 16 tổ hợp dataset × method và CSV full precision](tables/README.md), [Celeb-DF-v2](full-celebdf-report.md) và [WildDeepfake](full-wilddeepfake-report.md). Phần dưới giữ nguyên báo cáo lần đầu.

Ngày chạy: 2026-11-15. Victim: WGN reproduce của EXP-002, checkpoint cố định. EXP-005 không thuộc phạm vi báo cáo này.

**Cập nhật:** đã hoàn thành mở rộng toàn bộ 132.116 DFDC test frames, FAA ASR **84,02% (36.072/42.932)**. Xem [báo cáo full DFDC](full-dfdc-report.md) và [evidence full](full-dfdc-evaluation.json). Phần DFDC bên dưới giữ nguyên kết quả cohort 2.000 ảnh ban đầu để đối chiếu.

**WGN bị đánh lừa bởi nhiễu DCT đầu vào trong cấu hình tái dựng đã khóa**: FAA đạt ASR 51,21% trên FF++ c23 và 83,50% trên cohort DFDC. Đây là kết quả của `jia-faa-reconstruction`, chưa phải tái hiện chính xác code tác giả Jia.

## Dữ liệu và clean continuity

| Population | Frames | Real / Fake | Clean ACC | Clean AUC |
|---|---:|---:|---:|---:|
| FF++ c23 test | 11,200 | 5.600 / 5.600 | 0.939196 | 0.982102 |
| DFDC full clean gate | 132,116 | Toàn manifest | 0.635971 | 0.690770 |
| DFDC attack cohort | 2,000 | 1.000 / 1.000 | 0.618000 | 0.677458 |

Cả hai clean gates đầy đủ đều đạt tolerance tuyệt đối 0,001 so với EXP-002; record identity khớp baseline. FF++ được khôi phục 22.400 ảnh val/test c23; DFDC 132.116 ảnh. Bảy shard đã kiểm tra checksum và toàn bộ ảnh thuộc population đã decode. Revision HF: `e83e1c1d0b763f7fe324c5b57cd4c21e5f1529a2`. Crop hiện có đủ cho attack sau crop; chưa cần tải lại video gốc cho threat model này.

DFDC cohort được người dùng chọn là 1.000 Fake + 1.000 Real. Sampler seed 1024 ưu tiên nhiều video, không dùng clean/attack score để chọn; kết quả là một frame từ mỗi video trong 2.000 video. Đây không phải đánh giá mọi frame/video hoặc prevalence tự nhiên của DFDC.

## Threat model và cấu hình

- White-box, Fake→Real, threshold 0,5; chỉ attack Fake được phát hiện đúng lúc clean. Real và Fake đã false-negative giữ nguyên. WGN eval/frozen; không huấn luyện, không đổi checkpoint.
- Giữ nguyên EXP-002 RGB resize 256×256 / ToTensor, không normalization hay augmentation. Attack xảy ra sau crop/decode; chưa đánh giá độ bền qua tái nén, recrop hoặc pipeline video đầu cuối.
- FGSM: pixel L∞=4/255. PGD: cùng budget, alpha=1/255, 10 updates, 5 trajectories gồm một clean start và bốn random starts; giữ best iterate.
- FAA: orthonormal block DCT 8×8, M=`energy-proportion`, P~U(0,1), P-step=0,01, 10 updates, global per-image DCT L∞=0,1; per-image stopping khi evasion, giữ best BCE. M/norm/budget/feasibility là lựa chọn tái dựng, không phải hyperparameter đã xác minh từ tác giả.
- `frequency-init-control`: cùng M/P/feasibility và cùng khởi tạo ngẫu nhiên, không gradient. FAA và control seed=1026; PGD seed=1025; cohort seed=1024. Batch=32, workers=4.
- Các JSON [FF++](../code/configs/final_reconstruction_ffpp.json) và [DFDC](../code/configs/final_reconstruction_dfdc.json), cùng danh sách cohort runtime, được khóa trước final attack. Không tuning lại bằng final-test ASR.
- True-Fake BCE dùng `softplus(-logit)` để tránh gradient FP32 bị triệt tiêu ở logits dương lớn. Regression test logit=40 đã qua.

Chi tiết công thức và những điểm khác paper: [V3 protocol](../docs/V3-PROTOCOL.md), [audit Jia](../docs/JIA-ALGORITHM-SPEC.md).

## Conditional Fake→Real ASR

ASR chỉ lấy mẫu số là Fake clean-correct: FF++ **5.333/5.600**, DFDC **606/1.000**. Không tính 267 và 394 false negatives vốn có thành attack success.

| Method | FF++ flips / eligible | ASR | DFDC flips / eligible | ASR |
|---|---:|---:|---:|---:|
| fgsm | 3,119/5,333 | 58.48% | 335/606 | 55.28% |
| pgd | 5,333/5,333 | 100.00% | 606/606 | 100.00% |
| frequency-init-control | 324/5,333 | 6.08% | 143/606 | 23.60% |
| jia-faa-reconstruction | 2,731/5,333 | 51.21% | 506/606 | 83.50% |

Không xếp hạng sức mạnh giữa pixel attacks và FAA từ bảng này: budget thuộc hai miền/đơn vị khác nhau, chưa được ghép tương đương.

FAA so với đối chứng không gradient:

- FF++: FAA ASR 95% cluster-bootstrap interval **47.19–54.95%**. Paired ASR tăng **45.13 điểm phần trăm**, interval 42.27–48.25. Có 2,407 flips chỉ FAA đạt; 324 flips cả hai đạt; 0 flips chỉ control đạt.
- DFDC: FAA ASR 95% cluster-bootstrap interval **80.43–86.44%**. Paired ASR tăng **59.90 điểm phần trăm**, interval 55.94–63.53. Có 363 flips chỉ FAA đạt; 143 flips cả hai đạt; 0 flips chỉ control đạt.

Intervals dùng 1.000 bootstrap replicates, seed 1024. FF++ gom 70 official source pairs (hai video Real và các biến thể giả mạo cùng nhóm). DFDC dùng video IDs, thiếu liên kết original-source nên interval chỉ mang tính exploratory. Bootstrap [100%,100%] của PGD phản ánh tất cả mẫu đã quan sát đều bị fool; không phải chứng nhận ASR tổng thể bằng 100%.

## FAA theo manipulation và video FF++

| Manipulation | Flips / eligible frames | ASR |
|---|---:|---:|
| FF-DF | 614/1,358 | 45.21% |
| FF-F2F | 558/1,342 | 41.58% |
| FF-FS | 486/1,366 | 35.58% |
| FF-NT | 1,073/1,267 | 84.69% |

Video-level FAA: **233/542** Fake videos clean-correct bị evasion (**42,99%**), dùng trung bình score các frames được chọn. Có 700 video/manipulation records (140 Real, 560 Fake variants). Trên DFDC, mỗi video có một frame trong cohort nên số liệu video và frame của cohort trùng nhau.

## Chất lượng ảnh và AUC sau attack

PSNR/SSIM dưới đây lấy trung bình riêng trên Fake clean-correct, kể cả trường hợp thuật toán giữ nguyên ảnh. Tất cả eligible frames của bốn phương pháp trong lần chạy này có nhiễu khác 0. Không gộp Real không đổi để làm đẹp trung bình.

| Dataset | Method | PSNR mean (dB) | SSIM mean | Attacked-Fake / clean-Real AUC |
|---|---|---:|---:|---:|
| FF++ | fgsm | 36.127 | 0.864963 | 0.895036 |
| FF++ | pgd | 40.058 | 0.939777 | 0.034842 |
| FF++ | frequency-init-control | 42.942 | 0.994251 | 0.970653 |
| FF++ | jia-faa-reconstruction | 43.433 | 0.994643 | 0.921229 |
| DFDC | fgsm | 36.168 | 0.859665 | 0.530420 |
| DFDC | pgd | 40.071 | 0.934941 | 0.160463 |
| DFDC | frequency-init-control | 42.952 | 0.990221 | 0.625673 |
| DFDC | jia-faa-reconstruction | 43.250 | 0.990633 | 0.520049 |

FAA final DCT L∞ tối đa xấp xỉ 0,10000007 (trong tolerance FP32 của budget 0,1). FAA pixel L∞ trung bình: FF++ 0,012629; DFDC 0,012661. Đây là đo lường đầu ra, không phải pixel-budget đặt cho FAA. SSIM cao không thay thế nghiên cứu cảm nhận bằng mắt.

## Quan sát cơ chế WGN

Hook tại WGSA ghi mean, absolute mean, variance và energy theo bốn Haar kernels của feature guide, cùng gates và attention trước/sau attack. Đây là Haar trong feature space; khác với block DCT của input dùng tạo attack. Số liệu theo band và theo manipulation/outcome có trong JSON evidence.

| Dataset | FAA outcome | Frames | Gate MAE mean | Attention MAE mean | Variance MAE mean |
|---|---|---:|---:|---:|---:|
| FF++ | success | 2,731 | 0.001346 | 0.153801 | 0.151651 |
| FF++ | failure | 2,602 | 0.001127 | 0.121977 | 0.082023 |
| DFDC | success | 506 | 0.000861 | 0.113549 | 0.112460 |
| DFDC | failure | 100 | 0.000620 | 0.086758 | 0.070298 |

Trong cohort đã đo, các nhóm thành công có drift attention/gate/variance trung bình cao hơn nhóm thất bại. Đây là liên hệ mô tả; nhóm khác nhau về ảnh, manipulation, clean confidence và số bước do stopping. Chưa xác định hướng nhân quả và chưa chứng minh WGSA là nguồn gây yếu điểm. Energy drift FF++ gần tương đương giữa hai nhóm, nên không thể kết luận mọi statistic đều tăng cùng evasion.

## Chi phí và kiểm chứng

| Dataset | FGSM (s) | PGD (s) | Frequency control (s) | FAA (s) | Peak allocated VRAM cao nhất (MiB) |
|---|---:|---:|---:|---:|---:|
| FF++ | 38.42 | 661.11 | 27.37 | 228.77 | 5717.9 |
| DFDC | 6.95 | 77.95 | 4.97 | 28.23 | 4325.2 |

Thời gian gồm loader, attack, diagnostics, quality và ghi output; không phải microbenchmark kernel hoặc thời gian gồm restore/clean gates. Máy RTX 4080 SUPER, Python 3.11.14, torch 2.7.1+cu128. Dependency check đạt; **35 CPU tests passed**.

Cả hai final runs có `complete=true`. Audit hậu chạy kiểm tra đúng cohort/config hash đã khóa; không trùng ảnh; labels/video/manipulation đúng; cùng thứ tự và clean scores giữa methods; Real/false-negative giữ nguyên; final bounds; best-iterate PGD/FAA không làm score xấu hơn clean theo hướng mục tiêu. Hash của mọi module attack/evaluation chung giữa hai dataset trùng nhau. Không có huấn luyện hoặc thay checkpoint.

## Evidence và giới hạn

- [Compact evidence JSON](initial-evaluation.json): counts, CIs, chất lượng/quantiles, band statistics, paired table, metadata, source hashes và hash raw outputs.
- Runtime ngoài Git: `/home/naeem/Downloads/s1123570_sp1/exp04-runtime`. Có `cohorts/`, clean gates, `runs/final_ffpp_reconstruction_001/`, `runs/final_dfdc_reconstruction_001/`, source snapshots/diff, per-frame JSONL, logs, float32 examples và PNG/heatmap. Ví dụ lưu là Fake eligible đầu tiên, không được chọn theo success; score tương ứng nằm trong compact evidence.
- Mới một seed và một cấu hình reconstruction. M và feasibility chưa xác minh bằng code tác giả; không báo đây là ASR tái hiện chính xác Jia hoặc so trực tiếp với bảng paper.
- DFDC chỉ là cohort cân bằng 2.000 frames; chưa attack toàn bộ 132.116 frames. Kết luận giới hạn vào checkpoint, population và threat model đã ghi.
- Cần thảo luận tiếp về fidelity/M, sensitivity trên development và đối chứng causal WGSA/backbone trước các kết luận cơ chế mạnh hơn. Chưa chọn kiến trúc mới, chưa chạy defense/training.

Nguồn thuật toán: [Jia et al., CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/papers/Jia_Exploring_Frequency_Adversarial_Attacks_for_Face_Forgery_Detection_CVPR_2022_paper.pdf). Đặc tả tái dựng của dự án và output thực tế là căn cứ cho số liệu báo cáo ở đây.
