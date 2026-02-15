"""Tests for LK (личный кабинет) module."""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lk import SemesterDiscipline, SessionGrade
from src.models.semester import Semester
from src.parser.lk_parser import LkStudentData
from src.services.lk import import_to_app
from src.utils.crypto import decrypt_credential, encrypt_credential

# ============================================================================
# Crypto tests
# ============================================================================


class TestCrypto:
    """Tests for crypto utilities."""

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Test encryption and decryption work correctly."""
        original = "my_secret_password123"
        encrypted = encrypt_credential(original)

        assert encrypted != original
        assert len(encrypted) > len(original)

        decrypted = decrypt_credential(encrypted)
        assert decrypted == original

    def test_encrypt_different_inputs_different_outputs(self) -> None:
        """Test that different inputs produce different ciphertexts."""
        enc1 = encrypt_credential("password1")
        enc2 = encrypt_credential("password2")

        assert enc1 != enc2

    def test_encrypt_same_input_different_outputs(self) -> None:
        """Test that same input produces different ciphertexts (due to IV)."""
        enc1 = encrypt_credential("same_password")
        enc2 = encrypt_credential("same_password")

        # Fernet uses random IV, so same plaintext -> different ciphertext
        assert enc1 != enc2

        # But both decrypt to same value
        assert decrypt_credential(enc1) == decrypt_credential(enc2)

    def test_encrypt_unicode(self) -> None:
        """Test encryption works with Unicode characters."""
        original = "пароль_с_юникодом_😀"
        encrypted = encrypt_credential(original)
        decrypted = decrypt_credential(encrypted)

        assert decrypted == original

    def test_decrypt_invalid_token(self) -> None:
        """Test decryption fails with invalid token."""
        from src.utils.crypto import CryptoError

        with pytest.raises(CryptoError):
            decrypt_credential("invalid_token")

    def test_decrypt_corrupted_token(self) -> None:
        """Test decryption fails with corrupted token."""
        from src.utils.crypto import CryptoError

        encrypted = encrypt_credential("test")
        # Corrupt the token
        corrupted = encrypted[:-5] + "XXXXX"

        with pytest.raises(CryptoError):
            decrypt_credential(corrupted)


# ============================================================================
# LK Status tests
# ============================================================================


class TestLkStatus:
    """Tests for GET /api/v1/lk/status."""

    @pytest.mark.asyncio
    async def test_status_no_credentials(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test status when no credentials saved."""
        response = await client.get("/api/v1/lk/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["has_credentials"] is False
        assert data["last_sync_at"] is None

    @pytest.mark.asyncio
    async def test_status_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.get("/api/v1/lk/status")
        assert response.status_code == 401


# ============================================================================
# LK Credentials tests
# ============================================================================


class TestLkCredentials:
    """Tests for POST/DELETE /api/v1/lk/credentials."""

    @pytest.mark.asyncio
    async def test_save_credentials_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test saving credentials."""
        response = await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["message"] == "Credentials saved successfully"

        # Verify status
        status_resp = await client.get("/api/v1/lk/status", headers=auth_headers)
        assert status_resp.json()["has_credentials"] is True

    @pytest.mark.asyncio
    async def test_save_credentials_update(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating existing credentials."""
        # Save initial
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "old@omsu.ru", "password": "oldpass"},
            headers=auth_headers,
        )

        # Update
        response = await client.post(
            "/api/v1/lk/credentials",
            json={"email": "new@omsu.ru", "password": "newpass"},
            headers=auth_headers,
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_save_credentials_validation_email(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test validation error for short email."""
        response = await client.post(
            "/api/v1/lk/credentials",
            json={"email": "ab", "password": "testpass"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_save_credentials_validation_password(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test validation error for empty password."""
        response = await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_save_credentials_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_credentials_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test deleting credentials."""
        # Save first
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        # Delete
        response = await client.delete("/api/v1/lk/credentials", headers=auth_headers)
        assert response.status_code == 204

        # Verify status
        status_resp = await client.get("/api/v1/lk/status", headers=auth_headers)
        assert status_resp.json()["has_credentials"] is False

    @pytest.mark.asyncio
    async def test_delete_credentials_not_exists(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test deleting when no credentials exist (should succeed silently)."""
        response = await client.delete("/api/v1/lk/credentials", headers=auth_headers)
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_credentials_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.delete("/api/v1/lk/credentials")
        assert response.status_code == 401


# ============================================================================
# LK Verify tests
# ============================================================================


class TestLkVerify:
    """Tests for POST /api/v1/lk/verify."""

    @pytest.mark.asyncio
    async def test_verify_mocked_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test verify with mocked successful login."""
        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            MockParser.return_value.__aenter__.return_value = mock_parser

            response = await client.post(
                "/api/v1/lk/verify",
                json={"email": "test@omsu.ru", "password": "testpass"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.json()["valid"] is True

    @pytest.mark.asyncio
    async def test_verify_mocked_failure(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test verify with mocked failed login."""
        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = False
            MockParser.return_value.__aenter__.return_value = mock_parser

            response = await client.post(
                "/api/v1/lk/verify",
                json={"email": "bad@omsu.ru", "password": "wrongpass"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.json()["valid"] is False

    @pytest.mark.asyncio
    async def test_verify_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.post(
            "/api/v1/lk/verify",
            json={"email": "test@omsu.ru", "password": "testpass"},
        )
        assert response.status_code == 401


# ============================================================================
# LK Sync tests
# ============================================================================


class TestLkSync:
    """Tests for POST /api/v1/lk/sync."""

    @pytest.mark.asyncio
    async def test_sync_no_credentials(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test sync fails when no credentials saved."""
        response = await client.post("/api/v1/lk/sync", headers=auth_headers)

        assert response.status_code == 400
        assert "credentials" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_sync_mocked_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test sync with mocked LK data."""
        # Save credentials first
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        # Mock LkParser
        mock_data = LkStudentData(
            sessions=[
                {
                    "number": "5 2025/2026",
                    "entries": [
                        {"subject": "Математика", "result": "Отлично"},
                        {"subject": "Физика", "result": "Хорошо"},
                    ],
                }
            ],
            sem_info=[
                {
                    "number": 5,
                    "entries": [
                        {
                            "discipline": "Математический анализ",
                            "controlForm": "Экзамен",
                            "length": 108,
                        },
                        {
                            "discipline": "Физика",
                            "controlForm": "Зачет",
                            "length": 72,
                        },
                    ],
                },
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            response = await client.post("/api/v1/lk/sync", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["grades_synced"] == 2
            assert data["disciplines_synced"] == 2
            assert data["last_sync_at"] is not None

    @pytest.mark.asyncio
    async def test_sync_auth_failure(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test sync fails when LK auth fails."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "wrongpass"},
            headers=auth_headers,
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = False
            MockParser.return_value.__aenter__.return_value = mock_parser

            response = await client.post("/api/v1/lk/sync", headers=auth_headers)

            assert response.status_code == 502
            assert "authentication" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_sync_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.post("/api/v1/lk/sync")
        assert response.status_code == 401


# ============================================================================
# LK Grades tests
# ============================================================================


class TestLkGrades:
    """Tests for GET /api/v1/lk/grades."""

    @pytest.mark.asyncio
    async def test_get_grades_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test empty grades list."""
        response = await client.get("/api/v1/lk/grades", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_grades_after_sync(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test grades list after sync."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        mock_data = LkStudentData(
            sessions=[
                {
                    "number": "5 2025/2026",
                    "entries": [
                        {"subject": "Математика", "result": "Отлично"},
                    ],
                }
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            await client.post("/api/v1/lk/sync", headers=auth_headers)

        response = await client.get("/api/v1/lk/grades", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["subject_name"] == "Математика"
        assert data[0]["result"] == "Отлично"
        assert data[0]["session_number"] == "5 2025/2026"

    @pytest.mark.asyncio
    async def test_get_grades_filter_session(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test filtering grades by session."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        mock_data = LkStudentData(
            sessions=[
                {
                    "number": "4 2024/2025",
                    "entries": [{"subject": "Физика", "result": "Хорошо"}],
                },
                {
                    "number": "5 2025/2026",
                    "entries": [{"subject": "Математика", "result": "Отлично"}],
                },
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            await client.post("/api/v1/lk/sync", headers=auth_headers)

        response = await client.get(
            "/api/v1/lk/grades",
            params={"session": "4 2024/2025"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["subject_name"] == "Физика"

    @pytest.mark.asyncio
    async def test_get_grades_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.get("/api/v1/lk/grades")
        assert response.status_code == 401


# ============================================================================
# LK Sessions list tests
# ============================================================================


class TestLkSessions:
    """Tests for GET /api/v1/lk/grades/sessions."""

    @pytest.mark.asyncio
    async def test_get_sessions_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test empty sessions list."""
        response = await client.get("/api/v1/lk/grades/sessions", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_sessions_after_sync(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test sessions list after sync."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        mock_data = LkStudentData(
            sessions=[
                {"number": "4 2024/2025", "entries": [{"subject": "A", "result": "5"}]},
                {"number": "5 2025/2026", "entries": [{"subject": "B", "result": "4"}]},
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            await client.post("/api/v1/lk/sync", headers=auth_headers)

        response = await client.get("/api/v1/lk/grades/sessions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Sorted descending
        assert data[0] == "5 2025/2026"
        assert data[1] == "4 2024/2025"


# ============================================================================
# LK Disciplines tests
# ============================================================================


class TestLkDisciplines:
    """Tests for GET /api/v1/lk/disciplines."""

    @pytest.mark.asyncio
    async def test_get_disciplines_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test empty disciplines list."""
        response = await client.get("/api/v1/lk/disciplines", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_disciplines_after_sync(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test disciplines list after sync."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        mock_data = LkStudentData(
            sem_info=[
                {
                    "number": 5,
                    "entries": [
                        {
                            "discipline": "Математический анализ",
                            "controlForm": "Экзамен",
                            "length": 108,
                        },
                    ],
                },
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            await client.post("/api/v1/lk/sync", headers=auth_headers)

        response = await client.get("/api/v1/lk/disciplines", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["discipline_name"] == "Математический анализ"
        assert data[0]["control_form"] == "Экзамен"
        assert data[0]["hours"] == 108
        assert data[0]["semester_number"] == 5

    @pytest.mark.asyncio
    async def test_get_disciplines_filter_semester(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test filtering disciplines by semester."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        mock_data = LkStudentData(
            sem_info=[
                {
                    "number": 4,
                    "entries": [
                        {
                            "discipline": "Физика",
                            "controlForm": "Зачет",
                            "length": 72,
                        },
                    ],
                },
                {
                    "number": 5,
                    "entries": [
                        {
                            "discipline": "Математика",
                            "controlForm": "Экзамен",
                            "length": 108,
                        },
                    ],
                },
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            await client.post("/api/v1/lk/sync", headers=auth_headers)

        response = await client.get(
            "/api/v1/lk/disciplines",
            params={"semester": 4},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["discipline_name"] == "Физика"

    @pytest.mark.asyncio
    async def test_get_disciplines_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.get("/api/v1/lk/disciplines")
        assert response.status_code == 401


# ============================================================================
# LK Semesters list tests
# ============================================================================


class TestLkSemesters:
    """Tests for GET /api/v1/lk/disciplines/semesters."""

    @pytest.mark.asyncio
    async def test_get_semesters_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test empty semesters list."""
        response = await client.get(
            "/api/v1/lk/disciplines/semesters", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_semesters_after_sync(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test semesters list after sync."""
        await client.post(
            "/api/v1/lk/credentials",
            json={"email": "test@omsu.ru", "password": "testpass"},
            headers=auth_headers,
        )

        mock_data = LkStudentData(
            sem_info=[
                {
                    "number": 3,
                    "entries": [
                        {"discipline": "A", "controlForm": "Зачет", "length": 36},
                    ],
                },
                {
                    "number": 4,
                    "entries": [
                        {"discipline": "B", "controlForm": "Экзамен", "length": 72},
                    ],
                },
                {
                    "number": 5,
                    "entries": [
                        {"discipline": "C", "controlForm": "Экзамен", "length": 108},
                    ],
                },
            ],
        )

        with patch("src.services.lk.LkParser") as MockParser:
            mock_parser = AsyncMock()
            mock_parser.login.return_value = True
            mock_parser.fetch_student_data.return_value = mock_data
            MockParser.return_value.__aenter__.return_value = mock_parser

            await client.post("/api/v1/lk/sync", headers=auth_headers)

        response = await client.get(
            "/api/v1/lk/disciplines/semesters", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Sorted ascending
        assert data == [3, 4, 5]


# ============================================================================
# LK Import tests (B9: semester dates from LK)
# ============================================================================


class TestLkImport:
    """Tests for import_to_app() semester logic."""

    async def _create_user(self, db: AsyncSession) -> int:
        """Create a test user and return user_id."""
        from src.models.user import User

        user = User(
            email="import_test@example.com",
            password_hash="fakehash",
            name="Import Test",
        )
        db.add(user)
        await db.flush()
        return user.id

    async def _add_disciplines(
        self,
        db: AsyncSession,
        user_id: int,
        semester_numbers: list[int],
    ) -> None:
        """Add SemesterDiscipline records for given semesters."""
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        for sem_num in semester_numbers:
            disc = SemesterDiscipline(
                user_id=user_id,
                semester_number=sem_num,
                discipline_name=f"Subject_{sem_num}",
                control_form="Экзамен",
                hours=72,
                synced_at=now,
            )
            db.add(disc)
        await db.flush()

    async def _add_session_grades(
        self,
        db: AsyncSession,
        user_id: int,
        session_numbers: list[str],
    ) -> None:
        """Add SessionGrade records for given sessions."""
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        for sess in session_numbers:
            grade = SessionGrade(
                user_id=user_id,
                session_number=sess,
                subject_name=f"Subject_{sess}",
                result="Отлично",
                synced_at=now,
            )
            db.add(grade)
        await db.flush()

    @pytest.mark.asyncio
    async def test_import_correct_semester_3rd_year(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Test 5 sessions → current=6, semester 6 = is_current."""
        user_id = await self._create_user(db_session)

        # Disciplines for semesters 1-11 (full study plan)
        await self._add_disciplines(
            db_session,
            user_id,
            list(range(1, 12)),
        )
        # 5 completed sessions → current semester = 6
        await self._add_session_grades(
            db_session,
            user_id,
            ["1 2023/2024", "2 2023/2024", "3 2024/2025", "4 2024/2025", "5 2025/2026"],
        )

        result = await import_to_app(db_session, user_id)

        assert result.semesters_created == 11

        # Check semester 6 is current
        from sqlalchemy import select

        res = await db_session.execute(select(Semester).where(Semester.number == 6))
        sem6 = res.scalar_one()
        assert sem6.is_current is True

        # Check semester 11 is NOT current
        res = await db_session.execute(select(Semester).where(Semester.number == 11))
        sem11 = res.scalar_one()
        assert sem11.is_current is False

    @pytest.mark.asyncio
    async def test_import_no_grades_defaults_to_semester_1(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Test no sessions → current=1."""
        user_id = await self._create_user(db_session)

        await self._add_disciplines(
            db_session,
            user_id,
            [1, 2, 3, 4, 5],
        )
        # No session grades at all

        result = await import_to_app(db_session, user_id)

        assert result.semesters_created == 5

        from sqlalchemy import select

        res = await db_session.execute(select(Semester).where(Semester.number == 1))
        sem1 = res.scalar_one()
        assert sem1.is_current is True

        res = await db_session.execute(select(Semester).where(Semester.number == 5))
        sem5 = res.scalar_one()
        assert sem5.is_current is False

    @pytest.mark.asyncio
    async def test_import_fills_semester_dates(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Test odd=Sep1-Dec30, even=Feb9-Jul7."""
        user_id = await self._create_user(db_session)

        await self._add_disciplines(db_session, user_id, [5, 6])
        await self._add_session_grades(
            db_session,
            user_id,
            ["1 2023/2024", "2 2023/2024", "3 2024/2025", "4 2024/2025", "5 2025/2026"],
        )

        await import_to_app(db_session, user_id)

        from sqlalchemy import select

        # Semester 5 (odd = fall)
        res = await db_session.execute(select(Semester).where(Semester.number == 5))
        sem5 = res.scalar_one()
        assert sem5.start_date is not None
        assert sem5.end_date is not None
        assert sem5.start_date.month == 9
        assert sem5.start_date.day == 1
        assert sem5.end_date.month == 12
        assert sem5.end_date.day == 30

        # Semester 6 (even = spring)
        res = await db_session.execute(select(Semester).where(Semester.number == 6))
        sem6 = res.scalar_one()
        assert sem6.start_date is not None
        assert sem6.end_date is not None
        assert sem6.start_date.month == 2
        assert sem6.start_date.day == 9
        assert sem6.end_date.month == 7
        assert sem6.end_date.day == 7

    @pytest.mark.asyncio
    async def test_import_does_not_overwrite_manual_dates(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Test manual dates are preserved after re-import."""
        user_id = await self._create_user(db_session)

        await self._add_disciplines(db_session, user_id, [5])
        await self._add_session_grades(
            db_session,
            user_id,
            ["1 2023/2024", "2 2023/2024", "3 2024/2025", "4 2024/2025"],
        )

        # First import creates semester with default dates
        await import_to_app(db_session, user_id)

        from sqlalchemy import select

        res = await db_session.execute(select(Semester).where(Semester.number == 5))
        sem5 = res.scalar_one()

        # Simulate user manually changing dates
        manual_start = date(2025, 9, 2)
        manual_end = date(2025, 12, 28)
        sem5.start_date = manual_start
        sem5.end_date = manual_end
        await db_session.commit()

        # Re-import should NOT overwrite manual dates
        await import_to_app(db_session, user_id)

        await db_session.refresh(sem5)
        assert sem5.start_date == manual_start
        assert sem5.end_date == manual_end

    @pytest.mark.asyncio
    async def test_import_is_current_updated_on_reimport(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Test is_current updates when new sessions appear."""
        user_id = await self._create_user(db_session)

        await self._add_disciplines(db_session, user_id, [5, 6])
        # First import: 4 sessions → current = 5
        await self._add_session_grades(
            db_session,
            user_id,
            ["1 2023/2024", "2 2023/2024", "3 2024/2025", "4 2024/2025"],
        )

        await import_to_app(db_session, user_id)

        from sqlalchemy import select

        res = await db_session.execute(select(Semester).where(Semester.number == 5))
        sem5 = res.scalar_one()
        assert sem5.is_current is True

        res = await db_session.execute(select(Semester).where(Semester.number == 6))
        sem6 = res.scalar_one()
        assert sem6.is_current is False

        # Add session 5 → current becomes 6
        await self._add_session_grades(
            db_session,
            user_id,
            ["5 2025/2026"],
        )

        await import_to_app(db_session, user_id)

        await db_session.refresh(sem5)
        await db_session.refresh(sem6)
        assert sem5.is_current is False
        assert sem6.is_current is True
