# Prompt Correction Rule

## Muc tieu

Khi nguoi dung prompt mo ho, sai cau truc, hoac de bai de dan den output kem, Agent duoc phep goi y prompt viet lai cho dung hon.

Dieu nay khong co nghia la day viec nguoc lai cho nguoi dung. Mac dinh:

- neu co the tu gia dinh an toan va lam duoc, Agent van nen lam
- chi goi y viet lai khi prompt thieu phan cot loi hoac de bai co nhieu cach hieu

## Khi nao nen goi y prompt viet lai

- Khong ro muc tieu cuoi cung.
- Khong ro file/module nguon su that.
- Yeu cau vua muon hotfix nho vua muon refactor rong.
- Mo ta bug khong co behavior hien tai va behavior mong muon.
- Yeu cau review nhung thuc chat lai muon implement.

## Cach goi y dung

Agent nen tra theo 3 buoc:

1. Neu ngan gon van de cua prompt hien tai.
2. Dua 1 ban prompt viet lai co the dung ngay.
3. Neu hop ly, noi Agent se tam gia dinh huong nao de tiep tuc trong luc cho xac nhan.

## Mau phan hoi

```md
Prompt hien tai con thieu:
- ...
- ...

Ban co the prompt lai theo mau nay:

Muc tieu:
...

Nguon su that:
...

Hanh vi hien tai:
...

Hanh vi mong muon:
...

Pham vi sua:
...

Khong duoc lam:
...

Cach verify:
...
```

## Dieu can tranh

- Khong phan xet nguoi dung "prompt sai".
- Khong bat nguoi dung viet lai khi Agent tu lan duoc context.
- Khong dat qua nhieu cau hoi mo cung luc.
