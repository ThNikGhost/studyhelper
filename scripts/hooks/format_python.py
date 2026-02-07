"""Post-tool hook: auto-format Python files after Write/Edit.

Reads CLAUDE_TOOL_USE_RESULT from environment to determine which file
was modified. If it's a .py file, runs ruff format + ruff check --fix.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run ruff format and check on modified Python files."""
    tool_result = os.environ.get('CLAUDE_TOOL_USE_RESULT', '')
    if not tool_result:
        return 0

    # Parse the tool result to find the file path
    file_path = _extract_file_path(tool_result)
    if not file_path or not file_path.endswith('.py'):
        return 0

    if not os.path.isfile(file_path):
        return 0

    backend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'backend',
    )

    # Only format files inside the backend directory
    abs_file = os.path.abspath(file_path)
    if not abs_file.startswith(os.path.abspath(backend_dir)):
        return 0

    # Run ruff format
    try:
        subprocess.run(
            ['uv', 'run', 'ruff', 'format', abs_file],
            cwd=backend_dir,
            capture_output=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Run ruff check --fix
    try:
        subprocess.run(
            ['uv', 'run', 'ruff', 'check', '--fix', abs_file],
            cwd=backend_dir,
            capture_output=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return 0


def _extract_file_path(tool_result: str) -> str | None:
    """Extract file path from tool use result."""
    try:
        data = json.loads(tool_result)
        # Write tool result format
        if isinstance(data, dict):
            return data.get('filePath') or data.get('file_path') or data.get('path')
    except (json.JSONDecodeError, TypeError):
        pass

    # Try to find a path in plain text
    for line in tool_result.splitlines():
        stripped = line.strip()
        if stripped.endswith('.py') and (os.sep in stripped or '/' in stripped):
            return stripped

    return None


if __name__ == '__main__':
    sys.exit(main())
