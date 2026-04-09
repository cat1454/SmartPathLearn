# Agent Refactor Rule

## Khi nao duoc refactor

Duoc refactor khi:

- bug nam o contract hoac flow goc
- logic lap lai tu 2 noi tro len
- ten goi lam hieu sai domain
- mot ham dang om qua nhieu trach nhiem

Khong nen refactor khi:

- user chi can hotfix nho
- chua du context
- khong co cach verify
- refactor chi de tang do "dep" be ngoai

## Rule refactor

1. Don flow du lieu truoc khi them abstraction.
2. Dua logic ve noi gan nguon su that.
3. Dat ten theo domain.
4. Giu behavior ben ngoai neu chua duoc phep doi.
5. Moi refactor phai co ly do chuc nang ro rang.
