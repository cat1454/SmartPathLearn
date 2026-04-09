# Handoff API Backend V1

Backend nay dung FastAPI de scaffold flow handoff theo spec V2:

- `source_pack`
- `activity_authoring`
- `student_submission`
- `activity_feedback`

## Cai dependency

```powershell
python -m pip install -r requirements-handoff-api.txt
```

## Chay server local

```powershell
uvicorn handoff_api.main:app --reload
```

Mac dinh storage file nam tai:

- `.handoff_api_store.json`

Huong ha tang da chot neu di Google Cloud:

- M4 hardening/test truoc
- sau do doi sang `Cloud SQL Postgres`
- deploy len `Cloud Run`
- `Cloud Storage` chi dung cho file/object, khong dung lam DB

Xem them:

- `AI_DOCUMENT_HANDOFF_GOOGLE_CLOUD_PLAN.md`

## Frontend vertical slice

Frontend M1 duoc serve cung server FastAPI, khong can them dev server rieng.

Mo:

- `http://127.0.0.1:8000/handoff/source-packs/new`
- hoac `http://127.0.0.1:8000/handoff`

## Endpoint V1

- `POST /source-packs/validate`
- `POST /source-packs`
- `GET /source-packs/{source_pack_id}`
- `POST /activities/validate`
- `POST /activities`
- `GET /activities/{activity_id}`
- `POST /activities/{activity_id}/submission`
- `POST /activities/{activity_id}/feedback/validate`
- `POST /activities/{activity_id}/feedback`

## Luu y contract

1. API parse marker nghiem:
   - `SOURCE_PACK_V1`
   - `ACTIVITY_PAYLOAD_V2`
   - `ACTIVITY_FEEDBACK_V2`
2. API reject neu co text ngoai marker.
3. `source_pack_ref` trong `SOURCE_PACK_V1` va `activity_id` trong `ACTIVITY_PAYLOAD_V2` phai ton tai trong payload; neu de rong thi backend sinh luc save.
4. `source_notes` trong `SOURCE_PACK_V1` phai la `string[]`.
5. `student_submission.response_type` chi nhan:
   - `free_text`
   - `bullet_points`
   - `short_essay`
6. `feedback` van phai khop `activity_id` va `activity_type` da luu.

## Chay test

```powershell
python -m unittest tests.test_handoff_api -v
python -m unittest discover -s tests -v
```
