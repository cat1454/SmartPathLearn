# AI Document Handoff - M2 Debug Test Checklist

## Muc tieu M2

- Lam ro `load / validate / save` tren UI.
- Hien marker expected va bang issue de sua payload nhanh hon.
- Co `repair prompt` copy nhanh.
- Co preview normalized de soat schema truoc khi luu.
- Them nut doi ngon ngu `Tiếng Việt / English` cho frontend handoff.

## Da lam

1. UI them `status strip` cho source pack, activity, submission, feedback.
2. Validation panel hien:
   - tong so loi / canh bao
   - code
   - path
   - message dich theo locale
   - expected value neu co
3. Them `marker guide` rieng cho 3 envelope:
   - `SOURCE_PACK_V1`
   - `ACTIVITY_PAYLOAD_V2`
   - `ACTIVITY_FEEDBACK_V2`
4. Them `payload normalized preview`.
5. Them `repair prompt` ro hon va locale-aware prompt builder.
6. Them `language toggle`:
   - `Tiếng Việt`
   - `English`
   - luu qua `localStorage`
7. Khi payload thay doi, UI reset validation state de ep validate lai.

## Debug checklist

- [x] Validate source pack hien status `dang validate -> hop le/chua hop le`
- [x] Save source pack hien status `dang luu -> da luu/loi`
- [x] Activity page co marker guide + normalized preview
- [x] Feedback page co marker guide + normalized preview
- [x] Nut doi ngon ngu doi duoc text UI chinh
- [x] Prompt copy / repair prompt van dung duoc sau khi doi ngon ngu
- [x] Save button bi khoa khi chua co validation hop le

## Test checklist

### Backend / contract

- [x] `python -m unittest tests.test_handoff_api -v`
- [x] `python -m unittest discover -s tests -v`

### Frontend syntax

- [x] `node --check handoff_ui\\app.js`
- [x] `node --check handoff_ui\\components.js`
- [x] `node --check handoff_ui\\prompts.js`
- [x] `node --check handoff_ui\\i18n.js`
- [x] `node --check handoff_ui\\api.js`
- [x] `node --check handoff_ui\\router.js`

### Runtime smoke

- [x] Route `/handoff/source-packs/new` tra `200`
- [x] Asset `i18n.js` co `Tiếng Việt` va `English`
- [x] Asset `components.js` co `data-set-locale` va `renderStatusStrip`

## 5 case verify cua M2

- [x] text ngoai marker
- [x] thieu field required
- [x] sai `activity_type`
- [x] sai `response_type`
- [x] payload hop le

## Checkpoint - Moc 2

Ngay:

- 2026-04-09

File chinh:

- `handoff_ui/app.js`
- `handoff_ui/components.js`
- `handoff_ui/prompts.js`
- `handoff_ui/i18n.js`
- `handoff_ui/styles.css`
- `tests/test_handoff_api.py`

Lenh verify:

- `python -m unittest tests.test_handoff_api -v`
- `python -m unittest discover -s tests -v`
- `node --check handoff_ui\\app.js`
- `node --check handoff_ui\\components.js`
- `node --check handoff_ui\\prompts.js`
- `node --check handoff_ui\\i18n.js`
- `node --check handoff_ui\\api.js`
- `node --check handoff_ui\\router.js`

Ket qua:

- test backend xanh
- syntax check frontend xanh
- runtime smoke route + asset xanh

Diem tien do:

- Error clarity: `2/2`
- Repair path: `2/2`
- Preview clarity: `2/2`
- tong: `6/6`

Danh gia:

- `Done`

Buoc tiep theo:

- `Moc 4 - Hardening va test expansion`
