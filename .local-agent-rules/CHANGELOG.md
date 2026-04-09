# Local Agent Change Log

Log nay dung de Agent note lai ket qua xu ly sau moi prompt. File nay chi co tac dung local trong repo nay.

## 2026-04-09 12:26

Prompt:
- Mo rong spec handoff V2 theo huong `source_pack + activity payload + feedback payload`.
- Tao them screen de nhin flow de hieu hon.

Thay doi:
- Cap nhat `AI_DOCUMENT_HANDOFF_WORKFLOW.md` de gan nhan ro day la legacy quiz-only spec cho `QUIZ_PAYLOAD_V1`.
- Tao `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md` de chot kien truc V2:
  - `source_pack`
  - `activity_authoring`
  - `activity_feedback`
  - 5 format Wave 1: `case_mission`, `error_hunt`, `explain_back`, `mini_project`, `debate_defend`
  - prompt authoring / feedback / repair
  - marker va reject rules
- Tao `AI_DOCUMENT_HANDOFF_SCREENS.html` de mockup 6 man hinh chinh:
  - tao source pack
  - chon format
  - copy prompt authoring
  - paste payload + validate/repair
  - nop bai hoc sinh
  - paste feedback payload
- Cap nhat V2 spec de link sang file screen mockup.

Verify:
- Da grep lai marker `SOURCE_PACK_V1`, `ACTIVITY_PAYLOAD_V2`, `ACTIVITY_FEEDBACK_V2` trong V2 spec va screen mockup.
- Da grep lai 6 heading screen trong `AI_DOCUMENT_HANDOFF_SCREENS.html`.

Con lai:
- Screen hien la mockup HTML tinh de thong nhat flow, chua phai frontend implementation.
- Neu can, buoc tiep theo hop ly la doi mockup nay thanh wireframe chi tiet hon cho mobile + desktop hoac map thang sang route/component that.

## 2026-04-09 12:32

Prompt:
- Chuyen mockup handoff thanh screen spec chi tiet hon cho web.

Thay doi:
- Tao `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md` de chot:
  - route de xuat
  - layout desktop/tablet/mobile
  - component chung
  - 6 screen spec chi tiet
  - CTA chinh/phu
  - state model
  - validation theo tung screen
  - mapping voi contract `SOURCE_PACK_V1`, `ACTIVITY_PAYLOAD_V2`, `ACTIVITY_FEEDBACK_V2`
- Cap nhat `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md` de link sang screen spec moi.

Verify:
- Da grep lai route, heading screen, va cac marker contract trong screen spec va V2 workflow.
- Da doi chieu screen spec moi voi mockup HTML de dam bao van bam 6 man hinh chinh da thong nhat truoc do.

Con lai:
- Screen spec da du chi tiet de handoff cho web, nhung chua phan ra component API props hoac state machine cap code.
- Neu can, buoc tiep theo hop ly la viet tiep `frontend implementation spec` theo tung route/component.

## 2026-04-09 12:36

Prompt:
- Viet tiep mot frontend implementation spec theo kieu `route -> component tree -> props/data contract` de dev bat tay code luon.

Thay doi:
- Tao `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md` de chot lop implementation frontend gom:
  - 6 route chinh trong flow handoff
  - file structure goi y cho frontend
  - shared types va payload contracts
  - shared component props contract
  - route-by-route component tree
  - save/load contract cho tung page
  - validation matrix cho `SOURCE_PACK_V1`, `ACTIVITY_PAYLOAD_V2`, `ACTIVITY_FEEDBACK_V2`
  - hook boundary goi y de code page sach hon
- Cap nhat `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md` de link sang implementation spec moi.
- Cap nhat `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md` de chi ro tai lieu implementation tiep theo.

Verify:
- Da doi 3 tang tai lieu thanh chuoi ro: workflow -> screen spec -> implementation spec.
- Implementation spec da map du 6 route, component tree, props/data contract, va validation boundary cho Wave 1.

Con lai:
- Tai lieu moi da o muc code-ready cho frontend, nhung chua chot framework-specific detail nhu React Router, Next.js App Router, hoac store library.
- Neu can, buoc tiep theo hop ly la doi spec nay thanh skeleton folder + stub component/interface trong codebase that.

## 2026-04-09 13:01

Prompt:
- Scaffold backend V1 theo FastAPI cho flow handoff:
  - schema/parser/validator cho 3 envelope
  - storage
  - 9 endpoint chinh
  - test ingest/validate/save/load

Thay doi:
- Tao package `handoff_api` gom:
  - `contracts.py` cho request/response model va enum domain
  - `validation.py` cho parse marker + validate `SOURCE_PACK_V1`, `ACTIVITY_PAYLOAD_V2`, `ACTIVITY_FEEDBACK_V2`
  - `storage.py` cho file-based JSON store
  - `main.py` cho app FastAPI va 9 route V1
- Tao `requirements-handoff-api.txt` voi `fastapi` va `uvicorn`.
- Tao `tests/test_handoff_api.py` de cover:
  - validate source pack
  - create/get source pack
  - reject activity khi `source_pack_ref` khong ton tai
  - full flow activity -> submission -> feedback
  - reject text ngoai marker
- Tao `README_handoff_api.md` de chi nhanh cach cai, chay server, va test.

Verify:
- Da cai dependency backend tu `requirements-handoff-api.txt`.
- `python -m unittest tests.test_handoff_api -v` -> OK
- `python -m unittest discover -s tests -v` -> OK
- Da introspect route app va xac nhan du 9 endpoint V1 + `/health`.

Con lai:
- Storage hien la JSON file local, chua co DB hay migration.
- Validator dang practical-first: co mot so cho chap nhan thieu `source_pack_ref`/`activity_id` luc validate va sinh luc save de giam ma sat giua cac spec dang con lech nhe.
- Chua co auth, pagination, hay teacher dashboard.

## 2026-04-09 13:10

Prompt:
- Viet roadmap vao file md, bam sat trang thai hien tai, va moi lan xong phai co checkpoint danh gia tien do.

Thay doi:
- Tao `AI_DOCUMENT_HANDOFF_ROADMAP.md` gom:
  - trang thai hien tai cua repo
  - 6 moc thuc thi tu contract -> frontend -> UX -> storage -> hardening -> demo
  - dieu kien hoan thanh cho tung moc
  - lenh verify bat buoc cho tung moc
  - rubric danh gia tien do sau moi moc
  - mau checkpoint de dung lai sau moi chang
- Cap nhat `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md` de link sang roadmap moi.
- Cap nhat `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md` de link sang roadmap moi.

Verify:
- Da grep lai roadmap co du cac phan:
  - `Moc 0`
  - `Moc 5`
  - `Danh gia tien do sau khi xong`
  - `Mau checkpoint bat buoc sau moi moc`
- Da grep lai link `AI_DOCUMENT_HANDOFF_ROADMAP.md` trong V2 workflow va web screen spec.

Con lai:
- Roadmap da chot huong va cach tu danh gia, nhung chua bien thanh issue/task board.
- Buoc tiep theo hop ly nhat van la thuc hien `Moc 0 - Chot contract schema`.

## 2026-04-09 13:17

Prompt:
- Lam `Moc 0 - Chot contract schema`, tu lap list debug/test, tu resolve, va ghi checkpoint tien do.

Thay doi:
- Chot lai contract giua docs va backend:
  - `response_type` = `free_text | bullet_points | short_essay`
  - `source_notes` = `string[]`
  - source pack bat buoc co `formulas`, `events_or_milestones`
  - `source_pack_ref` ton tai trong source pack payload, co the rong khi create
  - `activity_id` ton tai trong authoring payload, co the rong khi create
  - `score_optional` = `string | number | null`
- Cap nhat `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md` cho schema/rule source pack, authoring, feedback.
- Cap nhat `AI_DOCUMENT_HANDOFF_FRONTEND_IMPLEMENTATION_SPEC.md` cho types, validation issue codes, validation matrix, va ID generation rule.
- Cap nhat `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md` de chot `response_type` choices.
- Cap nhat `handoff_api/validation.py` de backend enforce contract moi.
- Cap nhat `tests/test_handoff_api.py`:
  - sua payload mau theo schema moi
  - them test reject `source_notes` sai type
  - them test reject authoring payload khi thieu `activity_id`
  - giu test reject `response_type` sai
- Tao `AI_DOCUMENT_HANDOFF_M0_DEBUG_TEST_CHECKLIST.md` de note:
  - mismatch da tim thay
  - contract cuoi cung
  - checklist debug
  - checklist test
  - diem checkpoint
- Cap nhat `AI_DOCUMENT_HANDOFF_ROADMAP.md`:
  - danh dau Moc 0 da done
  - doi de xuat tiep theo sang Moc 1
  - them block `Checkpoint - Moc 0`
- Cap nhat `README_handoff_api.md` de phan note contract khop voi Moc 0.

Verify:
- `python -m unittest tests.test_handoff_api -v` -> OK (8 test backend handoff)
- `python -m unittest discover -s tests -v` -> OK (13 test tong)
- grep contract giua docs + backend + tests theo cac field:
  - `response_type`
  - `source_notes`
  - `formulas`
  - `events_or_milestones`
  - `activity_id`
  - `source_pack_ref`
  - `score_optional`
- grep lai roadmap co `Checkpoint - Moc 0` va de xuat tiep theo la `Moc 1 - Frontend vertical slice`

Checkpoint:
- contract alignment: `2/2`
- backend alignment: `2/2`
- test alignment: `2/2`
- tong: `6/6`
- danh gia: `Done`

Con lai:
- Moc 0 da xong.
- Buoc hop ly tiep theo la `Moc 1 - Frontend vertical slice`.

## 2026-04-09 13:30

Prompt:
- Hoan thien `Moc 1 - Frontend vertical slice`.

Thay doi:
- Tao frontend vertical slice duoi `handoff_ui/*`:
  - `index.html`
  - `styles.css`
  - `app.js`
  - `api.js`
  - `router.js`
  - `prompts.js`
  - `components.js`
- Chon huong SPA nho duoc serve truc tiep boi FastAPI thay vi tao stack frontend moi, de bam sat repo Python-first hien tai.
- Cap nhat `handoff_api/main.py` de:
  - mount asset route `/handoff/assets`
  - serve shell HTML cho cac route `/handoff/...`
- Cap nhat `tests/test_handoff_api.py` de them test:
  - UI shell route tra HTML
  - asset JS/CSS duoc serve
- Tao `AI_DOCUMENT_HANDOFF_M1_DEBUG_TEST_CHECKLIST.md` de note:
  - route cover
  - debug checklist
  - test checklist
  - diem checkpoint
- Cap nhat `AI_DOCUMENT_HANDOFF_ROADMAP.md`:
  - danh dau Moc 1 da done
  - them `Checkpoint - Moc 1`
  - doi de xuat tiep theo sang `Moc 2 - UX validation va repair`
- Cap nhat `README_handoff_api.md` de chi ro frontend vertical slice duoc mo bang route `/handoff/...`.

Verify:
- `python -m unittest tests.test_handoff_api -v` -> OK (10 test)
- `python -m unittest discover -s tests -v` -> OK (15 test)
- Chay server local:
  - `uvicorn handoff_api.main:app --port 8002`
  - verify `GET /handoff/source-packs/new` -> 200
  - verify `GET /handoff/assets/app.js` -> 200
- Runtime server dang chay tai:
  - `http://127.0.0.1:8002/handoff/source-packs/new`

Checkpoint:
- Create source pack UI: `2/2`
- Create activity UI: `2/2`
- Feedback flow UI: `2/2`
- End-to-end demo: `2/2`
- tong: `8/8`
- danh gia: `Done`

Con lai:
- Moc 1 da xong.
- Buoc hop ly tiep theo la `Moc 2 - UX validation va repair`.

## 2026-04-09 14:08

Prompt:
- Hoan thien `Moc 2 - UX validation va repair`.
- Them nut doi ngon ngu `Tiếng Việt / English` cho frontend handoff.

Thay doi:
- Cap nhat `handoff_ui/app.js` de:
  - tach trang thai `load / validate / save` cho source pack, activity, submission, feedback
  - reset validation khi payload thay doi
  - xu ly loi theo stage ro hon
  - ho tro nut doi locale bang `data-set-locale`
- Cap nhat `handoff_ui/components.js` de:
  - them `status strip`
  - them `marker guide`
  - them `issue table`
  - them `payload preview`
  - render language toggle trong shell
- Tao `handoff_ui/i18n.js` de:
  - luu locale vao `localStorage`
  - cung cap copy song ngu `Tiếng Việt / English`
  - dich UI va prompt text cho frontend handoff
- Cap nhat `handoff_ui/prompts.js` de prompt build theo locale dang chon.
- Cap nhat `handoff_ui/styles.css` de style:
  - language toggle
  - status strip
  - issue table
  - marker guide
- Cap nhat `tests/test_handoff_api.py` de smoke test:
  - asset `components.js`
  - asset `i18n.js`
  - CSS class moi cho UX M2
- Tao `AI_DOCUMENT_HANDOFF_M2_DEBUG_TEST_CHECKLIST.md`.
- Cap nhat `AI_DOCUMENT_HANDOFF_ROADMAP.md`:
  - danh dau Moc 2 da done
  - them `Checkpoint - Moc 2`
  - doi de xuat tiep theo sang `Moc 4 - Hardening va test expansion`

Verify:
- `python -m unittest tests.test_handoff_api -v` -> OK
- `python -m unittest discover -s tests -v` -> OK
- `node --check handoff_ui\\app.js` -> OK
- `node --check handoff_ui\\components.js` -> OK
- `node --check handoff_ui\\prompts.js` -> OK
- `node --check handoff_ui\\i18n.js` -> OK
- `node --check handoff_ui\\api.js` -> OK
- `node --check handoff_ui\\router.js` -> OK
- runtime smoke bang `Start-Job + uvicorn`:
  - `GET /handoff/source-packs/new` -> `200`
  - asset `i18n.js` co `Tiếng Việt` va `English`
  - asset `components.js` co `data-set-locale` va `renderStatusStrip`

Checkpoint:
- Error clarity: `2/2`
- Repair path: `2/2`
- Preview clarity: `2/2`
- tong: `6/6`
- danh gia: `Done`

Con lai:
- Moc 2 da xong.
- Buoc hop ly tiep theo la `Moc 4 - Hardening va test expansion`.
