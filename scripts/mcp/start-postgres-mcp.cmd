@echo off
REM Wrapper script for PostgreSQL MCP server
REM Reads connection string from STUDYHELPER_DB_URL environment variable

if "%STUDYHELPER_DB_URL%"=="" (
    echo ERROR: STUDYHELPER_DB_URL environment variable is not set
    echo Set it with: set STUDYHELPER_DB_URL=postgresql://user:pass@host:port/db
    exit /b 1
)

npx -y @modelcontextprotocol/server-postgres "%STUDYHELPER_DB_URL%"
