# Moc 0 Debug And Test Checklist

## Muc tieu

File nay ghi lai cac mismatch contract da tim thay trong `Moc 0`, cach chot cuoi, va checklist debug/test de verify xong la xong that.

## Danh sach mismatch da tim thay

### 1. `response_type` lech giua workflow va frontend spec

- Workflow V2: `free_text | bullet_points | short_essay`
- Frontend implementation spec cu: `plain_text | bullet_list | structured_text`

### 2. Source pack lech root field

- Workflow V2 co:
  - `formulas`
  - `events_or_milestones`
- Frontend spec cu chua map du

### 3. `source_notes` lech type

- Workflow V2 cu: string
- Frontend/backend normalized: list

### 4. Rule ID tao moi chua ro

- `source_pack_ref` o source pack
- `activity_id` o authoring payload

Van de:

- docs chua noi ro co the de rong hay backend phai sinh

### 5. `score_optional` lech type

- Workflow examples dung string
- Frontend spec cu chi cho number/null

### 6. Validation issue code lech giua backend va frontend spec

Backend dang tra them:

- `text_outside_marker`
- `response_type_invalid`
- `reference_not_found`
- `route_mismatch`

Frontend spec cu chua map du.

## Contract da chot sau Moc 0

### Source pack

Canonical root fields:

- `payload_type`
- `source_pack_ref`
- `subject`
- `grade_level`
- `chapter_title`
- `lesson_title`
- `learning_objectives`
- `key_concepts`
- `formulas`
- `events_or_milestones`
- `examples`
- `common_mistakes`
- `prerequisites`
- `source_notes`
- `coverage_warning`

Rule chot:

1. `payload_type` phai la `source_pack`
2. `source_pack_ref` phai ton tai trong payload, nhung co the de rong khi tao moi
3. `source_notes` la `string[]`
4. `formulas` va `events_or_milestones` la field root bat buoc

### Activity authoring

Rule chot:

1. `activity_id` phai ton tai trong payload
2. `activity_id` co the rong khi create flow
3. Neu rong, backend sinh luc save
4. `source_pack_ref` phai khong rong va tro dung source pack da luu

### Activity feedback

Rule chot:

1. `response_type` chi nhan:
   - `free_text`
   - `bullet_points`
   - `short_essay`
2. `score_optional` nhan:
   - `string`
   - `number`
   - `null`

## File da sua trong Moc 0

- `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
- `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
- `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md`
- `handoff_api/validation.py`
- `tests/test_handoff_api.py`

## Debug checklist

### A. Doc alignment

- [x] Workflow V2 noi dung schema source pack da co `payload_type`
- [x] Workflow V2 noi dung schema source pack da co `source_pack_ref`
- [x] Workflow V2 da chot `source_notes` la array
- [x] Workflow V2 da noi ro `activity_id` co the rong khi create
- [x] Frontend spec da dung `response_type` theo V2
- [x] Frontend spec da them `formulas` va `events_or_milestones`
- [x] Frontend spec da map them validation issue code cua backend

### B. Backend alignment

- [x] Validator source pack yeu cau `payload_type`
- [x] Validator source pack yeu cau `source_pack_ref` field ton tai
- [x] Validator source pack yeu cau `source_notes` la array string
- [x] Validator activity authoring yeu cau `activity_id` field ton tai
- [x] Validator feedback reject `response_type` sai

### C. Regression / compatibility note

- [x] Save source pack van sinh duoc ID neu `source_pack_ref = ""`
- [x] Save activity van sinh duoc ID neu `activity_id = ""`
- [x] Feedback van bat buoc `activity_id` that

## Test checklist

### Da co test tu dong

- [x] validate source pack normalize dung schema moi
- [x] create/get source pack
- [x] activity validate reject `source_pack_ref` khong ton tai
- [x] source pack reject `source_notes` sai type
- [x] activity authoring reject khi thieu `activity_id`
- [x] full flow activity -> submission -> feedback
- [x] reject text ngoai marker
- [x] reject `response_type` khong hop le

### Lenh verify

```powershell
python -m unittest tests.test_handoff_api -v
python -m unittest discover -s tests -v
rg -n "response_type|source_notes|formulas|events_or_milestones|activity_id|source_pack_ref|score_optional" AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md handoff_api\validation.py tests\test_handoff_api.py
```

## Ket qua sau Moc 0

- Doc alignment: `2/2`
- Backend alignment: `2/2`
- Test alignment: `2/2`
- Tong: `6/6`

Danh gia:

- `Done`

Buoc tiep theo:

- `Moc 1 - Frontend vertical slice`
