"""CLI commands for schedule parsing and synchronization.

Usage:
    # Dry-run parsing (without saving to DB)
    uv run python -m src.cli.schedule_cli parse --verbose

    # Output as JSON
    uv run python -m src.cli.schedule_cli parse --json

    # Sync schedule to database
    uv run python -m src.cli.schedule_cli sync

    # Force sync (even if hash unchanged)
    uv run python -m src.cli.schedule_cli sync --force
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


async def cmd_parse(args: argparse.Namespace) -> int:
    """Execute parse command - dry-run parsing without DB.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from src.parser import OmsuScheduleParser

    logger = logging.getLogger(__name__)
    logger.info("Starting schedule parsing (dry-run mode)")

    url = args.url

    try:
        async with OmsuScheduleParser(url=url) as parser:
            result = await parser.parse()

            print(f"\n{'=' * 60}")
            print(
                f"Parsing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"Source: {result.source_url}")
            print(f"Entries found: {result.entries_count}")
            print(f"Content hash: {result.content_hash}")
            print(f"{'=' * 60}\n")

            if result.has_errors:
                print("Errors during parsing:")
                for err in result.errors:
                    print(f"  - {err}")
                print()

            if args.verbose:
                print("Parsed entries:\n")
                for i, entry in enumerate(result.entries, 1):
                    print(
                        f"{i}. {entry.day_of_week.name} {entry.start_time}-{entry.end_time}"
                    )
                    print(f"   Subject: {entry.subject_name}")
                    print(f"   Type: {entry.lesson_type.value}")
                    if entry.teacher_name:
                        print(f"   Teacher: {entry.teacher_name}")
                    if entry.room:
                        print(f"   Room: {entry.room}", end="")
                        if entry.building:
                            print(f" (Building {entry.building})", end="")
                        print()
                    if entry.week_type:
                        print(f"   Week: {entry.week_type.value}")
                    print()

            if args.json:
                # Remove _original from raw_data for cleaner output
                clean_raw = [
                    {k: v for k, v in entry.items() if k != "_original"}
                    for entry in result.raw_data
                ]
                output = {
                    "source_url": result.source_url,
                    "parsed_date": str(result.parsed_date),
                    "content_hash": result.content_hash,
                    "entries_count": result.entries_count,
                    "raw_data": clean_raw,
                }
                print("\nJSON output:")
                print(json.dumps(output, ensure_ascii=False, indent=2, default=str))

            return 0

    except Exception as e:
        logger.error("Parsing failed: %s", e, exc_info=args.verbose)
        return 1


async def cmd_sync(args: argparse.Namespace) -> int:
    """Execute sync command - parse and save to database.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from src.config import settings
    from src.services import schedule as schedule_service

    logger = logging.getLogger(__name__)
    logger.info("Starting schedule synchronization")

    # Create async engine and session
    engine = create_async_engine(settings.database_url, echo=args.verbose)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as db:
            result = await schedule_service.sync_schedule(
                db,
                force=args.force,
            )

            print(f"\n{'=' * 60}")
            print(
                f"Synchronization completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"Success: {result['success']}")
            print(f"Changed: {result['changed']}")
            print(f"Entries count: {result['entries_count']}")
            if result.get("content_hash"):
                print(f"Content hash: {result['content_hash']}")
            if result.get("message"):
                print(f"Message: {result['message']}")
            print(f"{'=' * 60}\n")

            return 0 if result["success"] else 1

    except Exception as e:
        logger.error("Sync failed: %s", e, exc_info=args.verbose)
        return 1
    finally:
        await engine.dispose()


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(
        description="Schedule parsing and synchronization CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse schedule without saving to database (dry-run)",
    )
    parse_parser.add_argument(
        "--url",
        help="Schedule API URL (defaults to config)",
    )
    parse_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON data",
    )

    # Sync command
    sync_parser = subparsers.add_parser(
        "sync",
        help="Parse schedule and synchronize with database",
    )
    sync_parser.add_argument(
        "--force",
        action="store_true",
        help="Force sync even if content unchanged",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.verbose)

    # Run appropriate command
    if args.command == "parse":
        return asyncio.run(cmd_parse(args))
    elif args.command == "sync":
        return asyncio.run(cmd_sync(args))

    return 1


if __name__ == "__main__":
    sys.exit(main())
