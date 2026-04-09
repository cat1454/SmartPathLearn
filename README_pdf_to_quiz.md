# PDF to Quiz - hướng dẫn nhanh

Script này đọc 1 file PDF hoặc cả thư mục PDF, sau đó sinh quiz theo 2 kiểu:

- `bank`: ngân hàng câu hỏi phẳng để luyện nhanh
- `learning_path`: lộ trình theo section/concept để học sâu hơn

Lưu ý:

- Nếu chạy trên Windows/PowerShell, bạn có thể dùng cả `/mnt/data/...` lẫn `.\mnt\data\...`.
- Script sẽ tự map `/mnt/data/...` về thư mục `mnt/data` nằm cạnh file `pdf_to_quiz.py`.

## 1. Cài thư viện

```bash
pip install pdfplumber pypdf
```

Nếu muốn dùng lớp `hybrid LLM` để viết lại + chấm lọc câu hỏi:

```bash
pip install openai
```

và thiết lập `OPENAI_API_KEY`.

## 2. Chạy với cả thư mục PDF

```bash
python pdf_to_quiz.py /mnt/data --output /mnt/data/quiz_bank.json --format json --max-questions 180
```

PowerShell:

```powershell
python pdf_to_quiz.py .\mnt\data --output .\mnt\data\quiz_bank.json --format json --max-questions 180
```

## 3. Chạy với 1 file PDF

```bash
python pdf_to_quiz.py /mnt/data/3.PhuongPhap_Agile.pdf --output /mnt/data/agile_quiz.csv --format csv --max-questions 40
```

PowerShell:

```powershell
python pdf_to_quiz.py .\mnt\data\3.PhuongPhap_Agile.pdf --output .\mnt\data\agile_quiz.csv --format csv --max-questions 40
```

## 4. Chạy theo learning path

```powershell
python pdf_to_quiz.py .\mnt\data\3.PhuongPhap_Agile.pdf --output .\mnt\data\agile_learning_path.json --format json --mode learning_path --max-questions 40
```

## 5. Bật hybrid LLM

```powershell
python pdf_to_quiz.py .\mnt\data\3.PhuongPhap_Agile.pdf --output .\mnt\data\agile_hybrid.csv --format csv --mode learning_path --llm-model gpt-4.1-mini --max-questions 40
```

## 6. Cấu trúc output

Mỗi câu hỏi có dạng:

```json
{
  "id": "Q0001",
  "type": "single_choice",
  "difficulty": "medium",
  "concept_id": "3-phuongphap-agile__s02__product-backlog",
  "section_order": 2,
  "question_family": "anchor",
  "cognitive_level": "remember",
  "question": "Khái niệm nào khớp nhất với mô tả sau: ...?",
  "options": ["...", "...", "...", "..."],
  "answer": "B",
  "answer_text": "...",
  "explanation": "...",
  "why_correct": "...",
  "why_wrong": ["...", "...", "..."],
  "evidence": ["..."],
  "source_file": "3.PhuongPhap_Agile.pdf",
  "source_section": "Khái niệm",
  "source_excerpt": "...",
  "section_summary": "...",
  "quality": "offline_curated"
}
```

`learning_path` ở dạng JSON sẽ group theo:

- `source_file`
- `section`
- `questions`

## 7. Script đang sinh những loại câu nào?

- `anchor`: khóa ý chính / định nghĩa
- `mechanism`: vai trò, tác dụng, cách vận hành
- `contrast`: phân biệt khái niệm gần nhau
- `application`: nhận diện khái niệm qua tình huống ngắn

## 8. Cấu trúc code

Code đã được tách ra:

- `pdf_to_quiz.py`: entrypoint mỏng
- `pdf_to_quiz_core/schema.py`: dataclass + hằng số
- `pdf_to_quiz_core/extraction.py`: đọc PDF, clean text, evidence, concept pack
- `pdf_to_quiz_core/generation.py`: sinh câu hỏi offline / hybrid LLM
- `pdf_to_quiz_core/output.py`: xuất JSON/CSV
- `pdf_to_quiz_core/cli.py`: parse arg + orchestration

## 9. Giới hạn hiện tại

Đây vẫn là bản heuristic-first, nên các chỗ sau có thể cần review tay:

- tình huống dài
- so sánh sâu
- distractor rất tinh vi
- suy luận nhiều bước

## 10. Cách nâng chất lượng

Hướng nâng cấp tốt nhất:

1. Chạy offline để lấy `bank` hoặc `learning_path`.
2. Review nhanh những section nhiều OCR/noise.
3. Bật `--llm-model` để tăng chất lượng phrasing, distractor và explanation.

## 11. Gợi ý workflow thực chiến

- `step 1`: chạy `learning_path` cho 1 file
- `step 2`: review nhanh các concept bị OCR xấu
- `step 3`: nếu ổn, chạy cả thư mục ở mode `bank`
- `step 4`: bật `--llm-model` cho các file quan trọng
- `step 5`: xuất CSV để import vào web/app
