# AI Document Handoff Workflow V2

Screen walkthrough:

- xem wireframe o `AI_DOCUMENT_HANDOFF_SCREENS.html`
- xem screen spec chi tiet o `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md`
- xem frontend implementation spec o `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
- xem roadmap thuc thi o `AI_DOCUMENT_HANDOFF_ROADMAP.md`

## Muc tieu da chot

V2 mo rong huong handoff tu quiz-only sang mot kien truc tong quat hon:

- web khong tu sinh noi dung
- web khong tu cham runtime
- web chi phat prompt, nhan payload chuan, validate, luu, preview, import
- GPT / Gemini / Claude xu ly phan nang

V2 dung `thamkhao.txt` lam reference chinh cho huong van hanh:

1. `source_pack` la tang trung gian bat buoc
2. moi mode/format phai co prompt rieng
3. output phai la payload co schema
4. neu sai format thi repair, khong doan

## Moi quan he voi V1

- `AI_DOCUMENT_HANDOFF_WORKFLOW.md` tiep tuc la legacy spec cho `QUIZ_PAYLOAD_V1`
- V2 khong doi contract `QUIZ_PAYLOAD_V1`
- V1 co the duoc xem la mot `practice profile` chuyen biet
- V2 bo sung contract chung cho nhung format mo hon quiz

## Wave 1 duoc chot

Wave 1 chi chot 5 format `core async`:

1. `case_mission`
2. `error_hunt`
3. `explain_back`
4. `mini_project`
5. `debate_defend`

Hai format de phase sau:

- `decision_path`
- `speed_challenge`

Ly do deferred:

- can state
- can timer / step state
- can branch logic
- khong hop voi vong handoff thuong ngay cua V2

## Rules bat buoc

1. Moi lan chi xu ly 1 bai hoac 1 chuong.
2. Moi lan chi chay 1 mode hoac 1 format.
3. Chi nhan payload co marker/schema dung chuan.
4. Khong nhan prose tu do.
5. Khong duoc them fact ngoai tai lieu.
6. Neu thieu bang chung thi de trong hoac bo muc do.
7. Neu parse fail thi reject va dua prompt repair.
8. Web khong tu goi model de "tu doan y dung".
9. Web khong tu cham bai lam hoc sinh trong vong nay.
10. Authoring payload va feedback payload la 2 hop dong rieng.

## Kien truc 2 tang

### Tang 1: Source pack

`source_pack` la ban chuan hoa tai lieu de dung lai cho nhieu mode.

Flow:

1. nguoi dung chon 1 bai/chuong
2. dua tai lieu vao GPT / Gemini / Claude
3. chay prompt `source_pack`
4. AI tra ve 1 JSON chuan
5. nguoi dung dan nguoc vao web
6. web validate, luu, sinh `source_pack_ref`

### Tang 2: Activity payload

Moi format moi deu duoc sinh tu `source_pack`.

Flow:

1. nguoi dung chon 1 `source_pack_ref`
2. chon 1 format
3. web hien prompt authoring tuong ung
4. AI tra ve `activity_authoring payload`
5. nguoi dung dan vao web
6. web validate va luu
7. hoc sinh lam bai
8. hoc sinh hoac web copy bai lam sang AI bang feedback prompt
9. AI tra ve `activity_feedback payload`
10. nguoi dung dan vao web
11. web validate, luu, hien feedback

## Marker quy uoc

### Source pack

```text
<<<SOURCE_PACK_V1_START>>>
...
<<<SOURCE_PACK_V1_END>>>
```

### Activity authoring

```text
<<<ACTIVITY_PAYLOAD_V2_START>>>
...
<<<ACTIVITY_PAYLOAD_V2_END>>>
```

### Activity feedback

```text
<<<ACTIVITY_FEEDBACK_V2_START>>>
...
<<<ACTIVITY_FEEDBACK_V2_END>>>
```

## Contract 1: Source pack

### Schema

```json
{
  "payload_type": "source_pack",
  "source_pack_ref": "",
  "subject": "",
  "grade_level": "",
  "chapter_title": "",
  "lesson_title": "",
  "learning_objectives": [],
  "key_concepts": [],
  "formulas": [],
  "events_or_milestones": [],
  "examples": [],
  "common_mistakes": [],
  "prerequisites": [],
  "source_notes": [],
  "coverage_warning": ""
}
```

### Rule validate

- tat ca field root phai ton tai
- field array duoc rong nhung phai dung type
- string duoc rong
- `payload_type` phai la `source_pack`
- `source_pack_ref` co the de rong khi tao moi; backend se sinh luc save
- `source_notes` la array string, khong dung string don
- khong duoc co text ngoai marker

### Prompt sinh source pack

```text
Ban dang doc cac tai lieu dinh kem cho 1 bai hoac 1 chuong hoc.

Nhiem vu:
1. Chi dung thong tin co trong tai lieu dinh kem.
2. Khong them kien thuc ngoai tai lieu, tru khi can noi cau rat ngan.
3. Chuan hoa noi dung thanh 1 JSON duy nhat.
4. Neu mot truong thieu thong tin, de rong "" hoac [].
5. Khong viet bat ky giai thich nao ngoai block ket qua.

Tra ve dung block:
<<<SOURCE_PACK_V1_START>>>
{JSON}
<<<SOURCE_PACK_V1_END>>>

Schema bat buoc:
{
  "payload_type": "source_pack",
  "source_pack_ref": "",
  "subject": "",
  "grade_level": "",
  "chapter_title": "",
  "lesson_title": "",
  "learning_objectives": [],
  "key_concepts": [],
  "formulas": [],
  "events_or_milestones": [],
  "examples": [],
  "common_mistakes": [],
  "prerequisites": [],
  "source_notes": [],
  "coverage_warning": ""
}

Tai lieu:
{{DOCUMENT_TEXT}}
```

## Contract 2: Activity authoring envelope

### Schema chung

```json
{
  "payload_type": "activity_authoring",
  "activity_type": "case_mission",
  "activity_id": "",
  "source_pack_ref": "sp_bai_hoc_001",
  "document_title": "",
  "lesson_title": "",
  "student_level": "",
  "instructions": [],
  "activity_data": {}
}
```

### Rule chung

- `payload_type` phai la `activity_authoring`
- `activity_type` chi nhan 1 trong 5 gia tri Wave 1
- `activity_id` phai ton tai trong payload; neu de rong, backend se sinh luc save
- neu `activity_id` co gia tri, no phai unique trong 1 import batch
- `source_pack_ref` phai tro ve source pack da duoc luu
- `instructions` la danh sach ngan, huong dan hoc sinh lam bai
- `activity_data` bat buoc theo schema cua tung format

## Contract 3: Activity feedback envelope

### Schema chung

```json
{
  "payload_type": "activity_feedback",
  "activity_type": "case_mission",
  "activity_id": "act_case_001",
  "student_submission": {
    "response_type": "free_text",
    "response_content": ""
  },
  "feedback": {
    "overall_verdict": "partial",
    "strengths": [],
    "gaps": [],
    "misconceptions": [],
    "next_step": "",
    "score_optional": null
  }
}
```

### Rule chung

- `payload_type` phai la `activity_feedback`
- `activity_type` phai khop `activity_id`
- `response_type` Wave 1 chi nhan:
  - `free_text`
  - `bullet_points`
  - `short_essay`
- `feedback.strengths`, `feedback.gaps`, `feedback.misconceptions` la array
- `feedback.next_step` bat buoc
- `feedback.score_optional` neu co chi nhan string, number, hoac null
- `feedback.overall_verdict` chi nhan:
  - `strong`
  - `partial`
  - `needs_revision`

## Wave 1 activity types

### 1. `case_mission`

#### Activity data schema

```json
{
  "scenario": "",
  "task": "",
  "expected_points": ["", ""],
  "success_criteria": ["", ""],
  "hint_optional": ""
}
```

#### Feedback add-on

```json
{
  "missed_expected_points": ["", ""]
}
```

#### Authoring example

```text
<<<ACTIVITY_PAYLOAD_V2_START>>>
{
  "payload_type": "activity_authoring",
  "activity_type": "case_mission",
  "activity_id": "act_case_001",
  "source_pack_ref": "sp_sinh_hoc_001",
  "document_title": "He ho hap",
  "lesson_title": "Co che trao doi khi",
  "student_level": "lop_8",
  "instructions": [
    "Doc tinh huong",
    "Tra loi ngan gon theo y"
  ],
  "activity_data": {
    "scenario": "Mot benh nhan co bieu hien kho tho, met nhanh va tim dap nhanh sau van dong.",
    "task": "Xac dinh he co quan lien quan nhat va giai thich vi sao.",
    "expected_points": [
      "Nhan ra he ho hap",
      "Noi duoc vai tro trao doi oxy",
      "Lien he voi trieu chung"
    ],
    "success_criteria": [
      "Dung he co quan",
      "Co giai thich bang kien thuc trong bai"
    ],
    "hint_optional": "Tap trung vao chuc nang dua oxy vao co the."
  }
}
<<<ACTIVITY_PAYLOAD_V2_END>>>
```

#### Feedback example

```text
<<<ACTIVITY_FEEDBACK_V2_START>>>
{
  "payload_type": "activity_feedback",
  "activity_type": "case_mission",
  "activity_id": "act_case_001",
  "student_submission": {
    "response_type": "free_text",
    "response_content": "Em chon he ho hap vi benh nhan kho tho va met do thieu oxy."
  },
  "feedback": {
    "overall_verdict": "partial",
    "strengths": [
      "Da xac dinh dung he ho hap"
    ],
    "gaps": [
      "Chua giai thich ro co che trao doi khi"
    ],
    "misconceptions": [],
    "next_step": "Bo sung vai tro cua oxy va khi carbonic trong trao doi khi.",
    "score_optional": "7/10",
    "missed_expected_points": [
      "Lien he ro giua trieu chung va viec thieu oxy"
    ]
  }
}
<<<ACTIVITY_FEEDBACK_V2_END>>>
```

#### Prompt authoring

```text
Ban la nguoi thiet ke hoat dong hoc tap dang `case_mission`.

Du lieu nguon:
{source_pack_json}

Yeu cau:
- Tao 1 tinh huong ngan, thuc te, bam sat bai hoc.
- Khong them kien thuc ngoai source pack.
- Hoc sinh phai ap dung kien thuc, khong chi nho lai dinh nghia.
- Tra ve dung 1 block:
  <<<ACTIVITY_PAYLOAD_V2_START>>>
  ...
  <<<ACTIVITY_PAYLOAD_V2_END>>>
- JSON hop le, dung schema `case_mission`.
```

#### Prompt feedback

```text
Ban la nguoi cham hoat dong `case_mission`.

Du lieu nguon:
{source_pack_json}

Hoat dong:
{activity_authoring_json}

Bai lam hoc sinh:
{student_submission}

Yeu cau:
- Danh gia chi dua tren source pack va hoat dong.
- Neu hoc sinh dung mot phan, danh gia `partial`.
- Noi ro y dung, y thieu, hieu sai neu co.
- Tra ve dung 1 block:
  <<<ACTIVITY_FEEDBACK_V2_START>>>
  ...
  <<<ACTIVITY_FEEDBACK_V2_END>>>
```

### 2. `error_hunt`

#### Activity data schema

```json
{
  "artifact": "",
  "error_count_expected": 0,
  "error_categories": ["", ""],
  "reference_points": ["", ""]
}
```

#### Feedback add-on

```json
{
  "missed_errors": ["", ""],
  "false_positives": ["", ""]
}
```

#### Authoring example

```text
<<<ACTIVITY_PAYLOAD_V2_START>>>
{
  "payload_type": "activity_authoring",
  "activity_type": "error_hunt",
  "activity_id": "act_error_001",
  "source_pack_ref": "sp_toan_001",
  "document_title": "Phuong trinh bac nhat",
  "lesson_title": "Giai phuong trinh co dau",
  "student_level": "lop_7",
  "instructions": [
    "Tim loi sai",
    "Sua lai va giai thich"
  ],
  "activity_data": {
    "artifact": "2x + 5 = 11 => 2x = 11 + 5 => x = 8",
    "error_count_expected": 2,
    "error_categories": [
      "chuyen ve sai dau",
      "chia sai ket qua"
    ],
    "reference_points": [
      "Khi chuyen ve phai doi dau",
      "Sau do chia hai ve cho 2"
    ]
  }
}
<<<ACTIVITY_PAYLOAD_V2_END>>>
```

#### Feedback example

```text
<<<ACTIVITY_FEEDBACK_V2_START>>>
{
  "payload_type": "activity_feedback",
  "activity_type": "error_hunt",
  "activity_id": "act_error_001",
  "student_submission": {
    "response_type": "bullet_points",
    "response_content": "- Loi 1: chuyen 5 sai dau\n- Loi 2: ket qua x phai la 3"
  },
  "feedback": {
    "overall_verdict": "strong",
    "strengths": [
      "Da tim dung loi sai dau",
      "Da sua dung ket qua cuoi"
    ],
    "gaps": [],
    "misconceptions": [],
    "next_step": "Thu tu viet lai day du cac buoc sau khi sua.",
    "score_optional": "9/10",
    "missed_errors": [],
    "false_positives": []
  }
}
<<<ACTIVITY_FEEDBACK_V2_END>>>
```

#### Prompt authoring

```text
Ban la nguoi thiet ke hoat dong `error_hunt`.

Du lieu nguon:
{source_pack_json}

Yeu cau:
- Tao 1 artifact co loi dung trong pham vi bai hoc.
- Loi phai co the phat hien tu source pack.
- Chi tao so loi vua du, ro rang, khong danh do hoc sinh bang thong tin ngoai bai.
- Tra ve dung schema `error_hunt` trong marker V2.
```

#### Prompt feedback

```text
Ban la nguoi cham hoat dong `error_hunt`.

Du lieu nguon:
{source_pack_json}

Hoat dong:
{activity_authoring_json}

Bai lam:
{student_submission}

Yeu cau:
- Chi ra hoc sinh tim dung loi nao
- Hoc sinh bo sot loi nao
- Hoc sinh co ket luan nham nao khong
- Tra ve dung schema feedback `error_hunt` trong marker V2
```

### 3. `explain_back`

#### Activity data schema

```json
{
  "teaching_prompt": "",
  "target_audience": "",
  "expected_points": ["", ""],
  "clarity_rubric": ["", ""]
}
```

#### Feedback add-on

```json
{
  "missing_points": ["", ""],
  "clarity_notes": ["", ""]
}
```

#### Authoring example

```text
<<<ACTIVITY_PAYLOAD_V2_START>>>
{
  "payload_type": "activity_authoring",
  "activity_type": "explain_back",
  "activity_id": "act_explain_001",
  "source_pack_ref": "sp_lich_su_001",
  "document_title": "Cach mang thang Tam",
  "lesson_title": "Nguyen nhan va thoi co",
  "student_level": "lop_9",
  "instructions": [
    "Giai thich nhu dang day lai cho ban hoc",
    "Toi da 5 cau"
  ],
  "activity_data": {
    "teaching_prompt": "Hay giai thich vi sao thoi co cach mang xuat hien vao giai doan nay.",
    "target_audience": "hoc sinh lop 6",
    "expected_points": [
      "Noi duoc boi canh",
      "Noi duoc thoi co chinh tri",
      "Dung ngon ngu de hieu"
    ],
    "clarity_rubric": [
      "Cau ngan",
      "Khong dung tu qua hoc thuat"
    ]
  }
}
<<<ACTIVITY_PAYLOAD_V2_END>>>
```

#### Feedback example

```text
<<<ACTIVITY_FEEDBACK_V2_START>>>
{
  "payload_type": "activity_feedback",
  "activity_type": "explain_back",
  "activity_id": "act_explain_001",
  "student_submission": {
    "response_type": "short_essay",
    "response_content": "Thoi co den khi ke thu yeu di va nhan dan da san sang dung len."
  },
  "feedback": {
    "overall_verdict": "partial",
    "strengths": [
      "Cach noi kha de hieu",
      "Da co y ve boi canh thuan loi"
    ],
    "gaps": [
      "Con thieu mot y ve su san sang cua luc luong cach mang"
    ],
    "misconceptions": [],
    "next_step": "Them 1-2 cau noi ro yeu to thoi co va luc luong.",
    "score_optional": "7/10",
    "missing_points": [
      "Luc luong cach mang da duoc chuan bi"
    ],
    "clarity_notes": [
      "Cach noi gon, hop doi tuong lop 6"
    ]
  }
}
<<<ACTIVITY_FEEDBACK_V2_END>>>
```

#### Prompt authoring

```text
Ban la nguoi thiet ke hoat dong `explain_back`.

Du lieu nguon:
{source_pack_json}

Yeu cau:
- Tao 1 de bai bat hoc sinh giai thich lai kien thuc nhu dang day nguoi khac.
- Neu hop, chon doi tuong nho tuoi hon de bat buoc dien giai don gian.
- Tra ve dung schema `explain_back` trong marker V2.
```

#### Prompt feedback

```text
Ban la nguoi cham hoat dong `explain_back`.

Du lieu nguon:
{source_pack_json}

Hoat dong:
{activity_authoring_json}

Bai lam:
{student_submission}

Yeu cau:
- Danh gia do dung y
- Chi ra y thieu
- Danh gia do de hieu cua cach dien giai
- Tra ve dung schema feedback `explain_back` trong marker V2
```

### 4. `mini_project`

#### Activity data schema

```json
{
  "brief": "",
  "deliverable_type": "",
  "constraints": ["", ""],
  "rubric": ["", ""]
}
```

#### Feedback add-on

```json
{
  "rubric_breakdown": [
    {
      "criterion": "",
      "verdict": "",
      "note": ""
    }
  ]
}
```

#### Authoring example

```text
<<<ACTIVITY_PAYLOAD_V2_START>>>
{
  "payload_type": "activity_authoring",
  "activity_type": "mini_project",
  "activity_id": "act_project_001",
  "source_pack_ref": "sp_van_001",
  "document_title": "Nghi luan van hoc",
  "lesson_title": "Mo bai va than bai",
  "student_level": "lop_10",
  "instructions": [
    "Tao san pham ngan gon",
    "Bam sat de bai"
  ],
  "activity_data": {
    "brief": "Viet mot mo bai ngan cho de phan tich ve dep cua nhan vat.",
    "deliverable_type": "paragraph",
    "constraints": [
      "3-4 cau",
      "Neu duoc thi co 1 cau dan vao tac pham"
    ],
    "rubric": [
      "Dung de bai",
      "Mo bai tu nhien",
      "Ngon ngu ro rang"
    ]
  }
}
<<<ACTIVITY_PAYLOAD_V2_END>>>
```

#### Feedback example

```text
<<<ACTIVITY_FEEDBACK_V2_START>>>
{
  "payload_type": "activity_feedback",
  "activity_type": "mini_project",
  "activity_id": "act_project_001",
  "student_submission": {
    "response_type": "short_essay",
    "response_content": "Nhan vat hien len voi ve dep noi tam va su ben bi truoc nghich canh..."
  },
  "feedback": {
    "overall_verdict": "partial",
    "strengths": [
      "Da di dung huong de bai"
    ],
    "gaps": [
      "Mo bai chua tao duoc cau dan tu nhien"
    ],
    "misconceptions": [],
    "next_step": "Thu viet lai cau mo dau de dan vao tac pham mem hon.",
    "score_optional": "7.5/10",
    "rubric_breakdown": [
      {
        "criterion": "Dung de bai",
        "verdict": "dat",
        "note": "Khong lac chu de"
      },
      {
        "criterion": "Mo bai tu nhien",
        "verdict": "can cai thien",
        "note": "Chuyen y con gap"
      }
    ]
  }
}
<<<ACTIVITY_FEEDBACK_V2_END>>>
```

#### Prompt authoring

```text
Ban la nguoi thiet ke hoat dong `mini_project`.

Du lieu nguon:
{source_pack_json}

Yeu cau:
- Tao 1 san pham nho co gia tri dau ra that.
- Dau ra phai ro loai san pham.
- Chi tao trong pham vi kien thuc cua source pack.
- Tra ve dung schema `mini_project` trong marker V2.
```

#### Prompt feedback

```text
Ban la nguoi cham hoat dong `mini_project`.

Du lieu nguon:
{source_pack_json}

Hoat dong:
{activity_authoring_json}

Bai lam:
{student_submission}

Yeu cau:
- Danh gia theo rubric da cho
- Neu thieu y, noi ro thieu o tieu chi nao
- Tra ve dung schema feedback `mini_project` trong marker V2
```

### 5. `debate_defend`

#### Activity data schema

```json
{
  "claim": "",
  "position_task": "",
  "evidence_rules": ["", ""],
  "rubric": ["", ""]
}
```

#### Feedback add-on

```json
{
  "argument_quality": "",
  "evidence_quality": "",
  "logic_gaps": ["", ""]
}
```

#### Authoring example

```text
<<<ACTIVITY_PAYLOAD_V2_START>>>
{
  "payload_type": "activity_authoring",
  "activity_type": "debate_defend",
  "activity_id": "act_debate_001",
  "source_pack_ref": "sp_gdcd_001",
  "document_title": "Cong dan va trach nhiem xa hoi",
  "lesson_title": "Quyen va nghia vu",
  "student_level": "lop_11",
  "instructions": [
    "Chon lap truong",
    "Bao ve bang 3-4 y ngan"
  ],
  "activity_data": {
    "claim": "Hoc sinh nen tham gia cac hoat dong cong dong dinh ky.",
    "position_task": "Dong y hoac khong dong y, va bao ve lap truong cua em.",
    "evidence_rules": [
      "Chi dung du kien trong bai hoc",
      "Moi y nen co 1 ly do ro rang"
    ],
    "rubric": [
      "Lap truong ro",
      "Ly le hop logic",
      "Dung du lieu phu hop"
    ]
  }
}
<<<ACTIVITY_PAYLOAD_V2_END>>>
```

#### Feedback example

```text
<<<ACTIVITY_FEEDBACK_V2_START>>>
{
  "payload_type": "activity_feedback",
  "activity_type": "debate_defend",
  "activity_id": "act_debate_001",
  "student_submission": {
    "response_type": "short_essay",
    "response_content": "Em dong y vi hoat dong cong dong giup hoc sinh co y thuc trach nhiem va hieu xa hoi hon."
  },
  "feedback": {
    "overall_verdict": "partial",
    "strengths": [
      "Lap truong ro rang"
    ],
    "gaps": [
      "Con it y de bao ve lap luan"
    ],
    "misconceptions": [],
    "next_step": "Bo sung them 1 y ve loi ich doi voi tap the hoac cong dong.",
    "score_optional": "7/10",
    "argument_quality": "Lap luan co huong dung nhung chua day du.",
    "evidence_quality": "Dung y trong bai hoc nhung con it dan chieu.",
    "logic_gaps": [
      "Chua mo rong tac dong tu ca nhan sang cong dong"
    ]
  }
}
<<<ACTIVITY_FEEDBACK_V2_END>>>
```

#### Prompt authoring

```text
Ban la nguoi thiet ke hoat dong `debate_defend`.

Du lieu nguon:
{source_pack_json}

Yeu cau:
- Tao 1 nhan dinh co the tranh luan trong pham vi bai hoc.
- Hoc sinh phai chon lap truong va bao ve.
- Khong duoc can den thong tin ngoai source pack.
- Tra ve dung schema `debate_defend` trong marker V2.
```

#### Prompt feedback

```text
Ban la nguoi cham hoat dong `debate_defend`.

Du lieu nguon:
{source_pack_json}

Hoat dong:
{activity_authoring_json}

Bai lam:
{student_submission}

Yeu cau:
- Danh gia do ro cua lap truong
- Danh gia chat luong lap luan va dan chieu
- Chi ra logic gap neu co
- Tra ve dung schema feedback `debate_defend` trong marker V2
```

## Prompt repair

### Repair authoring payload

```text
Ban vua tra sai format cho activity authoring.

Hay sua lai theo cac rule sau:
- Chi tra ve 1 block duy nhat giua:
  <<<ACTIVITY_PAYLOAD_V2_START>>>
  ...
  <<<ACTIVITY_PAYLOAD_V2_END>>>
- JSON hop le
- Giu nguyen noi dung neu hop le
- Khong them markdown, khong them giai thich
- Phai dung schema cua `activity_type` da duoc yeu cau

Payload cu:
{{BROKEN_OUTPUT}}
```

### Repair feedback payload

```text
Ban vua tra sai format cho activity feedback.

Hay sua lai theo cac rule sau:
- Chi tra ve 1 block duy nhat giua:
  <<<ACTIVITY_FEEDBACK_V2_START>>>
  ...
  <<<ACTIVITY_FEEDBACK_V2_END>>>
- JSON hop le
- Giu nguyen y feedback neu hop le
- Khong them markdown, khong them giai thich
- Phai dung schema feedback cua `activity_type`

Payload cu:
{{BROKEN_OUTPUT}}
```

## Reject cases bat buoc

Web phai reject neu gap 1 trong cac truong hop sau:

1. sai marker
2. co text ngoai marker
3. parse JSON that bai
4. `payload_type` khong hop le
5. `activity_type` ngoai 5 gia tri Wave 1
6. thieu `source_pack_ref` trong authoring payload
7. thieu `student_submission` trong feedback payload
8. `feedback.next_step` rong
9. `activity_data` sai schema theo `activity_type`
10. payload nhac toi `decision_path` hoac `speed_challenge` nhu la Wave 1 contract

## Review checklist

Sau khi doc xong spec V2, implementer phai tra loi duoc:

1. ingest gi o Wave 1
2. feedback gi o Wave 1
3. `source_pack` dung de lam gi
4. V1 duoc giu lai nhu the nao
5. format nao de phase sau

Neu 1 trong 5 cau tren chua ro, xem nhu spec chua dat.
