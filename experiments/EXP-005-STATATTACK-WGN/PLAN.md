# EXP-005 — Kế hoạch StatAttack / MStatAttack trên WGN

Ngày lập: 2026-11-15; cập nhật setup/lịch chạy:2026-11-16, Asia/Taipei. Người dùng yêu cầu thay draft RCWG bằng phương pháp attack từ paper thứ hai trong proposal, sau đó yêu cầu tự chạy nối tiếp EXP-004.

**Trạng thái cập nhật 2026-11-16 (Asia/Taipei): hoàn tất.** E5-0/E5-1/E5-2/E5-3 đã qua các cổng. E5-4 hoàn tất full FF++ c23, Celeb-DF-v2 official-direct, DFDC và WildDeepfake với hai attack cùng hai initialization control; bốn integrity/statistical audit đều pass. DFDC được resume từ SQLite sau khi sửa kiểm tra clean-score batch shape. Preflight toàn bộ42.932 eligible Fake không phát hiện đổi clean class; max absolute probability delta0.001355052. Canonical score/eligibility EXP-004, cohort, bank, attack profile và số bước được giữ nguyên. Migration lưu hash runner cũ/mới và trạng thái database trước resume. Tổng kết ASR và links tới báo cáo nằm trong [README EXP-005](README.md#full-cohort-results). Không đổi threshold0.5.

## Mục tiêu

Đánh giá frozen WGN trước statistical-consistency attacks trên full FF++ c23, DFDC, Celeb-DF-v2 official-direct và WildDeepfake. Đối chiếu hiệu quả với EXP-004 trên cùng checkpoint/cohort, kèm chất lượng và chi phí. Không suy ra vulnerability riêng của WGSA từ drift; không huấn luyện defense hay thiết kế kiến trúc trong EXP-005.

## E5-0 — Hoàn tất đặc tả và provenance

- Dùng [paper/source audit](docs/HOU-PAPER-AUDIT.md) làm bảng đối chiếu. Pin commit `bd62d1f44cf822f665a192aa348925ec6c1fa033`; cache tài liệu/source tham chiếu ngoài Git và ghi SHA.
- Chọn rõ profile: bám source StatAttack, hoặc tái dựng theo paper. Không trộn default demo, main paper và supplement rồi gọi exact reproduction. Bảng khác biệt hiện gồm số update, exposure learning rate, regularizer, Gaussian parameterization và tổng budget RGB.
- Quyết định có tài liệu cho dấu/chuẩn hóa regularizer, blur parameterization, clipping và từng learning rate trước final lock. Tham số thử nghiệm chỉ được kiểm tra trên FF++ validation; không chọn bằng ASR của bốn test set.
- MStatAttack: tái dựng theo Eq.8 với bốn nhánh ở mỗi layer và joint optimization; chưa có implementation trong repo được đọc. Tên phương pháp phải thể hiện reconstruction nếu chưa đối chiếu được source tác giả.

Đầu ra đã có: `docs/HOU-ALGORITHM-SPEC.md` và profile source-adapted40/mstat3 nêu rõ mọi lựa chọn thay vì gọi exact reproduction. Không còn default mơ hồ trong profile đang xếp lịch.

## E5-1 — Dữ liệu, clean gates và Real reference bank

Tái sử dụng bốn full test manifests/cohorts của EXP-004: tổng **325.554 frames**, 133.220 Real / 192.334 Fake. Không gộp train/validation vào population báo cáo. Checkpoint SHA luôn là `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.

Reference policy đề xuất cho phép so sánh có kiểm soát giữa dataset:

1. Một bank **960 Real frames từ FF++ train c23**, seed1024, chọn video-round-robin trước khi nhìn kết quả attack. Manifest hiện có 720 training Real videos / 28.800 candidate frames. Bank size960 là lựa chọn dự án, không phải con số được xác nhận trong paper.
2. Kiểm tra split/file/video disjoint với FF++ validation/test. Không khẳng định disjoint danh tính xuyên mọi external dataset khi metadata không chứng minh được. Không dùng clean-test Real làm reference trong protocol chính.
3. Xác minh 960 file có trong FF++ tar shards đã cache, checksum lại và giải nén chọn lọc; không cần tải video gốc. Nếu cache thiếu thì restore đúng shard backup. Kiểm tra decode/RGB/preprocessing và lưu bank fingerprint/record IDs.
4. Cache đặc trưng Real từ frozen WGN; không training hoặc cập nhật normalization. Gán reference batch bằng lịch deterministic, không chọn ảnh Real theo mức dễ tấn công. Hai phương pháp dùng cùng bank và assignment.
5. Batch tối ưu dự kiến30 Fake và30 references; final partial batch n Fake dùng đúng n references. Replay/cycle reference loader để bao phủ **mọi eligible Fake**; không dùng `zip(fake_loader, real_loader)` làm cắt mất dữ liệu khi bank ngắn.

Đây là threat model attacker có tập Real training-source. Nếu về sau muốn Real cùng external dataset, lập protocol phụ có reference/evaluation video disjoint và công bố phạm vi giảm; không âm thầm lấy reference từ test đang báo cáo.

Chạy/đối chiếu full clean gates với EXP-004 (ACC/AUC tolerance0.001, record fingerprints phải đúng). Khóa eligible IDs từ canonical clean evaluation batch32. Optimization batch30 là một phần của MMD objective, khác evaluation batch32; tách hai bước và kiểm tra tính liên tục dự đoán, đặc biệt mẫu sát threshold. Không thay population chỉ vì đổi batching.

## E5-2 — Implementation độc lập

Code dự kiến: `code/wgn_feature_adapter.py`, `mmd.py`, `degradations.py`, `statattack.py`, `mstatattack.py`, `reference_bank.py`, `run_exp05.py`, `analyze_exp05.py`, `code/configs/` và `tests/`.

- Hook input của `model.classifier` để lấy vector sau fusion+global mean pooling của **toàn WGN**. Attacked features phải giữ autograd; references có thể detach/cache. Không thay bằng output logit hoặc chỉ feature backbone mà không khai báo variant.
- Reuse loader/quality/diagnostics đã audit với phiên bản/hash cố định. Parameters/buffers của model bất biến; chỉ degradation parameters/mixture logits được tối ưu.
- Objective chính là MMD + regularization đã đặc tả, không tự thêm classification BCE. Fixed update count; ghi final iterate theo profile. Không copy per-image first-evasion stopping/best-logit selection từ Jia vì MMD là objective theo batch.
- Degradation controls dùng đúng init/composition/reference assignment của từng method nhưng **0 gradient updates**. Init blur có thể đã thay ảnh; phải đo thay vì giả định init là identity.
- Sửa các lỗi numerical/device/loader có kiểm chứng, ghi rõ khác biệt source; không import toàn bộ demo rồi mặc nhiên đổi preprocessing của WGN.

## E5-3 — Kiểm thử và development smoke

Qua [TEST_PLAN](docs/TEST_PLAN.md) trước GPU research run. Dùng FF++ validation riêng: smoke nhỏ rồi benchmark khoảng120 Fake frames, deterministic video-round-robin, kèm Real bank đã khóa. Không bắt buộc attack phải thành công trên smoke; yêu cầu gradient, objective, scope, finite/bounds và metadata đúng.

Đo memory/runtime cho cả StatAttack và MStatAttack40 updates/3layers trước dự toán full. Nếu batch30 không vừa16GB thì dừng final lock và đánh giá phương án exact blocked MMD giữ toàn batch; giảm batch thay đổi mục tiêu thống kê nên phải thành profile rõ. Không dùng microbatch MMD riêng rồi gọi tương đương full-batch MMD. Các GPU runs được xếp tuần tự trên cùng một GPU.

## E5-4 — Khóa và chạy full cả bốn bộ

Sau code/spec/clean/smoke/benchmark gates:

| Thứ tự | Full test dataset | Frames | Eligible Fake đã đo trong EXP-004 |
|---|---|---:|---:|
| 1 | FF++ c23 | 11.200 | 5.333 |
| 2 | Celeb-DF-v2 official-direct | 16.576 | 8.278 |
| 3 | DFDC | 132.116 | 42.932 |
| 4 | WildDeepfake | 165.662 | 88.521 |

Các eligible counts là mốc canonical hiện có, không phải sampling quotas. Tổng145.064 eligible Fake. Mỗi dataset chạy **StatAttack, MStatAttack, Stat-init-control, MStat-init-control** trên toàn bộ manifest; Fake eligibility mới được tối ưu, Real/clean false negatives giữ nguyên. Nếu code chưa đủ fidelity cho MStatAttack, trạng thái dataset/experiment vẫn incomplete; không tự thay bằng proxy hoặc kết luận đã xong cả hai.

Lưu config/cohort/reference-bank/assignment/source/checkpoint hashes trước attack; output ở runtime EXP-005 riêng, không ghi đè EXP-004. Full-run locks phải ghi tất cả default, objective, clamp/budget, reference access policy, order, seeds, grouping, stopping và scoring. Batch progress/log/status phải đọc được trực tiếp như EXP-004. Mỗi batch ghi checkpoint degradation parameters hoặc kết quả đủ để resume/replay, tránh phải chạy lại toàn bộ nếu bị gián đoạn; không lưu toàn bộ float32 attacked corpus vào ổ40GB.

## E5-5 — Báo cáo và so sánh

- ASR Fake→Real có numerator/eligible denominator; baseline FN riêng; frame/video ACC/AUC trước/sau; full coverage/unique IDs.
- PSNR finite count, SSIM, tổng pixel L∞/L2 và DCT norms, clipping fraction; BRISQUE với backend/weights/preprocessing đã kiểm chứng nếu dùng để đối chiếu paper.
- MMD trước/sau trên **cùng references**, degradation parameters, exposure/blur/noise và mixture weights; Haar subband/gates/attention drift. MMD giảm không tự chứng minh attack thành công hoặc WGSA là nguyên nhân.
- CI theo official FF++ source pairs; external video/sequence clusters chỉ exploratory khi thiếu source/identity linkage. WildDeepfake806 records là face-sequence groups, không phải806 original independent videos.
- So sánh paired trên eligible IDs chung với Jia/FGSM/PGD từ EXP-004. Giữ khác biệt budget/batching/reference access/steps minh bạch; không xếp hạng sức mạnh chỉ từ ASR. FGSM/PGD của Hou paper dùng profile khác EXP-004; nếu chạy thêm phải đặt tên/config riêng.
- Runtime, peak VRAM, package/source provenance, failures/skips bằng0 hoặc lý do chính xác. Ghi partial status khi chưa đủ methods/datasets, không report hoàn thành bằng aggregate thiếu mẫu.

White-box WGN là mục tiêu chính. Bốn dataset không đồng nghĩa black-box transfer giữa bốn detector. Transfer cần surrogate/target checkpoints độc lập và một protocol khác; không huấn luyện chúng trong kế hoạch này.

## Ghi nhận phục hồi DFDC

DFDC SQLite qua `PRAGMA integrity_check`; lúc resume chỉ có `stat-init-control` với42.900/42.932 dòng và1.430 batch đã commit. Giữ nguyên các kết quả/audit FF++ và Celeb-DF-v2. Canonical eligibility/score lấy từ EXP-004, threshold0.5; clean score recheck theo batch attack chỉ phải giữ cùng nhãn và được lưu kèm absolute delta. Toàn bộ eligible Fake được preflight, không có đổi nhãn. Migration provenance trong `runs/full_dfdc/environment.json` ghi hash runner trước/sau, lý do, policy kiểm tra, và số dòng/batch DB trước resume; snapshot runner trước sửa được giữ lại. Các hash profile/cohort/checkpoint/manifest/reference bank/canonical JSONL không đổi. DFDC và WildDeepfake sau đó hoàn tất full coverage cho bốn method và qua audit; FF++/Celeb-DF không chạy lại. Compact provenance đã publish trong [resume audit](results/dfdc-resume-audit.json).

## Điều kiện bắt đầu / kết thúc

**Đã qua:** paper/source review, frozen checkpoint, spec/profile, Real bank, hai methods/hai controls, 49 CPU tests, bốn clean gates, actual-WGN GPU smoke/benchmark, full runs trên cả bốn test cohort, integrity/statistical audits và tổng hợp per-dataset results. **EXP-005 hoàn tất.** Các outcomes báo cáo theo scope/giới hạn trong README và mỗi dataset report; không tuyên bố exact Hou reproduction hoặc attribution nhân quả cho WGSA.

Hoàn thành khi hai attacks và hai matched init controls đã bao phủ đủ bốn full test cohorts, qua toàn bộ integrity audits và có báo cáo đối chiếu EXP-004. Mọi thiết kế defense là quyết định sau hai nghiên cứu attack, chưa gán số experiment mới.
