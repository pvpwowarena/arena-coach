"""CLI: arena-ingest.

Команды:
    paste                  — импорт Markdown-документа в kb/drafts/
    glossary extract       — собрать abilities.json skeleton из исходных файлов
    list                   — что лежит в kb/drafts/ и kb/matchups/
    review approve         — переместить draft → matchups (TODO: + audit log в Phase 2)
    review reject          — пометить draft на удаление (с reason)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from arena_ingest.glossary_extract import extract_from_files, write_glossary_skeleton
from arena_ingest.sources.paste import parse_and_write_drafts


def _kb_root_default() -> Path:
    """Найти `kb/` относительно текущей рабочей директории.

    Идём вверх по дереву из CWD, ищем родителя с подпапкой `kb/`.
    """
    cur = Path.cwd().resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "kb").is_dir():
            return parent / "kb"
    # Fallback: ожидаем что cwd сам == repo-root
    return Path.cwd() / "kb"


def _cmd_paste(args: argparse.Namespace) -> int:
    source = Path(args.file).resolve()
    if not source.is_file():
        print(f"ERROR: {source} не найден", file=sys.stderr)
        return 1
    output_dir = (
        Path(args.output_dir) if args.output_dir else _kb_root_default() / "drafts"
    ).resolve()
    results = parse_and_write_drafts(
        source_file=source,
        our_composition=args.comp,
        output_dir=output_dir,
        dry_run=args.dry_run,
    )
    if not results:
        print("WARNING: парсер не нашёл ни одного матчапа в файле", file=sys.stderr)
        return 1

    print(f"{'DRY-RUN: ' if args.dry_run else ''}Сгенерировано {len(results)} draft'ов:")
    for slug, path in results:
        rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
        marker = "[would-write]" if args.dry_run else "[written]"
        print(f"  {marker} {rel}  ({slug})")
    return 0


def _cmd_glossary_extract(args: argparse.Namespace) -> int:
    files = [Path(p).resolve() for p in args.files]
    missing = [p for p in files if not p.is_file()]
    if missing:
        print(f"ERROR: файлы не найдены: {missing}", file=sys.stderr)
        return 1
    output = (
        Path(args.output) if args.output else _kb_root_default() / "glossary" / "abilities.json"
    ).resolve()
    abilities = extract_from_files(files)
    write_glossary_skeleton(abilities, output)
    print(f"Записано {len(abilities)} способностей в {output}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    kb = (Path(args.kb_root) if args.kb_root else _kb_root_default()).resolve()
    drafts = sorted((kb / "drafts").glob("*.md")) if (kb / "drafts").is_dir() else []
    final = sorted((kb / "matchups").glob("*.md")) if (kb / "matchups").is_dir() else []
    print(f"kb/drafts/  ({len(drafts)} файлов):")
    for p in drafts:
        print(f"  {p.name}")
    print(f"\nkb/matchups/  ({len(final)} файлов):")
    for p in final:
        print(f"  {p.name}")
    return 0


def _cmd_review_approve(args: argparse.Namespace) -> int:
    kb = (Path(args.kb_root) if args.kb_root else _kb_root_default()).resolve()
    draft = kb / "drafts" / f"{args.slug}.md"
    if not draft.is_file():
        print(f"ERROR: {draft} не найден", file=sys.stderr)
        return 1
    target = kb / "matchups" / draft.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(
            f"ERROR: {target} уже существует. Сначала удали или используй --force", file=sys.stderr
        )
        return 1
    shutil.move(str(draft), str(target))
    print(f"Approved: {draft.name} → kb/matchups/")
    # TODO(Phase 2): запись в audit-JSONL: {ts, actor, action: 'kb.review.approve', target: slug}
    return 0


def _cmd_review_reject(args: argparse.Namespace) -> int:
    kb = (Path(args.kb_root) if args.kb_root else _kb_root_default()).resolve()
    draft = kb / "drafts" / f"{args.slug}.md"
    if not draft.is_file():
        print(f"ERROR: {draft} не найден", file=sys.stderr)
        return 1
    rejected_dir = kb / "drafts" / ".rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    target = rejected_dir / draft.name
    shutil.move(str(draft), str(target))
    print(f"Rejected: {draft.name} → {rejected_dir.name}/  (reason: {args.reason})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="arena-ingest", description="Arena Coach ingest pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── paste ──
    p_paste = sub.add_parser("paste", help="Импорт Markdown-документа с гайдами в kb/drafts/")
    p_paste.add_argument("--file", required=True, help="Путь к исходному .md")
    p_paste.add_argument(
        "--comp",
        required=True,
        help="Slug нашего состава, например 'rogue+mage' или 'rogue+priest'",
    )
    p_paste.add_argument("--output-dir", help="Куда писать draft'ы (по умолчанию kb/drafts/)")
    p_paste.add_argument(
        "--dry-run", action="store_true", help="Не писать файлы, только показать план"
    )
    p_paste.set_defaults(func=_cmd_paste)

    # ── glossary extract ──
    p_glos = sub.add_parser("glossary", help="Операции с глоссарием")
    glos_sub = p_glos.add_subparsers(dest="glos_cmd", required=True)
    p_glos_ext = glos_sub.add_parser(
        "extract", help="Собрать abilities.json skeleton из исходных Markdown-файлов"
    )
    p_glos_ext.add_argument("files", nargs="+", help="Один или несколько .md файлов")
    p_glos_ext.add_argument(
        "--output", help="Путь к abilities.json (по умолчанию kb/glossary/abilities.json)"
    )
    p_glos_ext.set_defaults(func=_cmd_glossary_extract)

    # ── list ──
    p_list = sub.add_parser("list", help="Показать содержимое kb/drafts/ и kb/matchups/")
    p_list.add_argument("--kb-root", help="Корень kb/ (по умолчанию авто-детект)")
    p_list.set_defaults(func=_cmd_list)

    # ── review ──
    p_rev = sub.add_parser("review", help="Review draft'ов")
    rev_sub = p_rev.add_subparsers(dest="rev_cmd", required=True)
    p_rev_app = rev_sub.add_parser("approve", help="Move draft → matchups")
    p_rev_app.add_argument("--slug", required=True)
    p_rev_app.add_argument("--kb-root")
    p_rev_app.set_defaults(func=_cmd_review_approve)
    p_rev_rej = rev_sub.add_parser("reject", help="Move draft в kb/drafts/.rejected/ с reason")
    p_rev_rej.add_argument("--slug", required=True)
    p_rev_rej.add_argument("--reason", required=True)
    p_rev_rej.add_argument("--kb-root")
    p_rev_rej.set_defaults(func=_cmd_review_reject)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
