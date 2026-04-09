# Agent Change Log Rule

## Muc tieu

Sau moi prompt cua nguoi dung, Agent phai ghi lai da thay doi gi vao `.local-agent-rules/CHANGELOG.md`.

## Rule

1. Moi task xong deu phai append 1 entry moi.
2. Entry phai noi ngan gon:
   - ngu canh yeu cau
   - file nao da doi
   - doi gi o muc do cao
   - da verify gi
   - con gi chua verify hoac assumption nao can noi ro
3. Neu prompt khong dan den sua file, van phai note ro:
   - khong co thay doi file
   - Agent da tra loi/phan tich/goi y gi
4. Khong copy nguyen diff dai vao changelog.
5. Changelog chi la log van hanh local, khong thay the final response cho nguoi dung.

## Mau entry

```md
## YYYY-MM-DD HH:mm

Prompt:
- ...

Thay doi:
- ...

Verify:
- ...

Con lai:
- ...
```
