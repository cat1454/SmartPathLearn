# Moc 1 Debug And Test Checklist

## Muc tieu

File nay ghi lai frontend vertical slice da duoc chot nhu the nao, da cover route nao, debug gi, test gi, va checkpoint cuoi cung.

## Frontend shell da chon

Khong tao stack frontend moi. M1 chon huong:

- SPA nho bang HTML + CSS + ES modules
- duoc serve truc tiep boi FastAPI app hien tai
- route UI nam duoi `/handoff/...`

Ly do:

1. Repo hien tai la Python-first
2. Da co FastAPI backend chay san
3. Giam do phuc tap va dependency cho vertical slice dau tien
4. Van du route that, asset that, va API integration that

## Route da cover trong M1

- `/handoff`
- `/handoff/source-packs/new`
- `/handoff/source-packs/:sourcePackId`
- `/handoff/activities/new?sourcePackId=:id`
- `/handoff/activities/:activityId`
- `/handoff/activities/:activityId/submission`
- `/handoff/activities/:activityId/feedback`

## Vertical slice da cover

1. Tao source pack
2. Validate source pack
3. Luu source pack
4. Tao activity
5. Validate activity
6. Luu activity
7. Nhap submission
8. Luu submission
9. Tao feedback prompt tu activity + submission
10. Validate feedback payload
11. Luu feedback payload
12. Reload detail page thay submission + feedback

## File da them/sua

### UI

- `handoff_ui/index.html`
- `handoff_ui/styles.css`
- `handoff_ui/app.js`
- `handoff_ui/api.js`
- `handoff_ui/router.js`
- `handoff_ui/prompts.js`
- `handoff_ui/components.js`

### Backend wiring

- `handoff_api/main.py`

### Test

- `tests/test_handoff_api.py`

### Docs / checkpoint

- `README_handoff_api.md`
- `AI_DOCUMENT_HANDOFF_ROADMAP.md`
- `.local-agent-rules/CHANGELOG.md`

## Debug checklist

### A. Route wiring

- [x] UI asset path `/handoff/assets/*` serve duoc
- [x] Tat ca route UI tra HTML shell
- [x] Deep link vao route chi tiet van load duoc SPA

### B. API integration

- [x] Source pack page goi `/source-packs/validate`
- [x] Source pack page goi `/source-packs`
- [x] Activity page goi `/activities/validate`
- [x] Activity page goi `/activities`
- [x] Submission page goi `/activities/:id/submission`
- [x] Feedback page goi `/activities/:id/feedback/validate`
- [x] Feedback page goi `/activities/:id/feedback`

### C. UI behavior

- [x] Co step rail
- [x] Co prompt copy button
- [x] Co validation panel
- [x] Co preview source pack
- [x] Co preview activity
- [x] Co preview submission
- [x] Co preview feedback
- [x] Co repair prompt khi payload invalid

## Test checklist

### Da co test tu dong

- [x] handoff UI route tra HTML shell
- [x] handoff asset JS/CSS duoc serve
- [x] full backend flow van xanh
- [x] contract test Moc 0 van xanh

### Lenh verify

```powershell
python -m unittest tests.test_handoff_api -v
python -m unittest discover -s tests -v
```

### Verify runtime local

1. Chay:

```powershell
uvicorn handoff_api.main:app --reload --port 8002
```

2. Mo:

- `http://127.0.0.1:8002/handoff/source-packs/new`

3. Di thu flow:

- paste source pack
- save
- tao activity
- save
- nhap submission
- save
- paste feedback
- save

## Ket qua sau Moc 1

- Create source pack UI: `2/2`
- Create activity UI: `2/2`
- Feedback flow UI: `2/2`
- End-to-end demo: `2/2`
- Tong: `8/8`

Danh gia:

- `Done`

Buoc tiep theo:

- `Moc 2 - UX validation va repair`
