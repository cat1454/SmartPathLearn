# Agent Execution Rule

## Cach Agent nen lam viec

1. Doc file lien quan truoc khi sua.
2. Xac dinh root cause truoc khi patch.
3. Chon pham vi sua nho nhat co the, nhung van chua dung goc van de.
4. Ton trong worktree dang ban.
5. Verify truoc khi ket thuc neu moi truong cho phep.

## Thu tu mac dinh

1. Hieu de bai.
2. Tim file va flow lien quan.
3. Neu ngan gon van de nam o dau.
4. Sua code.
5. Verify.
6. Append log vao `.local-agent-rules/CHANGELOG.md`.
7. Tom tat root cause, thay doi, va phan chua verify.

## Dieu Agent khong nen lam

- Khong patch theo cam tinh.
- Khong chen them nhieu `if` neu chua ro goc loi.
- Khong rewrite lon chi de "dep".
- Khong keo nguoi dung vao mot loat cau hoi mo neu van con co the tu lan context.

## Khi nao Agent nen dung lai va canh bao

- Can sua qua nhieu file so voi de bai.
- Co xung dot voi thay doi dang mo.
- Co 2 huong sua voi trade-off lon.
- Khong the verify nhung thay doi lai nhay cam.
