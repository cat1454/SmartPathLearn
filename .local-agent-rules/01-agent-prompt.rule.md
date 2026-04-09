# Agent Prompt Rule

## Muc tieu

Prompt tot giup Agent giam doan, giam patch sai huong, va tang kha nang sua dung goc van de.

## 7 o nen co trong prompt

1. `Muc tieu`
   Can sua gi, can tao gi, can review gi.
2. `Nguon su that`
   File, module, endpoint, component, hay service nao la dung.
3. `Hanh vi hien tai`
   Bug hien ra sao, dau vao nao gay ra.
4. `Hanh vi mong muon`
   Sau khi lam xong thi phai nhu the nao.
5. `Pham vi sua`
   Duoc sua file nao, co duoc refactor hay khong.
6. `Khong duoc lam`
   Vi du: khong doi API, khong them dependency, khong dong vao UI.
7. `Cach verify`
   Build/test/lint/step tay nao can pass.

## Mau prompt

```md
Muc tieu:

Nguon su that:

Hanh vi hien tai:

Hanh vi mong muon:

Pham vi sua:

Khong duoc lam:

Cach verify:
```

## Dinh huong cho Agent

- Neu prompt da ro, Agent khong can bat nguoi dung viet lai.
- Neu prompt thieu 1-2 o nhung van co the gia dinh an toan, Agent nen neu gia dinh va lam tiep.
- Neu prompt thieu phan cot loi, Agent nen goi y prompt viet lai theo `07-prompt-correction.rule.md`.
