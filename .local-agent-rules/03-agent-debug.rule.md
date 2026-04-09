# Agent Debug Rule

## Muc tieu

Agent phai debug theo root cause, khong fix theo dau vet be mat.

## Checklist

1. Tai hien loi neu co the.
2. Xac dinh input va flow gay loi.
3. Tim lop co trach nhiem dung:
   UI, service, API, repository, transform, model, contract.
4. Neu root cause bang 1 cau ngan.
5. Sua tai diem gan nguon loi nhat co the.
6. Verify lai happy path va edge lien quan.

## Dau hieu Agent dang fix sai huong

- Them guard lap lai o nhieu lop.
- Sua UI de che loi contract backend.
- Map/parse cung mot kieu du lieu o nhieu noi.
- Fix duoc case hien tai nhung mo ra regression moi.
