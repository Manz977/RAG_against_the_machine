import logging
from pathlib import Path
import re
from typing import Optional, Tuple


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class MarkdownChunking:
    @staticmethod
    def read_markdown_file(
        filepath: str | Path,
    ) -> Tuple[Optional[str], Optional[str]]:
        try:
            path = Path(filepath)

            if not path.is_absolute():
                project_root = Path(__file__).resolve().parents[1]
                path = (project_root / path).resolve()
            else:
                path = path.resolve()

            if not path.exists():
                logger.error(f"File does not exist: {path}")
                return None, None

            if not path.is_file():
                logger.error(f"Path is not a regular file: {path}")

            if path.suffix.lower() not in (".md", ".markdown"):
                logger.warning(
                    f"File is not a Markdown file (extension '{path.suffix}')"
                )

            content = path.read_text(encoding="utf-8")
            return str(path), content

        except PermissionError:
            logger.error(f"Permission denied: {filepath}")
            return None, None
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading '{filepath}': {e}")
            return None, None
        except OSError as e:
            logger.error(f"OS error reading '{filepath}': {e}")
            return None, None


if __name__ == "__main__":
    file_path, content = MarkdownChunking.read_markdown_file(
        "data/raw/vllm-0.10.1/docs/features/lora.md"
    )

    if file_path is None or content is None:
        raise SystemExit("Could not read the Markdown file.")

    pattern = r"^(#{1,6})[ \t]*(.*?)[ \t]*\n(.*?)(?=(?:^#{1,6}[ \t])|\Z)"

    # Casting to re.RegexFlag satisfies strict type-checker requirements.
    combined_flags = re.RegexFlag(re.M | re.S)

    for match in re.finditer(pattern, content, flags=combined_flags):
        body = match.group(3).strip()
        position = match.find(content)
        print(body)
