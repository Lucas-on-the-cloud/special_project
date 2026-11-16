# EXP-004 — Complete result tables

Bốn full processed test manifests; frozen WGN. Giá trị hiển thị được làm tròn; CSV giữ full precision từ evidence JSON. Không tính train/validation vào population báo cáo.

## 1. Cohort và clean reference

| Dataset | Frames | Real | Fake | Video/sequence | Eligible Fake | Baseline Fake FN | Clean ACC | Clean AUC |
|---|---|---|---|---|---|---|---|---|
| FF++ c23 | 11200 | 5600 | 5600 | 700 | 5333 | 267 | 93.92% | 98.21% |
| DFDC | 132116 | 63265 | 68851 | 4704 | 42932 | 25919 | 63.60% | 69.08% |
| Celeb-DF-v2 official-direct | 16576 | 5696 | 10880 | 518 | 8278 | 2602 | 64.38% | 64.70% |
| WildDeepfake | 165662 | 58659 | 107003 | 806 | 88521 | 18482 | 67.73% | 70.92% |

ASR = Fake clean-correct mới chuyển thành Real / tất cả Fake clean-correct. Real và baseline Fake false negatives giữ nguyên. Video/sequence records không đồng nghĩa independent source videos.

## 2. Frame attack results — đủ 16 tổ hợp

| Dataset | Method | Flips / eligible | ASR | 95% cluster CI | Attacked ACC | Attacked AUC |
|---|---|---|---|---|---|---|
| ffpp | fgsm | 3119/5333 | 58.48% | 52.49%–64.25% | 66.07% | 89.50% |
| ffpp | pgd | 5333/5333 | 100.00% | 100.00%–100.00% | 46.30% | 3.48% |
| ffpp | frequency-init-control | 324/5333 | 6.08% | 4.60%–7.76% | 91.03% | 97.07% |
| ffpp | jia-faa-reconstruction | 2731/5333 | 51.21% | 47.19%–54.95% | 69.54% | 92.12% |
| dfdc | fgsm | 23731/42932 | 55.28% | 53.20%–57.39% | 45.63% | 54.58% |
| dfdc | pgd | 42932/42932 | 100.00% | 100.00%–100.00% | 31.10% | 15.58% |
| dfdc | frequency-init-control | 9617/42932 | 22.40% | 21.28%–23.57% | 56.32% | 64.00% |
| dfdc | jia-faa-reconstruction | 36072/42932 | 84.02% | 82.47%–85.56% | 36.29% | 53.55% |
| celebdf | fgsm | 1487/8278 | 17.96% | 14.99%–21.11% | 55.41% | 52.78% |
| celebdf | pgd | 8278/8278 | 100.00% | 100.00%–100.00% | 14.44% | 5.37% |
| celebdf | frequency-init-control | 1518/8278 | 18.34% | 16.51%–20.22% | 55.22% | 55.37% |
| celebdf | jia-faa-reconstruction | 7946/8278 | 95.99% | 94.86%–97.02% | 16.45% | 31.67% |
| wilddeepfake | fgsm | 21134/88521 | 23.87% | 19.31%–28.96% | 54.98% | 53.14% |
| wilddeepfake | pgd | 88521/88521 | 100.00% | 100.00%–100.00% | 14.30% | 4.56% |
| wilddeepfake | frequency-init-control | 20281/88521 | 22.91% | 18.51%–27.14% | 55.49% | 56.98% |
| wilddeepfake | jia-faa-reconstruction | 82059/88521 | 92.70% | 89.85%–94.65% | 18.20% | 33.37% |

ACC/AUC sau attack dùng attacked Fake + clean Real. Bootstrap 1.000 replicates; FF++ theo 70 official source pairs, external theo video/sequence IDs. External intervals exploratory do thiếu original-source/identity linkage.

## 3. Chất lượng ảnh và chi phí

| Dataset | Method | Finite PSNR n | PSNR mean dB | SSIM mean | Pixel L∞ max | DCT L∞ max | Runtime s | Peak allocated MiB |
|---|---|---|---|---|---|---|---|---|
| ffpp | fgsm | 5333 | 36.127 | 0.864963 | 0.015686303 | 0.125490189 | 38.418 | 5431.5 |
| ffpp | pgd | 5333 | 40.058 | 0.939777 | 0.015686303 | 0.093137249 | 661.112 | 5505.5 |
| ffpp | frequency-init-control | 5333 | 42.942 | 0.994251 | 0.013205193 | 0.100000069 | 27.373 | 742.3 |
| ffpp | jia-faa-reconstruction | 5333 | 43.433 | 0.994643 | 0.013183467 | 0.100000069 | 228.771 | 5717.9 |
| dfdc | fgsm | 42932 | 36.158 | 0.859158 | 0.015686303 | 0.125490427 | 404.540 | 5431.5 |
| dfdc | pgd | 42932 | 40.046 | 0.934710 | 0.015686303 | 0.111274511 | 5497.410 | 5505.5 |
| dfdc | frequency-init-control | 42932 | 42.935 | 0.990641 | 0.016627692 | 0.100000069 | 317.846 | 742.3 |
| dfdc | jia-faa-reconstruction | 42922 | 43.236 | 0.991080 | 0.016718363 | 0.100000069 | 1627.445 | 5720.7 |
| celebdf | fgsm | 8278 | 36.116 | 0.851677 | 0.015686303 | 0.125490203 | 58.932 | 5433.9 |
| celebdf | pgd | 8278 | 40.056 | 0.932787 | 0.015686303 | 0.097549014 | 1045.319 | 5505.5 |
| celebdf | frequency-init-control | 8278 | 42.872 | 0.993225 | 0.012983032 | 0.100000069 | 41.023 | 742.6 |
| celebdf | jia-faa-reconstruction | 8276 | 43.122 | 0.993540 | 0.013085280 | 0.100000061 | 290.033 | 5721.1 |
| wilddeepfake | fgsm | 88521 | 36.125 | 0.848884 | 0.015686303 | 0.125490233 | 594.985 | 5430.9 |
| wilddeepfake | pgd | 88521 | 40.054 | 0.931582 | 0.015686303 | 0.105392158 | 11189.502 | 5501.4 |
| wilddeepfake | frequency-init-control | 88521 | 42.910 | 0.993214 | 0.013594300 | 0.100000076 | 508.164 | 742.3 |
| wilddeepfake | jia-faa-reconstruction | 88501 | 43.172 | 0.993521 | 0.013636611 | 0.100000076 | 2897.148 | 5719.0 |

Quality/norm summaries condition on eligible Fake. PSNR của ảnh không đổi là vô hạn, không đi vào finite mean; SSIM finite count bằng eligible count. CSV còn có MSE, DCT L2, median, p05/p95, min/max và finite counts. Runtime gồm loader/attack/quality/diagnostics/ghi output; peak allocated khác tổng reserved/device memory. SSIM không chứng minh imperceptibility.

## 4. Video/sequence aggregation

| Dataset | Method | Video/sequence records | Flips / eligible Fake groups | Group ASR | Clean AUC | Attacked AUC |
|---|---|---|---|---|---|---|
| ffpp | fgsm | 700 | 323/542 | 59.59% | 99.44% | 82.58% |
| ffpp | pgd | 700 | 542/542 | 100.00% | 99.44% | 7.13% |
| ffpp | frequency-init-control | 700 | 25/542 | 4.61% | 99.44% | 98.71% |
| ffpp | jia-faa-reconstruction | 700 | 233/542 | 42.99% | 99.44% | 93.00% |
| dfdc | fgsm | 4704 | 895/1540 | 58.12% | 69.67% | 47.88% |
| dfdc | pgd | 4704 | 1540/1540 | 100.00% | 69.67% | 17.80% |
| dfdc | frequency-init-control | 4704 | 378/1540 | 24.55% | 69.67% | 62.08% |
| dfdc | jia-faa-reconstruction | 4704 | 1272/1540 | 82.60% | 69.67% | 43.88% |
| celebdf | fgsm | 518 | 53/296 | 17.91% | 70.12% | 57.08% |
| celebdf | pgd | 518 | 296/296 | 100.00% | 70.12% | 1.45% |
| celebdf | frequency-init-control | 518 | 59/296 | 19.93% | 70.12% | 55.56% |
| celebdf | jia-faa-reconstruction | 518 | 289/296 | 97.64% | 70.12% | 11.33% |
| wilddeepfake | fgsm | 806 | 84/372 | 22.58% | 71.55% | 53.84% |
| wilddeepfake | pgd | 806 | 372/372 | 100.00% | 71.55% | 6.78% |
| wilddeepfake | frequency-init-control | 806 | 59/372 | 15.86% | 71.55% | 57.18% |
| wilddeepfake | jia-faa-reconstruction | 806 | 342/372 | 91.94% | 71.55% | 22.86% |

Group score là mean frame score trên cohort đã chọn, threshold 0.5; không đồng nhất frame eligibility và video/sequence eligibility.

## 5. Theo manipulation / Fake group

| Dataset | Method | Fake group | Fake frames | Flips / eligible | ASR |
|---|---|---|---|---|---|
| ffpp | fgsm | FF-DF | 1400 | 542/1358 | 39.91% |
| ffpp | fgsm | FF-F2F | 1400 | 814/1342 | 60.66% |
| ffpp | fgsm | FF-FS | 1400 | 1046/1366 | 76.57% |
| ffpp | fgsm | FF-NT | 1400 | 717/1267 | 56.59% |
| ffpp | pgd | FF-DF | 1400 | 1358/1358 | 100.00% |
| ffpp | pgd | FF-F2F | 1400 | 1342/1342 | 100.00% |
| ffpp | pgd | FF-FS | 1400 | 1366/1366 | 100.00% |
| ffpp | pgd | FF-NT | 1400 | 1267/1267 | 100.00% |
| ffpp | frequency-init-control | FF-DF | 1400 | 35/1358 | 2.58% |
| ffpp | frequency-init-control | FF-F2F | 1400 | 70/1342 | 5.22% |
| ffpp | frequency-init-control | FF-FS | 1400 | 36/1366 | 2.64% |
| ffpp | frequency-init-control | FF-NT | 1400 | 183/1267 | 14.44% |
| ffpp | jia-faa-reconstruction | FF-DF | 1400 | 614/1358 | 45.21% |
| ffpp | jia-faa-reconstruction | FF-F2F | 1400 | 558/1342 | 41.58% |
| ffpp | jia-faa-reconstruction | FF-FS | 1400 | 486/1366 | 35.58% |
| ffpp | jia-faa-reconstruction | FF-NT | 1400 | 1073/1267 | 84.69% |
| dfdc | fgsm | DFDC_Fake | 68851 | 23731/42932 | 55.28% |
| dfdc | pgd | DFDC_Fake | 68851 | 42932/42932 | 100.00% |
| dfdc | frequency-init-control | DFDC_Fake | 68851 | 9617/42932 | 22.40% |
| dfdc | jia-faa-reconstruction | DFDC_Fake | 68851 | 36072/42932 | 84.02% |
| celebdf | fgsm | CelebDFv2Official_fake | 10880 | 1487/8278 | 17.96% |
| celebdf | pgd | CelebDFv2Official_fake | 10880 | 8278/8278 | 100.00% |
| celebdf | frequency-init-control | CelebDFv2Official_fake | 10880 | 1518/8278 | 18.34% |
| celebdf | jia-faa-reconstruction | CelebDFv2Official_fake | 10880 | 7946/8278 | 95.99% |
| wilddeepfake | fgsm | WildDeepfake_Fake | 107003 | 21134/88521 | 23.87% |
| wilddeepfake | pgd | WildDeepfake_Fake | 107003 | 88521/88521 | 100.00% |
| wilddeepfake | frequency-init-control | WildDeepfake_Fake | 107003 | 20281/88521 | 22.91% |
| wilddeepfake | jia-faa-reconstruction | WildDeepfake_Fake | 107003 | 82059/88521 | 92.70% |

## 6. FAA và paired initialization control

| Dataset | Both flip | FAA only | Control only | Neither | FAA−control pp | 95% difference CI pp |
|---|---|---|---|---|---|---|
| ffpp | 324 | 2407 | 0 | 2602 | 45.13 | 42.27–48.25 |
| dfdc | 9608 | 26464 | 9 | 6851 | 61.62 | 60.19–63.13 |
| celebdf | 1516 | 6430 | 2 | 330 | 77.65 | 75.99–79.45 |
| wilddeepfake | 20263 | 61796 | 18 | 6444 | 69.79 | 65.69–73.31 |

Control-only outcomes được giữ nguyên: FAA không giữ riêng P0 initialization trước update đầu tiên. Không sửa thuật toán sau test để loại các case này.

## 7. FAA diagnostics theo thành công / thất bại

| Dataset | Outcome | Frames | Gate MAE | Attention MAE | Variance MAE | Energy MAE |
|---|---|---|---|---|---|---|
| ffpp | success | 2731 | 0.001346137 | 0.153801456 | 0.151651294 | 0.276307823 |
| ffpp | failure | 2602 | 0.001126637 | 0.121976505 | 0.082022860 | 0.277310440 |
| dfdc | success | 36072 | 0.000816218 | 0.117740822 | 0.116418484 | 0.228957395 |
| dfdc | failure | 6860 | 0.000818631 | 0.089419239 | 0.060173973 | 0.194062002 |
| celebdf | success | 7946 | 0.001511776 | 0.132683346 | 0.132151154 | 0.261099609 |
| celebdf | failure | 332 | 0.002338204 | 0.146025654 | 0.106531235 | 0.416683246 |
| wilddeepfake | success | 82059 | 0.001655274 | 0.154099876 | 0.119767861 | 0.297216658 |
| wilddeepfake | failure | 6462 | 0.002764537 | 0.148898582 | 0.093986756 | 0.489059708 |

Đây là liên hệ mô tả, không quy nguyên nhân riêng cho WGSA. `mechanism-outcomes.csv` có đủ cả bốn methods; `haar-bands.csv` có 320 rows signed/absolute mean, variance, energy và gates theo từng kernel. Index kernel 0–3 theo thứ tự buffer của frozen WGN, không suy đoán quy ước đặt tên LH/HL.

## 8. Protocol và provenance

Frozen checkpoint SHA256 `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`. Pixel FGSM/PGD L∞=4/255; PGD alpha=1/255,10 updates,5 trajectories. FAA: block8, energy-proportion M, global DCT L∞=0.1, P-step=0.01,10 updates, first-evasion stopping. Seed1024, batch32. Pixel/DCT budgets khác đơn vị; không coi đây là xếp hạng cùng ngân sách. FAA là reconstruction, chưa author-verified exact reproduction.

Các bảng chính dùng full DFDC132.116 frames; cohort DFDC2.000 ảnh ban đầu vẫn được giữ trong `initial-evaluation.json` để truy vết, không trộn vào full results.

Nguồn: [initial evidence (FF++ full)](../initial-evaluation.json), [DFDC full](../full-dfdc-evaluation.json), [Celeb-DF-v2 full](../full-celebdf-evaluation.json), [WildDeepfake full](../full-wilddeepfake-evaluation.json). [Tổng quan](../cross-dataset-overview.md).

CSV fractions nằm trong[0,1] cho ASR/ACC/AUC; các cột có `_pp` (nếu có) dùng điểm phần trăm. `all-numeric-values.csv` giữ mọi numeric/null/bool leaf theo RFC6901 JSON pointer, gồm các thống kê chưa đưa thành cột riêng. JSON `null` không bị biến thành0. Không công bố ảnh/weights/raw per-frame logs trong Git.
