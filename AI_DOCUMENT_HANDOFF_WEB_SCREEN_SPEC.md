# AI Document Handoff Web Screen Spec

## Muc tieu

Tai lieu nay chuyen `AI_DOCUMENT_HANDOFF_SCREENS.html` tu wireframe sang screen spec chi tiet cho web.

Scope cua spec nay:

- chi screen / route / state / component
- khong mo ta backend implementation chi tiet
- bam sat `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
- giu triet ly: web nghiem format, LLM ngoai lam phan nang

Tai lieu implementation tiep theo:

- `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
- `AI_DOCUMENT_HANDOFF_ROADMAP.md`

## Nguyen tac UI

1. Nguoi dung phai nhin ro dang o tang nao:
   - `source_pack`
   - `activity_authoring`
   - `activity_feedback`
2. Moi man hinh chi phuc vu 1 buoc chinh.
3. CTA chinh moi man hinh chi co 1 nut duoc nhan manh.
4. Validate phai ro:
   - sai marker
   - sai schema
   - thieu field
   - sai `activity_type`
5. Khong auto-fix ngam.
6. Luon co duong lui:
   - xem prompt
   - copy repair prompt
   - xem payload goc

## Kien truc dieu huong

### Route de xuat

1. `/handoff/source-packs/new`
2. `/handoff/source-packs/:sourcePackId`
3. `/handoff/activities/new?sourcePackId=:id`
4. `/handoff/activities/:activityId`
5. `/handoff/activities/:activityId/submission`
6. `/handoff/activities/:activityId/feedback`

### Thanh dieu huong buoc

Moi screen trong flow chinh dung 1 step rail co 6 buoc:

1. Chon bai hoc
2. Tao source pack
3. Chon format
4. Nhap authoring payload
5. Nop bai hoc sinh
6. Nhap feedback payload

Rule hien thi:

- buoc hien tai: accent
- buoc da xong: success
- buoc chua mo: disabled

## Layout chung

### Desktop

Khung 3 cot:

1. **Step rail** ben trai, rong 220px
2. **Workspace** o giua, rong linh hoat, la noi thao tac chinh
3. **Context panel** ben phai, rong 320px, hien:
   - source pack hien tai
   - marker/schema nhanh
   - note/validation/help

### Tablet

Khung 2 cot:

- bo step rail thanh thanh ngang o tren
- context panel xuong duoi workspace hoac dong thanh accordion

### Mobile

Khung 1 cot:

- step rail thanh progress header ngan
- context panel doi thanh section `Thong tin lien quan`
- textarea va payload preview full width
- CTA sticky o day man hinh

## Component chung

1. **StepRail**
   - props: `steps`, `currentStep`, `completedSteps`
2. **PromptCard**
   - hien prompt co nut `Copy prompt`
3. **PayloadPasteBox**
   - textarea lon
   - detect marker
   - hien trang thai parse
4. **ValidationPanel**
   - `valid`
   - `warning`
   - `error`
   - danh sach loi theo field
5. **SummaryCard**
   - source pack summary
   - activity summary
   - feedback summary
6. **RepairPromptCard**
   - hien prompt sua format
   - nut `Copy repair prompt`
7. **ActivityTypeCard**
   - title
   - short description
   - availability
8. **SubmissionBox**
   - nhap bai lam
   - chon `response_type`
   - chi nhan:
     - `free_text`
     - `bullet_points`
     - `short_essay`

## Screen Spec

## S1 - Chon bai hoc va tao Source Pack

### Route

`/handoff/source-packs/new`

### Muc tieu

- chon dung 1 bai/chapter
- copy prompt `source_pack`
- paste ket qua `SOURCE_PACK_V1`

### Dieu kien vao

- nguoi dung da co tai lieu hoac lesson shell

### Component bat buoc

1. `LessonSelector`
2. `AttachedFilesList`
3. `PromptCard` cho source pack
4. `PayloadPasteBox` cho `SOURCE_PACK_V1`
5. `ValidationPanel`
6. `SummaryCard` preview source pack neu parse ok

### Noi dung workspace

#### Khoi A - Bai hoc dang chon

Field view:

- `document_title`
- `lesson_title`
- so file dinh kem
- file type list
- canh bao neu > 1 bai/1 chuong

#### Khoi B - Prompt source pack

CTA:

- `Copy prompt Source Pack` (primary neu chua co payload)

#### Khoi C - Paste ket qua

Textarea label:

- `Dan block SOURCE_PACK_V1 vao day`

Placeholder:

- nhac ro marker start/end

#### Khoi D - Ket qua validate

Trang thai:

- empty
- parsing
- valid
- invalid

### Primary CTA

- Khi chua paste: `Copy prompt Source Pack`
- Khi payload valid: `Luu source pack`

### Secondary CTA

- `Copy repair prompt`
- `Xem schema`
- `Xem payload goc`

### Validation rule hien thi

1. thieu marker
2. co text ngoai marker
3. parse JSON fail
4. thieu field root
5. array field sai type

### Success state

Hien:

- `source_pack_ref`
- summary ngan
- nut `Tiep tuc chon format`

### Mobile note

- file list doi thanh accordion
- summary preview dua xuong sau validation

## S2 - Chon format Wave 1

### Route

`/handoff/activities/new?sourcePackId=:id`

### Muc tieu

- chon 1 `activity_type` cho Wave 1

### Dieu kien vao

- da co `source_pack_ref`

### Component bat buoc

1. `SourcePackHeader`
2. `ActivityTypeGrid`
3. `DeferredFormatNotice`

### Activity cards

Moi card phai co:

- title
- 1 dong mo ta
- do kho authoring
- loai bai lam hoc sinh
- trang thai `Core` hoac `Later`

### Rule chon

- chi cho chon 1 format
- `decision_path` va `speed_challenge` chi hien disabled

### Primary CTA

- `Tao prompt authoring`

### Secondary CTA

- `Quay lai source pack`

### Success transition

Di den screen S3 va giu:

- `source_pack_ref`
- `activity_type`

## S3 - Copy prompt authoring va sinh activity payload

### Route

`/handoff/activities/new?sourcePackId=:id&activityType=:type`

### Muc tieu

- dua prompt authoring cho 1 format
- nhan `ACTIVITY_PAYLOAD_V2`

### Dieu kien vao

- co `source_pack_ref`
- co `activity_type`

### Component bat buoc

1. `SourcePackSummaryMini`
2. `ActivityTypeSummary`
3. `PromptCard`
4. `ExpectedSchemaMini`
5. `PayloadPasteBox`
6. `ValidationPanel`

### PromptCard phai hien

- ten format
- bien dau vao se duoc nhung:
  - `source_pack_json`
  - `activity_type`
- marker dung

### Context panel phai hien

- field bat buoc cua format da chon
- reject cases nhanh

### Primary CTA

- neu chua paste: `Copy prompt`
- neu da paste va valid: `Luu activity`

### Secondary CTA

- `Copy repair prompt`
- `Doi format`

### Validation bat buoc

Rule chung:

1. marker `ACTIVITY_PAYLOAD_V2`
2. `payload_type = activity_authoring`
3. `activity_type` khop format da chon
4. co `source_pack_ref`
5. co `instructions`
6. `activity_data` hop schema theo format

### Validation rieng theo format

#### `case_mission`

- `scenario`
- `task`
- `expected_points[]`
- `success_criteria[]`

#### `error_hunt`

- `artifact`
- `error_count_expected`
- `error_categories[]`
- `reference_points[]`

#### `explain_back`

- `teaching_prompt`
- `target_audience`
- `expected_points[]`
- `clarity_rubric[]`

#### `mini_project`

- `brief`
- `deliverable_type`
- `constraints[]`
- `rubric[]`

#### `debate_defend`

- `claim`
- `position_task`
- `evidence_rules[]`
- `rubric[]`

### Success state

Hien preview co cau truc:

- header activity
- instruction list
- activity data render de doc

## S4 - Preview activity va phat cho hoc sinh

### Route

`/handoff/activities/:activityId`

### Muc tieu

- cho nguoi quan tri giao vien xem activity da luu
- cho phep copy version de dua cho hoc sinh

### Component bat buoc

1. `ActivityHeader`
2. `InstructionList`
3. `ActivityRendererByType`
4. `PayloadMetaPanel`
5. `ActionBar`

### ActivityRendererByType

#### `case_mission`

- scenario card
- task box
- expected points an mac dinh, co nut hien

#### `error_hunt`

- artifact box
- huong dan tim loi

#### `explain_back`

- teaching prompt
- target audience badge

#### `mini_project`

- brief
- constraints
- rubric preview

#### `debate_defend`

- claim
- position task
- evidence rules

### Primary CTA

- `Mo man nop bai`

### Secondary CTA

- `Copy activity payload`
- `Sua bang prompt moi`
- `Gan vao lesson`

### Empty/error states

- khong tim thay `activityId`
- activity payload parse duoc truoc day nhung schema version cu

## S5 - Hoc sinh nop bai

### Route

`/handoff/activities/:activityId/submission`

### Muc tieu

- nhan bai lam hoc sinh
- dong goi submission de dua sang AI feedback prompt

### Component bat buoc

1. `ActivityHeaderMini`
2. `SubmissionBox`
3. `ResponseTypeSelect`
4. `PromptCard` cho feedback
5. `SubmissionPreview`

### Response type

Wave 1 chi nhan:

- `free_text`
- `bullet_points`
- `short_essay`

### Rule UI

- response type default theo format:
  - `case_mission`: `free_text`
  - `error_hunt`: `bullet_points`
  - `explain_back`: `short_essay`
  - `mini_project`: `short_essay`
  - `debate_defend`: `short_essay`

### Primary CTA

- `Copy feedback prompt`

### Secondary CTA

- `Luu nhap tam bai lam`
- `Xem lai activity`

### Validation

- `response_content` khong rong
- neu vuot gioi han ky tu hien warning, khong chan

### Success state

Hien package se duoc gui di:

- `source_pack_ref`
- `activity_authoring`
- `student_submission`

## S6 - Paste feedback payload va hien feedback

### Route

`/handoff/activities/:activityId/feedback`

### Muc tieu

- nhan `ACTIVITY_FEEDBACK_V2`
- validate
- hien feedback co cau truc

### Component bat buoc

1. `PayloadPasteBox`
2. `ValidationPanel`
3. `FeedbackSummary`
4. `FeedbackDetailsByType`
5. `RepairPromptCard`

### Validation rule chung

1. marker `ACTIVITY_FEEDBACK_V2`
2. `payload_type = activity_feedback`
3. `activity_type` khop `activityId`
4. co `student_submission`
5. co `feedback`
6. `feedback.overall_verdict`
7. `feedback.strengths[]`
8. `feedback.gaps[]`
9. `feedback.misconceptions[]`
10. `feedback.next_step`

### Validation rieng theo format

#### `case_mission`

- `missed_expected_points[]`

#### `error_hunt`

- `missed_errors[]`
- `false_positives[]`

#### `explain_back`

- `missing_points[]`
- `clarity_notes[]`

#### `mini_project`

- `rubric_breakdown[]`

#### `debate_defend`

- `argument_quality`
- `evidence_quality`
- `logic_gaps[]`

### FeedbackSummary

Field bat buoc hien ra man hinh:

- `overall_verdict`
- `score_optional` neu co
- `strengths`
- `gaps`
- `next_step`

### FeedbackDetailsByType

#### `case_mission`

- danh sach y thieu

#### `error_hunt`

- loi bo sot
- false positive

#### `explain_back`

- y thieu
- ghi chu do ro rang

#### `mini_project`

- rubric breakdown table

#### `debate_defend`

- chat luong lap luan
- chat luong dan chieu
- logic gaps

### Primary CTA

- `Luu feedback`

### Secondary CTA

- `Copy repair prompt`
- `Xem payload goc`
- `Gan vao roadmap sau`

## State model theo man hinh

Moi screen co 5 state co ban:

1. `empty`
2. `draft`
3. `validating`
4. `valid`
5. `invalid`

State them khi can:

- `saved`
- `stale_version`
- `load_error`

## Copy / label nen dung

### CTA chinh

- `Copy prompt Source Pack`
- `Luu source pack`
- `Tao prompt authoring`
- `Copy prompt`
- `Luu activity`
- `Mo man nop bai`
- `Copy feedback prompt`
- `Luu feedback`

### CTA phu

- `Copy repair prompt`
- `Xem schema`
- `Xem payload goc`
- `Quay lai source pack`
- `Doi format`

### Error copy mau

- `Khong tim thay marker bat dau hoac ket thuc.`
- `JSON khong hop le. Kiem tra dau phay, dau ngoac va dau ngoac kep.`
- `payload_type khong dung voi screen hien tai.`
- `activity_type khong khop format da chon.`
- `activity_data thieu truong bat buoc.`
- `Feedback thieu next_step nen chua the luu.`

## Responsive behavior

### Desktop

- giu du 3 cot
- context panel sticky
- textarea payload toi thieu 320px chieu cao

### Tablet

- step rail len tren
- context panel thanh accordion `Xem them`

### Mobile

- tung section thanh card doc
- CTA sticky bottom
- payload preview/validation dat sau textarea
- label ngan, tranh 2 dong qua dai trong toolbar

## Mapping voi V2 workflow

### Source pack

- S1 map voi contract `SOURCE_PACK_V1`

### Activity authoring

- S2 + S3 + S4 map voi `ACTIVITY_PAYLOAD_V2`

### Student submission + feedback

- S5 + S6 map voi `ACTIVITY_FEEDBACK_V2`

## Khong nam trong scope screen nay

1. runtime branching cho `decision_path`
2. timer cho `speed_challenge`
3. collaborative multi-user editing
4. auto-call API LLM trong web
5. import tu nhieu mode trong cung 1 request

## Acceptance checklist

Screen spec nay dat neu implementer doc xong co the tra loi ngay:

1. Moi screen co route gi
2. Moi screen co CTA chinh gi
3. Validate gi tren tung screen
4. State nao bat buoc phai co
5. Screen nao map vao contract nao

Neu con phai doan 1 trong 5 muc tren, spec nay chua du chi tiet.
