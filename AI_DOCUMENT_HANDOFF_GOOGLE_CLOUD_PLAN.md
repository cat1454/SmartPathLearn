# AI Document Handoff Google Cloud Plan

## Summary

Huong chot neu di Google Cloud:

1. Lam `Moc 4 - Hardening va test expansion` truoc.
2. Doi `Moc 3` thanh `cloud persistence`:
   - bo JSON store
   - chuyen sang `Cloud SQL Postgres`
3. Sau do moi lam `Moc 5 - Deploy len Cloud Run`.
4. `Cloud Storage` chi dung cho file/object, khong dung lam database.

Tai lieu nay chot ro:

- dich den ha tang
- vai tro cua tung dich vu Google Cloud
- pham vi code can sua
- checklist verify va checkpoint sau moi moc

## Kien truc muc tieu

### Runtime

- `Cloud Run`
  - chay `FastAPI` backend
  - serve frontend shell `handoff_ui/*`
  - scale theo request

### Database

- `Cloud SQL for PostgreSQL`
  - la he thong record chinh
  - luu `source_packs`, `activities`, `submissions`, `feedbacks`
  - thay the `.handoff_api_store.json`

### File/Object storage

- `Cloud Storage`
  - luu file PDF/doc goc neu co upload
  - luu export artifact neu can
  - luu import bundle hay backup object-level neu can
  - khong dung de query domain object chinh
  - khong dung thay DB

## Nguyen tac ha tang

1. Route public va payload contract giu nguyen.
2. Chuyen storage bang abstraction, khong de route biet storage cu the.
3. Cloud Storage la noi giu file, Cloud SQL la noi giu state/domain record.
4. M4 phai xong truoc khi doi persistence de tranh vua doi DB vua sua contract.
5. Deployment len Cloud Run chi bat dau khi local Postgres flow da xanh.

## Mapping tu storage hien tai sang Postgres

Storage hien tai:

- `JsonStore` trong `handoff_api/storage.py`

Huong doi:

1. Tao `StorageBackend` interface cho:
   - `has_source_pack`
   - `get_source_pack`
   - `create_source_pack`
   - `has_activity`
   - `get_activity`
   - `create_activity`
   - `get_submission`
   - `upsert_submission`
   - `get_feedback`
   - `upsert_feedback`
2. Giu `JsonStore` lam local/demo backend tam thoi
3. Them `PostgresStore`
4. Chon backend bang env var:
   - `HANDOFF_STORAGE_BACKEND=json|postgres`

## Bang du lieu de xuat

### `source_packs`

- `id` text primary key
- `created_at` timestamptz
- `updated_at` timestamptz
- `payload` jsonb not null

### `activities`

- `id` text primary key
- `source_pack_id` text not null references `source_packs(id)`
- `created_at` timestamptz
- `updated_at` timestamptz
- `payload` jsonb not null

### `submissions`

- `activity_id` text primary key references `activities(id)`
- `created_at` timestamptz
- `updated_at` timestamptz
- `submission` jsonb not null

### `feedbacks`

- `id` text primary key
- `activity_id` text unique not null references `activities(id)`
- `created_at` timestamptz
- `updated_at` timestamptz
- `payload` jsonb not null

## Cloud Storage dung cho gi

Dung cho:

1. file PDF/doc goc ma user upload
2. export JSON/CSV de tai xuong
3. artifact tam do AI tao ra neu can luu lai
4. archive import/export bundle

Khong dung cho:

1. query `source_pack` theo id
2. query `activity` theo id
3. save `submission`/`feedback` dang record nghiep vu
4. thay the transaction/update logic cua DB

## Thu tu thuc hien

### Phase A - Moc 4 truoc

Muc tieu:

- khoa contract
- day test matrix
- giam regression truoc khi doi persistence

Acceptance:

- 5 `activity_type` co duong validate/create/save/load xanh
- reject case Wave 1 co test rieng
- UI smoke van xanh

### Phase B - Moc 3 Cloud SQL Postgres

Muc tieu:

- thay JSON store bang Postgres backend
- giu nguyen API shape

Viec can lam:

1. tach storage interface
2. them `PostgresStore`
3. them bootstrap schema SQL
4. them config env runtime
5. cap nhat test cho backend `postgres`
6. giu `JsonStore` cho local fallback neu can trong giai doan chuyen doi

Acceptance:

- app chay local voi Postgres
- full flow luu/doc du lieu duoc
- restart app khong mat du lieu
- response shape route cu khong doi

### Phase C - Moc 5 Cloud Run deploy

Muc tieu:

- dua app len Google Cloud o muc dung duoc

Viec can lam:

1. them `Dockerfile`
2. chot startup command cho Cloud Run
3. noi Cloud SQL vao app
4. noi Cloud Storage bucket neu co file flow
5. them env deployment:
   - `HANDOFF_STORAGE_BACKEND=postgres`
   - `HANDOFF_DATABASE_URL`
   - `GCS_BUCKET_NAME` neu can
6. deploy va verify bang route that

Acceptance:

- `/health` xanh tren Cloud Run
- tao duoc `source_pack`
- tao duoc `activity`
- save duoc `submission`
- save duoc `feedback`

## Bien moi truong de xuat

- `HANDOFF_STORAGE_BACKEND`
- `HANDOFF_DATABASE_URL`
- `HANDOFF_JSON_STORE_PATH` cho local fallback
- `GCS_BUCKET_NAME`
- `PORT`

## File du kien se doi khi vao M3

- `handoff_api/storage.py`
- `handoff_api/main.py`
- `handoff_api/validation.py` chi neu can wiring nho, khong doi contract
- `tests/test_handoff_api.py`
- `requirements-handoff-api.txt`
- `README_handoff_api.md`

## File du kien se doi khi vao M5

- `Dockerfile`
- `.dockerignore`
- `README_handoff_api.md`
- script deploy/ghi chu deploy neu can

## Checkpoint rubric

### Checkpoint cho M4

- Validator coverage: `0/1/2`
- Route coverage: `0/1/2`
- Regression confidence: `0/1/2`
- Tong: `0-6`

### Checkpoint cho M3

- Storage abstraction: `0/1/2`
- Postgres persistence: `0/1/2`
- Contract stability: `0/1/2`
- Tong: `0-6`

### Checkpoint cho M5

- Build/deploy: `0/1/2`
- DB connectivity: `0/1/2`
- Runtime verification: `0/1/2`
- Tong: `0-6`

## Quy tac quyet dinh

Neu co mau thuan giua cloud convenience va contract da chot, uu tien:

1. giu contract route/payload
2. giu test xanh
3. sau do moi toi uu deployment

## Next step ngay luc nay

Buoc tiep theo nen lam ngay van la:

### `Moc 4 - Hardening va test expansion`

Chi khi M4 dat xong moi doi storage sang Cloud SQL Postgres.
