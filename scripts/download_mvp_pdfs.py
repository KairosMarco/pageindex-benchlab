from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_MANIFEST = ROOT / "reports" / "mvp_pdf_manifest.json"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, output: Path, *, retries: int = 3) -> None:
    request = Request(url, headers={"User-Agent": "pageindex-benchlab"})
    part = output.with_suffix(output.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=180) as response, part.open("wb") as f:
                while True:
                    chunk = response.read(1024 * 512)
                    if not chunk:
                        break
                    f.write(chunk)
            part.replace(output)
            return
        except (TimeoutError, URLError, OSError) as exc:
            last_error = exc
            if part.exists():
                part.unlink()
            print(f"retry {attempt}/{retries}: {url} ({exc})")
    raise RuntimeError(f"Failed to download {url}") from last_error


def main() -> None:
    parser = argparse.ArgumentParser(description="Download PDFs for FinanceBench MVP questions.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--force", action="store_true", help="Re-download existing PDFs.")
    args = parser.parse_args()

    questions = load_jsonl(args.questions)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    docs: dict[str, dict] = {}
    for question in questions:
        docs[question["doc_name"]] = {
            "doc_name": question["doc_name"],
            "company": question["company"],
            "pdf_url": question["pdf_url"],
        }

    manifest = []
    for doc_name, doc in sorted(docs.items()):
        output = args.output_dir / f"{doc_name}.pdf"
        status = "exists"
        if args.force or not output.exists():
            status = "downloaded"
            download(doc["pdf_url"], output)

        manifest.append(
            {
                **doc,
                "local_path": str(output.relative_to(ROOT)),
                "size_bytes": output.stat().st_size,
                "sha256": sha256_file(output),
                "status": status,
            }
        )
        print(f"{status}: {output}")

    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote manifest: {args.manifest}")


if __name__ == "__main__":
    main()
