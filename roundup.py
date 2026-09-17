import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import trafilatura
from bs4 import BeautifulSoup
from markitdown import MarkItDown


# Use the folder containing this script as the working directory.
BASE_DIR = Path(__file__).resolve().parent
ROUNDUP_OUTPUT_DIR = BASE_DIR / "Daily Roundups"


def safe_filename(text: str, max_length: int = 120) -> str:
    text = re.sub(r'[<>:"/\\|?*]', "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length] or "untitled_article"


def get_roundup_label(path: Path) -> str:
    match = re.search(r"\d{4}-\d{2}-\d{2}", path.stem)

    if match:
        return match.group(0)

    return safe_filename(path.stem)


def get_auto_html_path() -> Path:
    files = sorted(
        BASE_DIR.glob("todays_roundup_*.html"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not files:
        raise FileNotFoundError(
            f"No roundup HTML files found in: {BASE_DIR}"
        )

    return files[0]


def get_input_path_from_dialog() -> Path:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Choose roundup HTML or CSV file",
        initialdir=BASE_DIR,
        filetypes=[
            ("Roundup files", "*.html *.htm *.csv"),
            ("HTML files", "*.html *.htm"),
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ],
    )

    if not file_path:
        raise FileNotFoundError("No input file selected.")

    return Path(file_path)


def clean_url(url: str) -> str:
    url = url.strip()

    # Remove trailing comma-separated timestamp or spreadsheet junk.
    url = url.split(",")[0].strip()

    # Remove common trailing punctuation.
    url = url.rstrip(").,;")

    return url


def extract_urls_from_html(path: Path) -> list[str]:
    html_content = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html_content, "html.parser")

    urls = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("http"):
            urls.append(clean_url(href))

    urls.extend(
        clean_url(u) for u in re.findall(r"https?://[^\s\"'<>]+", html_content)
    )

    return list(dict.fromkeys(urls))


def extract_urls_from_csv(path: Path) -> list[str]:
    urls = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        errors="ignore",
        newline=""
    ) as f:
        reader = csv.reader(f)

        for row in reader:
            for cell in row:
                found_urls = re.findall(
                    r'https?://[^\s,"\']+',
                    cell
                )

                for url in found_urls:
                    urls.append(clean_url(url))

    return list(dict.fromkeys(urls))


def fallback_title_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    slug = path.split("/")[-1] if path else parsed.netloc

    return slug.replace("-", " ").replace("_", " ").title()


def is_youtube_url(url: str) -> bool:
    domain = urlparse(url).netloc.lower()

    return (
        "youtube.com" in domain
        or "youtu.be" in domain
    )


def extract_with_markitdown(url: str) -> tuple[str | None, str | None]:
    try:
        cleaned_url = clean_url(url)
        md = MarkItDown()
        result = md.convert(cleaned_url)

        text = result.text_content

        # Put interviewer questions into headings.
        text = re.sub(
            r'^>>\s*(.+\?)$',
            r'### \1',
            text,
            flags=re.MULTILINE
        )

        # Remove simple repeated words.
        text = re.sub(
            r'\b(\w+)\s+\1\b',
            r'\1',
            text,
            flags=re.IGNORECASE
        )

        # Remove the top-level "# YouTube" heading.
        text = re.sub(
            r"^#\s*YouTube\s*\n+",
            "",
            text,
            count=1,
            flags=re.IGNORECASE
        )

        if not text or not text.strip():
            return None, None

        title = fallback_title_from_url(cleaned_url)

        for line in text.splitlines():
            clean = line.strip()
            if clean.startswith("## "):
                title = clean.replace("## ", "", 1).strip()
                break
            if clean.startswith("# ") and clean.casefold() != "# youtube":
                title = clean.replace("# ", "", 1).strip()
                break

        return text, title

    except Exception as e:
        print(f"  MarkItDown extraction failed: {e}")
        return None, None


def extract_with_trafilatura(url: str) -> tuple[str | None, str | None]:
    cleaned_url = clean_url(url)
    html = trafilatura.fetch_url(cleaned_url)

    if not html:
        print("  Failed to fetch")
        return None, None

    article_text = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=True,
        include_comments=False,
        include_tables=True,
        include_formatting=True,
        favor_precision=False,
    )

    if not article_text:
        print("  No article text extracted")
        return None, None

    metadata = trafilatura.extract_metadata(html)

    if metadata and metadata.title:
        article_title = metadata.title
    else:
        article_title = fallback_title_from_url(cleaned_url)

    return article_text, article_title


def article_contains_heading(article_text: str, article_title: str) -> bool:
    target = article_title.strip().casefold()

    for line in article_text.splitlines():
        line = line.strip()

        if line.startswith("#"):
            heading = line.lstrip("#").strip().casefold()

            if heading == target:
                return True

    return False


def main():
    if "--auto" in sys.argv:
        input_file = get_auto_html_path()
    else:
        input_file = get_input_path_from_dialog()

    roundup_label = get_roundup_label(input_file)

    output_dir = ROUNDUP_OUTPUT_DIR / f"EditorialRoundup_{roundup_label}"
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = input_file.suffix.lower()

    if suffix in {".html", ".htm"}:
        urls = extract_urls_from_html(input_file)
    elif suffix == ".csv":
        urls = extract_urls_from_csv(input_file)
    else:
        raise ValueError(
            f"Unsupported input file type: {input_file.suffix}"
        )

    print(f"Using input file: {input_file}")
    print(f"Roundup label: {roundup_label}")
    print(f"Found {len(urls)} URLs")
    print(f"Saving files to: {output_dir}")

    for i, url in enumerate(urls, start=1):
        url = clean_url(url)
        print(f"[{i}/{len(urls)}] Fetching {url}")

        if is_youtube_url(url):
            print("  Detected YouTube URL; using MarkItDown")
            article_text, article_title = extract_with_markitdown(url)
        else:
            article_text, article_title = extract_with_trafilatura(url)

        if not article_text:
            print("  Skipping")
            continue

        if not article_title:
            article_title = fallback_title_from_url(url)

        filename = (
            f"{i:03d}_{roundup_label}_"
            f"{safe_filename(article_title)}.md"
        )

        output_path = output_dir / filename

        if article_contains_heading(article_text, article_title):
            file_content = (
                f"**URL:** {url}\n\n"
                f"**Source:** {roundup_label}\n\n"
                f"{article_text}"
            )
        else:
            file_content = (
                f"# {article_title}\n\n"
                f"**URL:** {url}\n\n"
                f"**Source:** {roundup_label}\n\n"
                f"{article_text}"
            )

        output_path.write_text(
            file_content,
            encoding="utf-8",
        )

        print(f"  Saved: {output_path.name}")

    print("Done.")


if __name__ == "__main__":
    main()