# Dataset Access Plan

**Project:** Generalizable Deepfake Detection  
**Purpose:** obtain the datasets needed for WGN reproduction and improvement before renting the GPU.  
**Important:** raw videos, extracted frames, face crops, checkpoints, credentials, and signed agreements must never be committed to GitHub.

## 1. Datasets required for the current WGN plan

| Dataset | Purpose in this project | Access status | Action |
|---|---|---|---|
| FaceForensics++ | Main training set, c23/c40 control, and manipulation experiments | Permission email received | Keep the approval email and use the official download script |
| Celeb-DF v2 | Main cross-dataset evaluation; current WGN weakness | Permission required | Submit the Google or Tencent form |
| DFDC full dataset | Cross-dataset evaluation and robustness check | Meta/AWS access required | Create AWS account/IAM credentials and request access |
| WildDeepfake | Real-world cross-dataset evaluation | Agreement required | Submit the agreement form; use the official Hugging Face mirror after approval |

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

### What to request

Request **Celeb-DF v2**, not v1. The official repository describes v2 as 590 original videos and 5,639 synthesized videos, with an official 518-video testing list. We will use the official test list for cross-dataset evaluation and will not fine-tune WGN on Celeb-DF.

Suggested form description:

~~~text
I am an undergraduate student at Yuan Ze University conducting an academic
capstone project on generalizable deepfake detection. I will train a WGN-based
detector on the approved FaceForensics++ dataset and use Celeb-DF v2 only for
cross-dataset evaluation. The data will not be redistributed or used for
commercial purposes. I will cite the Celeb-DF paper and follow the dataset
terms of use.
~~~

## 4. DFDC

### Official sources

- [Meta AI DFDC dataset page](https://ai.meta.com/datasets/dfdc/)
- [DFDC access portal](https://dfdc.ai/)
- [DFDC full-dataset paper](https://arxiv.org/abs/2006.07397)
- [DFDC Kaggle competition page](https://www.kaggle.com/c/deepfake-detection-challenge/data)

### Access requirements

The official Meta page states that access requires an AWS account, an IAM user with access keys, and the AWS account number. Prepare these before the GPU rental. Do not put AWS keys in this repository or in experiment logs.

The full DFDC contains approximately 124,000 videos and is much larger than the other evaluation sets. We should request access now but download only the exact split needed for the agreed evaluation protocol. The current WGN plan uses DFDC as an external test set, not as a training set.

## 5. WildDeepfake

### Official sources

- [Official WildDeepfake repository](https://github.com/xingjunm/wild-deepfake)
- [WildDeepfake paper](https://arxiv.org/abs/2101.01456)
- [WildDeepfake agreement form](https://forms.gle/o8vy9Q8fQ5mQZ4Qk6)
- [Official Hugging Face dataset mirror](https://huggingface.co/datasets/xingjunm/WildDeepfake)
- Contact listed by the authors: danxjma@gmail.com

The official repository describes 7,314 face sequences from 707 deepfake videos. Only face sequences are released. Complete the agreement form before using the dataset. The Hugging Face mirror is a download location, not a replacement for the authors' usage agreement.

Suggested form description:

~~~text
I am an undergraduate student at Yuan Ze University conducting an academic
capstone project on generalizable deepfake detection. I will use WildDeepfake
only as an external evaluation set for a detector trained on FaceForensics++.
The data will not be redistributed or used commercially, and I will follow the
privacy, citation, and removal requirements in the dataset agreement.
~~~

## 6. Optional preprocessed data from DeepfakeBench

DeepfakeBench provides preprocessed RGB face crops, masks, landmarks, and JSON configurations. This can save preprocessing time, but it does not replace the original dataset providers' terms.

- [DeepfakeBench official repository](https://github.com/SCLBD/DeepfakeBench)
- [Preprocessed RGB data on Google Drive](https://drive.google.com/drive/folders/1N4X3rvx9IhmkEZK-KIk4OxBrQb9BRUcs?usp=drive_link)
- [JSON configurations on Google Drive](https://drive.google.com/drive/folders/1ZV3fz5MZZU5BTB5neziN6i8Yv0Z21_LO?usp=drive_link)
- [DeepfakeBench paper](https://arxiv.org/abs/2307.01426)

Important limitations:

- The provided processed data is generally 32 cropped frames per video.
- The provided FaceForensics++/FaceShifter data is c23 only, so it cannot replace the c40 download.
- DeepfakeBench explicitly states that copyright belongs to the original providers.
- Use the processed data only after confirming that the relevant original-provider terms permit this academic use.
- Record the downloaded archive name, date, checksum, and source URL in the private data log.

For a faithful WGN reproduction, use the approved FF++ data and the existing preprocessing pipeline for the final c23/c40 control. Use DeepfakeBench data only for a pilot or when preprocessing time is the bottleneck.

## 7. Recommended request order

1. **Celeb-DF v2:** submit both forms now; it is the most important target because the WGN baseline has its largest generalization gap there.
2. **WildDeepfake:** submit the agreement form now; approval may require an academic email and signature.
3. **DFDC:** create the AWS/IAM access prerequisites now; request access before renting the GPU because the dataset is large.
4. **FaceForensics++:** keep the existing author approval email and download-script instructions.
5. **DeepfakeBench processed data:** download only after the source-dataset permissions are clear.

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

Do not rent the GPU for final experiments until:

- FF++ data path and manifest are confirmed;
- Celeb-DF v2 request has been submitted;
- WildDeepfake agreement has been submitted;
- DFDC AWS prerequisites are ready;
- at least one cross-dataset target is physically available or its download is scheduled;
- the WGN smoke test can run on the rented environment.

