# EXP-004 — Kế hoạch áp dụng attack Jia lên WGN

Ngày lập: 2026-11-15, Asia/Taipei.

Trạng thái: đã hoàn thành đánh giá đầu tiên E4-A/E4-B, kiểm tra hậu chạy và báo cáo. FAA reconstruction ASR: FF++ 51,21% (2.731/5.333); DFDC 83,50% (506/606). Xem [kết quả và evidence](results/INITIAL-EVALUATION-REPORT.md), [LAB-STATUS](docs/LAB-STATUS.md) và [protocol V3](docs/V3-PROTOCOL.md). Mức claim là bản tái dựng có đặc tả đầy đủ, chưa xác minh tương đương code tác giả. Cross-compression/Hybrid/transfer và đối chứng causal có training vẫn là follow-up riêng.

Mở rộng full DFDC theo yêu cầu người dùng cũng **đã hoàn thành**: 132.116 test frames, FAA 84,02% (36.072/42.932), control 22,40%; giữ nguyên cấu hình và checkpoint. Cohort/config/source/bounds/clean continuity đều qua đối soát. [Báo cáo full DFDC](results/full-dfdc-report.md) và [evidence](results/full-dfdc-evaluation.json). Không thực hiện training/đối chứng causal hoặc thiết kế kiến trúc mới.

## Mục tiêu và phạm vi

Mở rộng full Celeb-DF-v2 official-direct (16.576 test frames / 518 video) và WildDeepfake processed test (165.662 frames / 806 video-sequence records) **đã hoàn tất**2026-11-16,02:31:12 Asia/Taipei, gồm hậu kiểm. FAA95,99% và92,70%; giữ nguyên checkpoint/cấu hình/core source từ full DFDC, clean gates và cohorts đều qua đối soát. [Tổng hợp bốn dataset](results/cross-dataset-overview.md). EXP-005 đã tự bắt đầu clean gates sau completion; đây là nghiên cứu attack riêng.

Áp dụng phương pháp tấn công trong Jia et al., CVPR 2022 lên WGN đã reproduce ở EXP-002, đo khả năng làm ảnh Fake được nhận diện thành Real trên FF++ và DFDC, rồi phân tích tác động lên frequency statistics, gating và attention của WGN.

Victim chính luôn là checkpoint EXP-002 `baseline_final/best.pt`, SHA-256 `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`. EXP-004 không thay trọng số của checkpoint này. Các mô hình đối chứng được huấn luyện về sau phải có artifact và cấu hình riêng.

- Attack chính: frequency adversarial attack (FAA) của Jia, Algorithm 1, với mức độ tái hiện được xác minh và mô tả đúng.
- Đối chứng bắt buộc: clean, FGSM, PGD có kiểm tra độ mạnh.
- Dataset bắt buộc theo thứ tự: FF++ c23, sau đó DFDC.
- Mở rộng sau kết quả chính: FF++ c40 với cùng checkpoint c23; Jia Hybrid Algorithm 2; transfer attack.
- Phạm vi đầu vào ban đầu: ảnh crop RGB 256×256 đã được chuẩn bị theo EXP-002; white-box, Fake→Real, Real giữ nguyên, threshold=0.5.
- Hou StatAttack/MStatAttack và thiết kế kiến trúc là các nghiên cứu riêng, không đổi attack, metric, đối chứng hoặc hướng diễn giải đã khóa của EXP-004. Việc xây dựng kiến trúc về sau phụ thuộc bằng chứng từ các nghiên cứu attack.

Tài liệu đầu vào: proposal của sinh viên; [paper Jia](https://openaccess.thecvf.com/content/CVPR2022/papers/Jia_Exploring_Frequency_Adversarial_Attacks_for_Face_Forgery_Detection_CVPR_2022_paper.pdf); [protocol hiện tại](docs/PROTOCOL.md); [test plan](docs/TEST_PLAN.md); audit trước chạy tại workspace `EXP04-PRE-RUN-AUDIT.md`.

Các phần giai đoạn dưới đây giữ cấu trúc kế hoạch ban đầu; bảng điểm xuất phát là lịch sử audit ban đầu, không phải trạng thái lab hiện tại. V3 đã triển khai adapter DFDC, development dùng validation, kiểm tra feasibility trong DCT space, paired initialization control và evaluator mới; V2 chỉ còn để truy vết.

## Điểm xuất phát đã kiểm tra

| Thành phần | Bằng chứng hiện có | Việc còn lại |
|---|---|---|
| GPU | RTX 4080 SUPER 16 GB, CUDA scalar/autograd hoạt động | Kiểm tra WGN forward/backward trong environment mới |
| Checkpoint | Hash đúng, strict-load CPU thành công | Đưa vào vị trí runtime bền vững; đo clean reference |
| FF++ | Manifest test có 11.200 record, fingerprint khớp baseline; một PNG RGB 256×256 được đọc từ shard | Restore media, kiểm tra toàn vẹn và decode |
| DFDC | Có backup và kết quả baseline lưu trong repo | Audit manifest/media riêng và bổ sung dataset adapter |
| Environment | Environment cũ dùng được CUDA nhưng khác version baseline, thiếu pytest | Tạo environment EXP-004 riêng |
| Tests | 10 hàm test CPU chạy trực tiếp đều pass; DCT khớp SciPy | Chạy pytest chuẩn và bổ sung test theo đặc tả đã chốt |
| Thuật toán | `jia-faa-adapt` là bản điều chỉnh đã ghi nhận | Đối chiếu chi tiết, sửa implementation trước kết luận nghiên cứu |

## Giai đoạn 1 — Chốt đặc tả attack và mức độ tái hiện

Đây là công việc ưu tiên đầu tiên; chưa sử dụng code hiện tại để báo cáo kết quả Jia.

1. Tìm và xác minh code chính thức, supplementary hoặc thông tin do tác giả cung cấp nếu có. Phân biệt nguồn chính thức với implementation bên thứ ba.
2. Tạo bảng đối chiếu paper → công thức/pseudocode → implementation → test. Ghi rõ chi tiết xác định được và chi tiết còn thiếu.
3. Chốt cấu trúc/chuẩn hóa DCT, kích thước block, cách tính M, khởi tạo P, cập nhật gradient, quy tắc cộng dồn, stopping và chọn kết quả.
4. Định nghĩa đầy đủ norm, miền áp dụng, đơn vị epsilon, RGB scale, ràng buộc theo block hay toàn ảnh và cách xử lý RGB hợp lệ. Đo norm trên ảnh kết quả cuối sau mọi clamp/biến đổi.
5. Tách các tham số xác minh từ tác giả khỏi các lựa chọn tái dựng của dự án. Không suy ra một giá trị epsilon trong pixel space cũng dùng được trong DCT space.
6. Chốt tên/claim: chỉ gọi exact/official reproduction khi có đủ căn cứ; nếu một phần không được đặc tả, công bố giả định và mức độ tái dựng. Không âm thầm dùng heuristic M hiện tại như công thức gốc.

**Đầu ra:** `docs/JIA-ALGORITHM-SPEC.md` dự kiến, bảng provenance và danh sách câu hỏi chưa giải quyết.

**Tiêu chí qua bước:** mọi thao tác trong thuật toán có định nghĩa thực thi, nguồn hoặc giả định rõ ràng; cách gọi phương pháp phù hợp bằng chứng. Nếu M/norm/budget vẫn chưa xác minh được, nêu giới hạn để thống nhất phạm vi trước full run. Việc chuẩn bị environment/media vẫn có thể tiếp tục.

## Giai đoạn 2 — Chuẩn bị environment và artifact trên máy lab

1. Tạo environment riêng trong workspace, không thay đổi environment đang phục vụ công việc khác.
2. Ưu tiên mốc baseline: Python 3.11, torch 2.7.1, torchvision 0.22.1, timm 1.0.15, NumPy 1.26.4, scikit-learn 1.3.2, Pillow 10.2.0, PyYAML 6.0.1; chọn wheel CUDA tương thích máy, lưu phiên bản thực tế và thêm pytest.
3. Tách requirements inference/attack khỏi preprocessing. File requirements gộp hiện có xung đột với facenet-pytorch; không cài nguyên trạng. Không cần MTCNN/OpenCV cho inference trên crop đã restore.
4. Khôi phục checkpoint và FF++/DFDC từ đúng revision Hugging Face, giữ ngoài Git. Verify checksum shard trước giải nén, kiểm tra file tồn tại và decode ảnh theo manifest. Có thể xử lý từng shard để giảm dung lượng đỉnh.
5. Lưu manifest SHA, split, label mapping, record fingerprint dùng đường dẫn tương đối ổn định. Với FF++ đối chiếu thêm fingerprint Windows của lần baseline đã lưu.
6. Chụp thông tin GPU/driver, Python executable, package versions, Git commit và trạng thái source; chạy import/pip check, CUDA check, strict checkpoint load.

**Đầu ra:** environment tái tạo được, artifact inventory, báo cáo preflight và manifest FF++/DFDC có kiểm chứng.

**Tiêu chí qua bước:** thư viện import được, CUDA hoạt động, checkpoint đúng, mọi file trong population sẽ dùng có thể đọc; không đưa media/weights/credentials vào Git.

Hiện API Hugging Face trả dataset backup là public dù tài liệu gọi private. Ghi nhận trạng thái thực tế và trao đổi với chủ dataset; kế hoạch này không thay visibility.

## Giai đoạn 3 — Hoàn thiện implementation và test

Các thay đổi dự kiến sau khi có đặc tả:

- Thực hiện FAA theo đặc tả giai đoạn 1; giữ bản `jia-faa-adapt` cũ có nhãn rõ để truy vết nếu cần.
- Bổ sung PGD random start/restarts và lựa chọn best iterate; ghi lại toàn bộ setting. FAA dừng/chọn ảnh theo đặc tả và báo được thành công đã đạt trong quá trình tối ưu.
- Xử lý gradient/perturbation/score NaN/Inf; kiểm tra cả norm cần thiết và khoảng RGB trên đầu ra cuối.
- Sửa sampler để không lặp record; cho phép chọn validation/development split riêng.
- Bổ sung adapter DFDC từ manifest đã audit; dùng đúng preprocessing WGN và một cohort cố định dùng chung cho clean và mọi attack. Runner hiện gọi FF++ `build_records` nên chưa chạy được DFDC trực tiếp.
- Ghi metadata đầy đủ; tránh run cũ bị ghi đè. Lưu dự đoán paired, numerator/denominator ASR, manipulation/video ID, norm pixel và DCT, MSE/PSNR/SSIM, WGSA diagnostics, runtime/peak VRAM.
- Lưu thống kê subband/gates/attention đủ chi tiết cho so sánh success/failure và phân tích theo band; scalar MAE tổng hợp hiện tại chưa đủ cho mọi phân tích cơ chế.
- Hạn chế CPU transfer trong inner attack loop khi không cần diagnostics trung gian.
- Đồng bộ PROTOCOL, TEST_PLAN, README và launcher với phương pháp đã chốt.

Tests cần có: DCT so với reference độc lập; gradient DCT→IDCT; toy objective đúng hướng; init/M/projection theo spec; norm sau toàn bộ biến đổi; stopping/best-iterate; model parameter và buffer bất biến; Real không đổi; sampler unique; ASR conditional/null; cả adapter FF++/DFDC; diagnostics clean=self có drift bằng 0; lỗi NaN/Inf dừng rõ.

**Đầu ra:** code reviewable, pytest report và protocol cập nhật, không kèm kết quả robustness.

**Tiêu chí qua bước:** tests pass và đối chiếu thuật toán hoàn thành theo mức claim đã chốt; test phần mềm không tự chứng minh fidelity với tác giả.

## Giai đoạn 4 — Clean reference và pilot trên development

1. Đo clean FF++ c23 test trên đúng 11.200 frames. Mốc kiểm tra: ACC=0.9391964285714286, AUC=0.9821176020408163; tolerance tuyệt đối=0.001 như gate hiện tại. Nếu sai thì sửa dữ liệu/model/environment, không tự nới tolerance.
2. Đo clean DFDC trên đúng cohort đã audit; so với record identity và kết quả baseline tương ứng. File baseline ghi 132.116 frames/4.704 videos; xác nhận lại sau restore trước khi coi là population khóa.
3. Chạy smoke 40 frames từ FF++ validation, dự kiến 20 Real và 5 Fake mỗi nhóm, nhiều video và không lặp record. Các tham số/chỉ số của pilot chỉ phục vụ kiểm tra pipeline.
4. Nếu cần chọn tham số, dùng development cohort cố định lớn hơn; đề xuất ban đầu 200 frames FF++ validation, cân bằng nhãn và nhóm. Ghi seed/cohort, không chọn frame dựa trên attack success. Thay đổi kích thước sau benchmark phải ghi trước final test.
5. Kiểm tra ảnh clean/adversarial, heatmap, RGB/norm, độ hữu hạn, hướng score, sự hoạt động của diagnostics, thời gian và bộ nhớ. Không đòi mọi frame phải giảm score ở mọi bước.
6. Chạy development smoke riêng cho DFDC sau khi adapter qua test. Nếu không có validation split hợp lệ, ưu tiên chuyển nguyên cấu hình đã khóa từ FF++; mọi tuning DFDC cần một development cohort loại khỏi final cohort và ghi lại định nghĩa protocol mới.

**Đầu ra:** clean-reference report, pilot report, cấu hình attack đã khóa, estimate runtime/disk từ tốc độ đo thực tế.

**Tiêu chí qua bước:** clean continuity đạt, attack tạo nhiễu hợp lệ/nonzero và có optimization sanity; không dùng final-test ASR để chọn epsilon, steps, M hoặc architecture.

## Giai đoạn 5 — Full evaluation theo protocol đã khóa

| Run | Victim | Population | Methods | Vai trò |
|---|---|---|---|---|
| E4-A | EXP-002 c23 checkpoint | FF++ c23 official test, 11.200 frames | Clean, FGSM, strong PGD, Jia FAA đã chốt | Kết quả chính đầu tiên |
| E4-B | Cùng checkpoint | DFDC: 1.000 Fake + 1.000 Real, seed 1024, được người dùng chọn | Cùng bộ methods; setting khóa trước final test | Đánh giá trên dataset khác |
| E4-C | Cùng checkpoint c23 | FF++ c40 test | Cấu hình đã khóa | Mở rộng cross-compression |
| E4-D | Cùng checkpoint | Cohort khóa | Jia Hybrid được đối chiếu riêng | Mở rộng sau FAA |

E4-A/E4-B là phạm vi bắt buộc; E4-C/E4-D và transfer study thực hiện sau khi xem kết quả và chi phí của phạm vi chính.

Lịch chạy đầu tiên dùng hai JSON `code/configs/final_reconstruction_{ffpp,dfdc}.json`; có thêm đối chứng `frequency-init-control`. Clean DFDC kiểm tra đủ 132.116 frames; cohort attack 2.000 frames có danh sách khóa riêng trước chạy. Tham số chi tiết và giới hạn về fidelity được ghi tại V3-PROTOCOL.md.

Thiết kế ngân sách gồm hai loại báo cáo nếu cần:

- Áp dụng thuật toán theo đặc tả Jia: giữ norm/miền/đơn vị đã xác minh hoặc công bố rõ các lựa chọn tái dựng.
- So sánh công bằng giữa attack: thiết lập ràng buộc/chất lượng có thể so sánh được, ghi rõ mọi thay đổi thuật toán. Không gọi ASR cao hơn là mạnh hơn nếu budget ở hai miền chưa tương xứng.

Không mặc định gán epsilon FAA=4/255 hoặc lấy epsilon pixel của FGSM/PGD làm epsilon DCT. Các sweep về steps/restarts/budget phải có trong schedule trước final test; sau test chỉ báo cáo sweep, không chọn lại một cấu hình thắng để che các run khác.

Chạy tuần tự trên GPU lab. Mỗi method/run có progress/checkpoint tiến độ phù hợp, file kết quả riêng và completion status. Không đoán tổng thời gian trước benchmark. Không tự chạy thêm training hoặc mở rộng dataset từ kết quả full run.

## Giai đoạn 6 — Phân tích vulnerability và cơ chế của WGN

Kết quả cần trình bày cho mỗi dataset/method/budget:

- Clean ACC/AUC và số lượng Fake clean-correct.
- Conditional Fake→Real ASR kèm tử số/mẫu số; unconditional evasion trình bày riêng.
- Attacked-Fake/clean-Real ACC/AUC với tên đúng phạm vi.
- Kết quả frame/video; per-manipulation FF++; confidence interval theo video/source-pair cluster, ghi rõ hạn chế mapping.
- Norm cuối, MSE/PSNR/SSIM và ví dụ trực quan; chi phí theo ảnh, tổng runtime, peak VRAM.
- Wavelet statistics, gates, attention drift ở nhóm attack thành công/thất bại; so sánh trong cùng manipulation/video/budget để giảm nhiễu do thành phần mẫu.

Không có ASR mục tiêu phải đạt. Nếu attack yếu hoặc không tìm thấy evasion, kiểm tra độ mạnh, tham số, gradient và giới hạn implementation trước diễn giải. Attack thất bại chưa đủ chứng nhận robustness.

Trước khi quy điểm yếu cho WGSA:

1. Kiểm tra ablation constant/clean-frozen gate với định nghĩa rõ; đánh giá clean performance của ablation.
2. So sánh backbone-only được huấn luyện với cùng split, initialization/budget/checkpoint-selection hợp lý; không dùng classifier mới khởi tạo để kết luận.
3. Lặp lại kết quả chính với seed/restarts đã định trước, kiểm tra độ ổn định và budget.

Các đối chứng có training được lập kế hoạch riêng sau kết quả vulnerability; không gộp vào lần attack đầu tiên.

**Đầu ra:** báo cáo vulnerability/mechanism có số liệu thực, evidence package và các câu hỏi nghiên cứu còn mở.

Kết luận cần trả lời: WGN có bị đánh lừa trong threat model đã khóa không, ở mức nhiễu nào, trên dataset/manipulation nào, và có bằng chứng gì về cơ chế liên quan. Phân biệt tương quan trong diagnostics với kết luận nhân quả; ghi nhận cả kết quả âm và giới hạn của attack. Kế hoạch hiện tại kết thúc ở bằng chứng này; chưa lựa chọn kiến trúc hoặc cơ chế phòng vệ mới.

## Giai đoạn 7 — Lưu và bàn giao kết quả

Lưu revision dataset, checksum checkpoint/shard/manifest, config đã khóa, Git commit/source diff, environment, per-frame outputs, summary, seed, log và completion status. Dùng policy backup/handoff của repo. Media, weights và ảnh trực quan giữ ngoài Git; chỉ publish artifact được phép và metadata gọn. Không thay visibility hoặc upload dữ liệu trong quá trình thực hiện kế hoạch nếu chưa có chỉ dẫn tương ứng.

## Việc làm ngay, theo thứ tự

1. Viết bảng đặc tả Jia và giải quyết các khác biệt đã audit.
2. Chuẩn bị environment riêng và restore/verify FF++ trước; tiếp tục audit/restore DFDC.
3. Triển khai attack/evaluator theo spec, thêm DFDC adapter và tests.
4. Chạy clean-reference gate, development smoke và benchmark.
5. Chốt schedule/config; chạy E4-A, rồi E4-B.
6. Phân tích cơ chế, tổng hợp kết quả EXP-004 và các giới hạn được bằng chứng hỗ trợ.

Không đặt deadline cố định cho full GPU runs trước benchmark. Tiến độ được cập nhật theo artifact và tiêu chí hoàn thành của từng giai đoạn.
