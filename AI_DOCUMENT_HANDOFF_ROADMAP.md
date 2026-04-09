# AI Document Handoff Roadmap

## Muc tieu

Tai lieu nay chot **buoc tiep theo nen lam gi** de di tu:

- co spec
- co backend scaffold

sang:

- co vertical slice chay duoc
- co demo web dung duoc
- co nen tang de mo rong sau do

Roadmap nay bam sat trang thai repo hien tai, khong viet theo kieu wishlist chung chung.

## Trang thai hien tai

### Da co

1. CLI sinh quiz tu PDF dang chay duoc
   - `pdf_to_quiz.py`
   - `pdf_to_quiz_core/*`
2. Spec V2 cho handoff da co
   - `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
   - `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md`
   - `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
3. Backend V1 da scaffold va test xanh
   - `handoff_api/main.py`
   - `handoff_api/validation.py`
   - `handoff_api/storage.py`
   - `tests/test_handoff_api.py`
4. API route da co:
   - `POST /source-packs/validate`
   - `POST /source-packs`
   - `GET /source-packs/{source_pack_id}`
   - `POST /activities/validate`
   - `POST /activities`
   - `GET /activities/{activity_id}`
   - `POST /activities/{activity_id}/submission`
   - `POST /activities/{activity_id}/feedback/validate`
   - `POST /activities/{activity_id}/feedback`

### Chua co hoac chua chot

1. Da co frontend vertical slice cho flow handoff duoi `/handoff/...`
2. Contract schema da duoc chot cho V2 / frontend spec / backend validator
3. Storage hien la JSON file local, chua phai DB
4. Chua co list page, auth, teacher dashboard, history

## Nguyen tac lam tiep

1. Chot contract truoc khi do frontend.
2. Lam theo **vertical slice** thay vi tan man.
3. Moi moc phai co:
   - file thay doi
   - command verify
   - ket qua danh gia
4. Khong mo rong format moi khi 5 format Wave 1 chua on.
5. Chua lam auth/dashboard som; uu tien flow dau-cuoi truoc.

## Bang tong quan tien do

| Moc | Noi dung | Trang thai hien tai | Ket qua mong muon |
|---|---|---|---|
| 0 | Chot contract schema | Done (2026-04-09) | 1 schema thong nhat |
| 1 | Frontend vertical slice | Done (2026-04-09) | Tao -> validate -> luu -> xem lai |
| 2 | UX validation / repair | Done (2026-04-09) | Nguoi dung dan payload de dung on dinh |
| 4 | Hardening va test | Chua bat dau | Test mo rong + reject case day du |
| 3 | Cloud persistence | Chua bat dau | Cloud SQL Postgres thay JSON store |
| 5 | Deploy len Cloud Run | Chua bat dau | Ban chay duoc tren Google Cloud |
| 6 | Demo / pilot | Chua bat dau | Co flow noi bo de dung thu |

---

## Moc 0 - Chot contract schema

### Muc tieu

Lam cho 3 lop sau noi cung 1 ngon ngu:

- `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
- `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
- `handoff_api/validation.py`

### Viec can lam

1. Chot `response_type` Wave 1:
   - `free_text`
   - `bullet_points`
   - `short_essay`
2. Chot `source_notes` la `string` hay `string[]`
3. Chot co hay khong:
   - `formulas`
   - `events_or_milestones`
   trong source pack contract
4. Chot rule voi:
   - `source_pack_ref`
   - `activity_id`
   la AI phai tra ve san hay backend duoc sinh khi save
5. Cap nhat lai spec + backend validator theo cung mot contract

### File du kien dong vao

- `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
- `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
- `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md`
- `handoff_api/contracts.py`
- `handoff_api/validation.py`
- `tests/test_handoff_api.py`

### Dieu kien hoan thanh

1. Khong con field lech ten/le chuan giua 3 tang docs + backend
2. Test backend khong can workaround vi spec mo ho
3. Readme va prompt docs noi cung 1 contract

### Verify bat buoc

```powershell
python -m unittest tests.test_handoff_api -v
rg -n "response_type|source_notes|formulas|events_or_milestones|activity_id|source_pack_ref" AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md handoff_api\validation.py handoff_api\contracts.py
```

### Danh gia tien do sau khi xong

- Contract alignment: `0/1/2`
- Backend alignment: `0/1/2`
- Doc alignment: `0/1/2`
- Tong ket:
  - `0-2`: chua dat
  - `3-4`: dat mot phan
  - `5-6`: dat

---

## Moc 1 - Frontend vertical slice

### Muc tieu

Co 1 flow UI toi thieu de nguoi dung di het 1 vong:

1. tao `source_pack`
2. tao `activity`
3. nhap `submission`
4. dan `feedback payload`
5. load lai thay du lieu da luu

### Viec can lam

1. Chon framework/frontend shell that
   - neu chua co web app, uu tien React + Vite hoac Next.js
2. Scaffold feature `handoff`
3. Lam toi thieu 4 screen:
   - source pack create
   - activity create
   - activity detail
   - feedback page
4. Noi API backend V1
5. Render preview cho `case_mission` truoc, sau do mo rong 4 format con lai

### File/thu muc du kien

- `src/features/handoff/*` hoac equivalent theo framework
- route/page component
- API client/service layer

### Dieu kien hoan thanh

1. UI goi duoc backend dang chay
2. Paste payload hop le thi save duoc
3. Reload lai van thay source pack / activity / feedback
4. It nhat `case_mission` chay dau-cuoi

### Verify bat buoc

1. Chay backend local
2. Chay frontend local
3. Tu tay di het 1 flow demo
4. Ghi lai:
   - URL
   - buoc nao thanh cong
   - screenshot neu can

### Danh gia tien do sau khi xong

- Create source pack UI: `0/1/2`
- Create activity UI: `0/1/2`
- Feedback flow UI: `0/1/2`
- End-to-end demo: `0/1/2`
- Tong ket:
  - `0-3`: chua dat
  - `4-6`: dat mot phan
  - `7-8`: dat

---

## Moc 2 - UX validation va repair

### Muc tieu

Lam cho viec copy/paste payload khong bi roi vao vung mo ho.

### Viec can lam

1. Hien loi theo field ro rang
2. Hien marker expected
3. Hien payload parse thanh cong o dang preview
4. Them `repair prompt` copy nhanh
5. Phan tach:
   - load error
   - validation error
   - save error

### Dieu kien hoan thanh

1. Sai marker thi UI bao dung marker nao dang can
2. Sai schema thi UI chi ro field nao sai
3. Paste lai payload sua xong thi qua duoc

### Verify bat buoc

Dung it nhat 5 case:

1. text ngoai marker
2. thieu field required
3. sai `activity_type`
4. sai `response_type`
5. payload hop le

### Danh gia tien do sau khi xong

- Error clarity: `0/1/2`
- Repair path: `0/1/2`
- Preview clarity: `0/1/2`
- Tong ket:
  - `0-2`: chua dat
  - `3-4`: dat mot phan
  - `5-6`: dat

---

## Moc 3 - Cloud persistence voi Cloud SQL Postgres

### Muc tieu

Thoat khoi JSON store muc demo, dua backend len storage dung duoc that tren Google Cloud.

### Viec can lam

1. Tach `JsonStore` thanh storage interface ro rang
2. Tao Postgres-backed store cho Cloud SQL
3. Tao bang:
   - `source_packs`
   - `activities`
   - `submissions`
   - `feedbacks`
4. Giu route va response shape hien tai
5. Them config runtime:
   - `HANDOFF_STORAGE_BACKEND=postgres`
   - `HANDOFF_DATABASE_URL`
6. Viet migration/bootstrapping schema cho local dev va Cloud SQL
7. Neu them list API thi lam sau khi persistence da on, khong de no chan migration

### Dieu kien hoan thanh

1. Khong phu thuoc file JSON de chay app tren môi truong cloud
2. Restart app khong mat du lieu
3. Detail flow hien tai van chay voi route cu
4. Test save/load chay duoc voi Postgres backend

### Verify bat buoc

1. Tao 2 source pack
2. Tao 2 activity
3. Save submission + feedback
4. Restart app
5. Goi lai detail endpoint va doi chieu du lieu
6. Chay full test suite voi backend `postgres`

### Danh gia tien do sau khi xong

- Persistence: `0/1/2`
- Runtime config: `0/1/2`
- Backward compatibility: `0/1/2`
- Tong ket:
  - `0-2`: chua dat
  - `3-4`: dat mot phan
  - `5-6`: dat

---

## Moc 4 - Hardening va test expansion

### Muc tieu

Giam bug contract va regression truoc khi doi storage va dua len cloud.

### Viec can lam

1. Them test reject case cho backend
2. Them test mismatch giua route param va payload
3. Them test save/load voi cac `activity_type` khac ngoai `case_mission`
4. Them test UI cho flow paste payload neu co frontend
5. Review lai message error cho de dung
6. Chot lai reject case Wave 1 de M3 khong phai sua contract nua

### Dieu kien hoan thanh

1. Co test cho 5 format Wave 1 o muc backend validator
2. Co test cho nhung reject case bat buoc trong spec
3. Khong co regression o flow da xanh

### Verify bat buoc

```powershell
python -m unittest discover -s tests -v
```

Neu da co frontend test:

```powershell
# tuy framework ma them lenh test tuong ung
```

### Danh gia tien do sau khi xong

- Validator coverage: `0/1/2`
- Route coverage: `0/1/2`
- Regression confidence: `0/1/2`
- Tong ket:
  - `0-2`: chua dat
  - `3-4`: dat mot phan
  - `5-6`: dat

---

## Moc 5 - Deploy len Cloud Run

### Muc tieu

Dua backend/frontend slice len Google Cloud o muc co the dung va verify duoc.

### Viec can lam

1. Viet `Dockerfile` cho app FastAPI + UI shell
2. Them config env cho Cloud Run:
   - `HANDOFF_STORAGE_BACKEND`
   - `HANDOFF_DATABASE_URL` hoac Cloud SQL binding
   - `PORT`
3. Cau hinh ket noi Cloud SQL Postgres
4. Chot health check va startup command
5. Neu co file upload/export thi noi Cloud Storage bucket cho object/file
6. Viet huong dan deploy `gcloud run deploy`

### Dieu kien hoan thanh

1. App len duoc Cloud Run
2. App doc/ghi duoc Cloud SQL
3. Route `/health` va flow handoff co the verify duoc sau deploy
4. Cloud Storage chi dung cho file/object, khong la he thong record chinh

### Verify bat buoc

1. Build image thanh cong
2. Deploy len Cloud Run thanh cong
3. Goi `/health`
4. Tao 1 `source_pack`
5. Tao 1 `activity`
6. Save 1 `submission`
7. Save 1 `feedback`

### Danh gia tien do sau khi xong

- Cloud deploy: `0/1/2`
- DB connectivity: `0/1/2`
- Runtime verification: `0/1/2`
- Tong ket:
  - `0-2`: chua dat
  - `3-4`: dat mot phan
  - `5-6`: dat

---

## Moc 6 - Ban demo / pilot

### Muc tieu

Ra duoc 1 ban demo sau khi da co cloud runtime on dinh.

### Viec can lam

1. Lam landing route cho handoff tool neu can
2. Lam list page co ban:
   - source packs
   - activities
3. Viet huong dan thao tac ngan
4. Chuan bi bo payload mau cho 2-3 mon hoc
5. Chay 1 vong pilot tu tai lieu -> prompt -> payload -> feedback

### Dieu kien hoan thanh

1. Nguoi khac co the tu thao tac khong can mo source code
2. Co 1-2 flow mau de demo
3. Ghi nhan duoc pain point that tu user

### Verify bat buoc

1. Cho 1 nguoi khac dung thu
2. Ghi lai:
   - buoc nao bi dung
   - buoc nao hieu ngay
   - loi nao lap lai
3. Tong hop feedback thanh backlog tiep theo

### Danh gia tien do sau khi xong

- Demo completeness: `0/1/2`
- User self-serve level: `0/1/2`
- Pilot feedback quality: `0/1/2`
- Tong ket:
  - `0-2`: chua dat
  - `3-4`: dat mot phan
  - `5-6`: dat

---

## Thu tu uu tien de lam ngay

Neu chi lam theo thu tu thuc chien nhat, thi:

1. **Moc 0** - Chot contract schema
2. **Moc 1** - Frontend vertical slice
3. **Moc 2** - UX validation va repair
4. **Moc 4** - Hardening va test expansion
5. **Moc 3** - Cloud persistence voi Cloud SQL Postgres
6. **Moc 5** - Deploy len Cloud Run
7. **Moc 6** - Ban demo / pilot

Ly do:

- Neu contract chua chot, frontend se code sai huong
- Neu chua co vertical slice, storage tot hon cung chua giup demo
- Hardening sau khi co flow that se hieu qua hon
- Cloud SQL nen duoc dua vao sau khi reject case va regression da chac
- Cloud Storage chi dung cho file/object, khong dung lam DB trong huong nay

## Mau checkpoint bat buoc sau moi moc

Sau moi moc, phai them 1 block danh gia vao changelog hoac note task theo mau nay:

```md
## Checkpoint - [Ten moc]

Ngay:

Ket qua:
- da xong gi
- chua xong gi

File chinh:
- ...

Lenh verify:
- ...

Ket qua verify:
- ...

Diem tien do:
- tieu chi 1: 0/1/2
- tieu chi 2: 0/1/2
- tieu chi 3: 0/1/2
- tong: x/6 hoac x/8

Danh gia:
- Done
- Partial
- Blocked

Buoc tiep theo:
- ...
```

## De xuat ngay luc nay

Moc nen lam tiep ngay la:

### `Moc 4 - Hardening va test expansion`

Ly do:

- contract va vertical slice da co diem dung ro
- M2 da giam ma sat nguoi dung o lop UX va validation
- buoc tiep theo hop ly nhat la mo rong test reject case va tang do tin cay truoc khi doi sang Cloud SQL va deploy cloud

## Checkpoint - Moc 0

Ngay:

- 2026-04-09

Ket qua:

- da chot lai contract schema giua workflow V2, frontend implementation spec, web screen spec, va backend validator
- da bo sung list debug/test rieng tai `AI_DOCUMENT_HANDOFF_M0_DEBUG_TEST_CHECKLIST.md`
- da them test cho `response_type` sai va cap nhat test source pack theo schema moi

File chinh:

- `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
- `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md`
- `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md`
- `handoff_api/validation.py`
- `tests/test_handoff_api.py`
- `AI_DOCUMENT_HANDOFF_M0_DEBUG_TEST_CHECKLIST.md`

Lenh verify:

- `python -m unittest tests.test_handoff_api -v`
- `python -m unittest discover -s tests -v`
- `rg -n "response_type|source_notes|formulas|events_or_milestones|activity_id|source_pack_ref|score_optional" AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md handoff_api\validation.py tests\test_handoff_api.py`

Ket qua verify:

- backend test xanh
- contract grep ra cung field va enum giua doc + code

Diem tien do:

- contract alignment: `2/2`
- backend alignment: `2/2`
- test alignment: `2/2`
- tong: `6/6`

Danh gia:

- `Done`

Buoc tiep theo:

- `Moc 1 - Frontend vertical slice`

## Checkpoint - Moc 1

Ngay:

- 2026-04-09

Ket qua:

- da scaffold frontend vertical slice duoi `handoff_ui/*`
- da serve UI bang chinh FastAPI app
- da cover route source pack, activity, submission, feedback
- da noi API validate/save/load vao UI
- da co route test va asset test cho frontend shell

File chinh:

- `handoff_ui/index.html`
- `handoff_ui/styles.css`
- `handoff_ui/app.js`
- `handoff_ui/api.js`
- `handoff_ui/router.js`
- `handoff_ui/prompts.js`
- `handoff_ui/components.js`
- `handoff_api/main.py`
- `tests/test_handoff_api.py`
- `AI_DOCUMENT_HANDOFF_M1_DEBUG_TEST_CHECKLIST.md`

Lenh verify:

- `python -m unittest tests.test_handoff_api -v`
- `python -m unittest discover -s tests -v`
- chay server local va mo `/handoff/source-packs/new`

Ket qua verify:

- route shell va asset frontend duoc serve
- test backend va frontend shell deu xanh
- flow API source pack -> activity -> submission -> feedback van xanh

Diem tien do:

- Create source pack UI: `2/2`
- Create activity UI: `2/2`
- Feedback flow UI: `2/2`
- End-to-end demo: `2/2`
- tong: `8/8`

Danh gia:

- `Done`

Buoc tiep theo:

- `Moc 2 - UX validation va repair`

## Checkpoint - Moc 2

Ngay:

- 2026-04-09

Ket qua:

- da tach ro `load / validate / save` state trong frontend handoff
- da them issue table, marker guide, normalized preview, va repair prompt ro hon
- da them nut doi ngon ngu `Tiếng Việt / English` cho web handoff va luu locale bang `localStorage`
- da cap nhat prompt builder de doi theo locale chon tren UI
- da them frontend asset smoke test cho `i18n.js`, `components.js`, `styles.css`

File chinh:

- `handoff_ui/app.js`
- `handoff_ui/components.js`
- `handoff_ui/prompts.js`
- `handoff_ui/i18n.js`
- `handoff_ui/styles.css`
- `tests/test_handoff_api.py`
- `AI_DOCUMENT_HANDOFF_M2_DEBUG_TEST_CHECKLIST.md`

Lenh verify:

- `python -m unittest tests.test_handoff_api -v`
- `python -m unittest discover -s tests -v`
- `node --check handoff_ui\\app.js`
- `node --check handoff_ui\\components.js`
- `node --check handoff_ui\\prompts.js`
- `node --check handoff_ui\\i18n.js`
- `node --check handoff_ui\\api.js`
- `node --check handoff_ui\\router.js`
- runtime smoke route `/handoff/source-packs/new` + asset `i18n.js` + asset `components.js`

Ket qua verify:

- backend test xanh
- frontend syntax check xanh
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
