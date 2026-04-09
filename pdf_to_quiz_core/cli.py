from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path
from typing import Optional, Sequence

from .extraction import resolve_output_path
from .generation import generate_quiz_artifacts, sort_learning_path_questions
from .output import save_csv, save_json


def console_print(message: str, *, stream: Optional[object] = None) -> None:
    target = sys.stdout if stream is None else stream
    try:
        print(message, file=target)
    except UnicodeEncodeError:
        encoding = getattr(target, "encoding", None) or "utf-8"
        transliterated = message.replace("Đ", "D").replace("đ", "d")
        ascii_fallback = unicodedata.normalize("NFKD", transliterated).encode("ascii", errors="ignore").decode("ascii")
        safe_message = ascii_fallback or message
        payload = f"{safe_message}\n".encode(encoding, errors="replace")
        buffer = getattr(target, "buffer", None)
        if buffer is not None:
            buffer.write(payload)
            buffer.flush()
            return
        target.write(payload.decode(encoding, errors="replace"))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Đọc PDF và sinh câu hỏi trắc nghiệm bám sát evidence của tài liệu."
    )
    parser.add_argument("input_path", type=Path, help="Đường dẫn tới 1 file PDF hoặc 1 thư mục chứa nhiều PDF.")
    parser.add_argument("--output", type=Path, required=True, help="File đầu ra .json hoặc .csv")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Định dạng đầu ra. Mặc định: json")
    parser.add_argument("--mode", choices=["bank", "learning_path"], default="bank", help="Kiểu tổ chức output. Mặc định: bank")
    parser.add_argument("--llm-model", default=None, help="Model OpenAI tùy chọn để viết lại + chấm lọc câu hỏi.")
    parser.add_argument("--max-questions", type=int, default=120, help="Số lượng câu tối đa muốn sinh. Mặc định: 120")
    parser.add_argument("--seed", type=int, default=42, help="Seed để random ổn định. Mặc định: 42")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    output_path = resolve_output_path(args.output)
    try:
        questions, concept_packs = generate_quiz_artifacts(
            input_path=args.input_path,
            max_questions=args.max_questions,
            seed=args.seed,
            mode=args.mode,
            llm_model=args.llm_model,
        )
    except Exception as exc:
        console_print(f"[ERROR] {exc}", stream=sys.stderr)
        return 1
    if not questions:
        console_print(
            "[ERROR] Không sinh được câu hỏi nào. Tài liệu có thể quá nhiễu hoặc cần chỉnh heuristics.",
            stream=sys.stderr,
        )
        return 2
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        save_json(questions, output_path, args.mode, concept_packs)
    else:
        save_csv(sort_learning_path_questions(questions) if args.mode == "learning_path" else questions, output_path)
    console_print(f"Đã sinh {len(questions)} câu hỏi -> {output_path}")
    return 0
