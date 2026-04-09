# AI Document Handoff Workflow

> Legacy note:
> File nay la quiz-only spec cho `QUIZ_PAYLOAD_V1`.
> Kien truc tong quat `source_pack + activity payload + feedback payload` duoc mo rong o `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`.

## Muc tieu da chot

Huong nay co 1 nguyen tac trung tam:

- **Khong de web tu sinh noi dung**
- **Web chi dong vai tro bo dieu phoi + noi nhan payload da chuan hoa**
- **Phan nang de GPT / Gemini / Claude lam**

Noi cach khac:

1. nguoi dung do tai lieu vao AI ben ngoai
2. AI tra ve dung 1 format co cau truc
3. nguoi dung dan nguoc payload do vao he thong cua ban
4. he thong parse, validate, luu

## Rules bat buoc

1. He thong cua ban chi nhan **payload co format chuan**, khong nhan prose tu do.
2. AI phai tra ve **duy nhat 1 block copy-paste** giua marker start/end.
3. Khong cho phep AI them fact ngoai tai lieu.
4. Moi `quiz_item` phai co `evidence`.
5. Moi lan xu ly chi nen gom:
   - 1 tai lieu, hoac
   - 1 chunk lon da duoc danh so section ro rang
6. Neu sai format, he thong khong "doan". He thong:
   - reject
   - bao loi
   - dua prompt sua format
7. Frontend/UX phai noi ro:
   - `Step 1`: copy prompt
   - `Step 2`: dan tai lieu vao GPT/Gemini/Claude
   - `Step 3`: copy block output
   - `Step 4`: dan vao he thong

## Luong xu ly de xai on dinh

### Luong chinh

1. Nguoi dung chon tai lieu hoac section can xu ly.
2. He thong hien prompt mau.
3. Nguoi dung dem prompt + noi dung tai lieu sang GPT/Gemini/Claude.
4. AI tra ve payload theo dung marker.
5. Nguoi dung dan nguoc payload vao he thong.
6. He thong:
   - tim marker
   - cat block JSON
   - parse
   - validate schema
   - luu vao DB / file / queue
7. Neu pass validate:
   - hien preview
   - cho phep import / publish
8. Neu fail validate:
   - hien loi field nao sai
   - dua prompt repair

### Luong khi tai lieu qua dai

Neu tai lieu dai, chia theo:

- chapter
- section
- part

Mau id:

- `s01`
- `s02`
- `s03`

Sau do merge payload theo:

- `document_title`
- `section_id`
- `quiz_items`

## Format copy-paste chuan

He thong chi nen tim va parse dung block duoi day:

```text
<<<QUIZ_PAYLOAD_V1_START>>>
{
  "document_title": "...",
  "source_language": "vi",
  "summary": "...",
  "sections": [
    {
      "section_id": "s01",
      "title": "...",
      "summary": "...",
      "key_points": ["...", "..."],
      "quiz_items": [
        {
          "id": "s01_q01",
          "type": "single_choice",
          "question_family": "anchor",
          "cognitive_level": "remember",
          "question": "...?",
          "options": ["...", "...", "...", "..."],
          "answer": "B",
          "answer_text": "...",
          "why_correct": "...",
          "why_wrong": ["...", "...", "..."],
          "evidence": ["..."]
        }
      ]
    }
  ]
}
<<<QUIZ_PAYLOAD_V1_END>>>
```

## Rule schema toi thieu

### Root

- `document_title`: string
- `source_language`: string
- `summary`: string
- `sections`: array

### Section

- `section_id`: string
- `title`: string
- `summary`: string
- `key_points`: array string
- `quiz_items`: array

### Quiz item

- `id`: string
- `type`: chi nhan `single_choice`
- `question_family`: `anchor | mechanism | contrast | application`
- `cognitive_level`: `remember | understand | apply`
- `question`: string
- `options`: dung 4 phan tu
- `answer`: `A | B | C | D`
- `answer_text`: phai khop 1 option
- `why_correct`: string
- `why_wrong`: dung 3 phan tu
- `evidence`: it nhat 1 phan tu

## Prompt mau de dua cho GPT / Gemini / Claude

### Prompt chinh

```text
Ban la bo chuyen doi tai lieu thanh payload quiz co cau truc.

NHIEM VU:
- Doc noi dung tai lieu ben duoi.
- Rut ra section, y chinh, va quiz item.
- Khong them thong tin ngoai tai lieu.
- Neu mot y khong du bang chung, bo qua.
- Chi tra ve duy nhat block giua marker:
  <<<QUIZ_PAYLOAD_V1_START>>>
  ...
  <<<QUIZ_PAYLOAD_V1_END>>>
- Khong giai thich them.
- Khong viet markdown ngoai block.

RULE OUTPUT:
- JSON hop le.
- Moi section co section_id dang s01, s02, s03...
- Moi quiz_item co id dang s01_q01, s01_q02...
- options phai dung 4 lua chon.
- answer_text phai bang dung option dung.
- why_wrong phai co 3 dong, moi dong ung voi 1 distractor.
- evidence phai trich tu tai lieu.

TAI LIEU:
{{DOCUMENT_TEXT}}
```

### Prompt repair khi AI tra sai format

```text
Ban vua tra sai format.

Hay sua lai payload theo DUNG cac rule sau:
- Chi tra ve 1 block duy nhat giua:
  <<<QUIZ_PAYLOAD_V1_START>>>
  ...
  <<<QUIZ_PAYLOAD_V1_END>>>
- JSON hop le.
- Khong them giai thich.
- Giu nguyen noi dung neu hop le, chi sua format/schema.

Payload cu:
{{BROKEN_OUTPUT}}
```

## Rule validate trong he thong cua ban

Backend / parser cua ban nen check it nhat:

1. Co marker start/end.
2. Parse duoc JSON.
3. Co day du field root.
4. Moi section co `section_id`.
5. Moi `quiz_item`:
   - du 4 options
   - `answer` hop le
   - `answer_text` nam trong options
   - `why_wrong` co 3 dong
   - `evidence` khong rong
6. Neu fail:
   - tra message ro field nao sai
   - khong import nua chung

## Quy uoc van hanh de giam phu thuoc ky thuat

1. Web khong can "thong minh".
2. Web can "nghiem format".
3. Tat ca su thong minh day sang AI ngoai.
4. Tat ca su on dinh keo ve parser + schema + validator.
5. Neu can doi provider:
   - GPT
   - Gemini
   - Claude
   thi van giu nguyen format V1.

## Checklist de review dung huong

Neu lam dung huong da chot, thi he thong cua ban phai dung voi 4 cau sau:

- Web co tu sinh noi dung khong? -> **Khong**
- Web co parse payload chuan khong? -> **Co**
- Prompt co ep AI tra ve dung marker/schema khong? -> **Co**
- Neu doi GPT sang Gemini/Claude co phai doi schema ingest khong? -> **Khong**
