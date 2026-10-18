# Dataset Access Plan

**Project:** Generalizable Deepfake Detection  
**Purpose:** obtain the datasets needed for WGN reproduction and improvement before renting the GPU.  
**Important:** raw videos, extracted frames, face crops, checkpoints, credentials, and signed agreements must never be committed to GitHub.

## 1. Datasets required for the current WGN plan

| Dataset | Purpose in this project | Access status | Action |
|---|---|---|---|
| FaceForensics++ | Main training set, c23/c40 control, and manipulation experiments | Permission email received | Keep the approval email and use the official download script |
| Celeb-DF v2 | Main cross-dataset evaluation; current WGN weakness | **Approved; direct links received** | Download v2 and keep the access email private |
| DFDC full dataset | Cross-dataset evaluation and robustness check | **Approved; access granted** | Use the approved DeepfakeBench-processed copy for this phase |
| WildDeepfake | Real-world cross-dataset evaluation | **Approved; agreement accepted** | Use the approved DeepfakeBench-processed copy for this phase |

FaceShifter and DeepfakeDetection do not need a separate request for the current plan if they are downloaded through the approved FaceForensics++ script. Verify the exact permission scope in the reply received from the FaceForensics authors.

## 2. FaceForensics++

### Official sources

- [Official FaceForensics repository](https://github.com/ondyari/FaceForensics)
- [FaceForensics++ download script v4](http://kaldir.vc.in.tum.de/faceforensics_download_v4.py)
- [FaceForensics benchmark documentation](https://kaldir.vc.in.tum.de/faceforensics_benchmark/documentation)
- [FaceForensics benchmark images](http://kaldir.vc.in.tum.de/faceforensics_benchmark_images.zip)

### Permission already received

The project has received an approval email from the FaceForensics authors. Preserve that email outside GitHub as evidence of access. The authors currently instruct users to use the EU2 server:

~~~text
python download.py --server EU2 --c c23
python download.py --server EU2 --c c40
~~~

The existing WGN reproduction uses FF++ c23 for training and c40 for compression robustness. The FaceShifter manipulation is evaluated as an additional held-out manipulation when present in the approved FF++ download.

## 3. Celeb-DF v2

### Official sources

- [Official Celeb-DF repository](https://github.com/yuezunli/celeb-deepfakeforensics)
- [Celeb-DF v2 information page](https://cse.buffalo.edu/~siweilyu/celeb-deepfakeforensics)
- [Celeb-DF paper](https://arxiv.org/abs/1909.12962)
- [Google access/terms form](https://forms.gle/2jYBby6y1FBU3u6q9)
- [Tencent access/terms form](https://wj.qq.com/s2/8540155/b5d9/)
- Contact: deepfakeforensics@gmail.com

### Access received

The project will use **Celeb-DF v2 only** for external evaluation. The access email supplied the following official download locations:

- Google Drive (v2): <https://drive.google.com/open?id=1iLx76wsbi9itnkxSqz9BVBl4ZvnbIazj>
- Baidu Netdisk (v2): <https://pan.baidu.com/s/1EcYX0s4U3kbI1V2vdrP46A> — extraction code: `yxa1`

The v1 links are recorded for reference only and are not required for this project:

- Google Drive (v1): <https://drive.google.com/open?id=10NGF38RgF8FZneKOuCOdRIsPzpC7_WDd>
- Baidu Netdisk (v1): <https://pan.baidu.com/s/16QulfMFG4TQB9iMZIZnsjQ> — extraction code: `ku0s`

We will use the official test list for cross-dataset evaluation and will not fine-tune WGN on Celeb-DF. Keep the approval email and any downloaded archive outside GitHub.

## 4. DFDC

### Official sources

- [Meta AI DFDC dataset page](https://ai.meta.com/datasets/dfdc/)
- [DFDC access portal](https://dfdc.ai/)
- [DFDC full-dataset paper](https://arxiv.org/abs/2006.07397)
- [DFDC Kaggle competition page](https://www.kaggle.com/c/deepfake-detection-challenge/data)

### Access requirements

The project has received DFDC access approval. For the current improvement phase, use the approved **DeepfakeBench preprocessed RGB/JSON copy** for external evaluation instead of repeating full video extraction and face preprocessing on the rented GPU. The original Meta/DFDC terms still apply; never commit AWS credentials, private access messages, or raw data.

The full DFDC contains approximately 124,000 videos and is much larger than the other evaluation sets. Download only the exact split needed for the agreed evaluation protocol. The current WGN plan uses DFDC as an external test set, not as a training set.

## 5. WildDeepfake

### Official sources

- [Official WildDeepfake repository](https://github.com/xingjunm/wild-deepfake)
- [WildDeepfake paper](https://arxiv.org/abs/2101.01456)
- [WildDeepfake agreement form](https://forms.gle/o8vy9Q8fQ5mQZ4Qk6)
- [Official Hugging Face dataset mirror](https://huggingface.co/datasets/xingjunm/WildDeepfake)
- Contact listed by the authors: danxjma@gmail.com

The official repository describes 7,314 face sequences from 707 deepfake videos. Only face sequences are released. The project has received approval to use WildDeepfake. For this phase, use the approved **DeepfakeBench preprocessed RGB/JSON copy**; the original authors' privacy, citation, and removal requirements still apply.

Suggested form description:

~~~text
I am an undergraduate student at Yuan Ze University conducting an academic
capstone project on generalizable deepfake detection. I will use WildDeepfake
only as an external evaluation set for a detector trained on FaceForensics++.
The data will not be redistributed or used commercially, and I will follow the
privacy, citation, and removal requirements in the dataset agreement.
~~~

## 6. Selected preprocessed data source (DeepfakeBench)

DeepfakeBench is now the selected source for the external-evaluation copies of **Celeb-DF v2, DFDC, and WildDeepfake**. This saves GPU time by avoiding a second full face-detection/cropping pipeline. It does not replace the original dataset providers' terms or citations.

- [DeepfakeBench official repository](https://github.com/SCLBD/DeepfakeBench)
- [Preprocessed RGB data on Google Drive](https://drive.google.com/drive/folders/1N4X3rvx9IhmkEZK-KIk4OxBrQb9BRUcs?usp=drive_link)
- [JSON configurations on Google Drive](https://drive.google.com/drive/folders/1ZV3fz5MZZU5BTB5neziN6i8Yv0Z21_LO?usp=drive_link)
- [DeepfakeBench paper](https://arxiv.org/abs/2307.01426)

Use the processed RGB data and matching JSON configurations only after confirming that the relevant source-dataset approvals cover this academic use. The project will not fine-tune WGN on these target datasets.

Important limitations and validation requirements:

- The processed data is generally 32 cropped frames per video.
- The available FaceForensics++/FaceShifter processed copy is c23 only, so it does not replace the FF++ c40 control.
- Copyright remains with the original dataset providers.
- Record archive name, download date, checksum, source URL, and local path in the private data log.
- The current WGN loader expects a compatible JSON layout. **Do not assume DeepfakeBench JSON is directly compatible**; first validate paths, labels, video IDs, and split names, then write the small conversion step if needed.
- Raw external downloads are a fallback only if the processed archive or manifest cannot be validated.

For faithful reproduction, keep the existing approved FF++ c23/c40 pipeline as the baseline/control. Use DeepfakeBench data for the external-evaluation phase to reduce preprocessing time.

## 7. Next data-access actions

All required permissions have now been received for this phase:

1. Keep the FaceForensics++ approval email and existing FF++ download instructions.
2. Download the DeepfakeBench RGB archive and matching JSON configurations.
3. Record checksums and inspect the archive layout.
4. Validate or convert the DeepfakeBench JSON into the WGN manifest format.
5. Run a small external-evaluation smoke test before renting long GPU sessions.

Do not commit signed agreements, private download links, credentials, raw videos, face crops, or checkpoints.

## 8. Private data-access log

Keep the following information in a private file outside GitHub:

~~~text
dataset:
provider:
request_date:
approval_date:
account_or_email_used:
terms_url:
download_url:
archive_name:
sha256:
local_path:
permitted_use:
notes:
~~~

Commit only a redacted status file containing dataset name, approval status, date, source URL, and checksum. Never commit signed agreements, private download links, AWS credentials, or raw data.

## 9. Machine preparation rule

Do not start long final GPU runs until:

- FF++ data path and manifest are confirmed;
- DeepfakeBench RGB and JSON archives are downloaded or scheduled;
- archive checksums and sample paths are recorded privately;
- the DeepfakeBench-to-WGN manifest validation/conversion passes;
- at least one external target smoke test completes;
- the WGN smoke test can run on the rented environment.

