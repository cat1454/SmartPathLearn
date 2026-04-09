# Local Agent Rules

Thu muc nay chi ap dung cho Agent lam viec trong repo nay.

Muc tieu:

- giao task ro hon cho Agent
- giup Agent lam viec on dinh hon trong repo that
- uu tien sua goc van de thay vi patch trieu chung
- khi prompt cua nguoi dung mo ho hoac sai cau truc, Agent co the goi y prompt viet lai

Bo rule nay co the dua len git de chia se trong repo.

## Cac file chinh

- `01-agent-prompt.rule.md`: cach prompt Agent cho dung
- `02-agent-execution.rule.md`: cach Agent nen thuc hien task
- `03-agent-debug.rule.md`: rule debug va tim root cause
- `04-agent-refactor.rule.md`: rule cho refactor co kiem soat
- `05-agent-review.rule.md`: rule review code
- `06-agent-done-check.rule.md`: checklist truoc khi chot task
- `07-prompt-correction.rule.md`: rule de Agent goi y prompt viet lai
- `08-agent-change-log.rule.md`: rule ghi log van hanh sau moi prompt
- `CHANGELOG.md`: log local de Agent append lai thay doi da lam theo tung task

`CHANGELOG.md` duoc giu local-only bang `.git/info/exclude`, khong mac dinh dua len git.

## Nguyen tac tong

- Day la rule cho Agent, khong phai phat bieu tong quat ve moi AI.
- Neu prompt on, Agent nen lam viec ngay.
- Neu prompt thieu hoac sai cau truc, Agent nen neu van de ngan gon va de xuat prompt viet lai tot hon.
- Neu co the gia dinh an toan va van lam duoc, Agent co the vua de xuat prompt tot hon vua tiep tuc lam.
- Sau moi prompt, Agent phai cap nhat `.local-agent-rules/CHANGELOG.md` de note lai da thay doi gi. Neu khong sua file thi cung phai note ro la khong co thay doi file.
