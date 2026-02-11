"""Tests for LK (личный кабинет) module."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.parser.lk_parser import LkStudentData
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
                    "semester": 5,
                    "discipline": "Математический анализ",
                    "controlForm": "Экзамен",
                    "length": 108,
                },
                {
                    "semester": 5,
                    "discipline": "Физика",
                    "controlForm": "Зачет",
                    "length": 72,
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
                    "semester": 5,
                    "discipline": "Математический анализ",
                    "controlForm": "Экзамен",
                    "length": 108,
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
                    "semester": 4,
                    "discipline": "Физика",
                    "controlForm": "Зачет",
                    "length": 72,
                },
                {
                    "semester": 5,
                    "discipline": "Математика",
                    "controlForm": "Экзамен",
                    "length": 108,
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
                    "semester": 3,
                    "discipline": "A",
                    "controlForm": "Зачет",
                    "length": 36,
                },
                {
                    "semester": 4,
                    "discipline": "B",
                    "controlForm": "Экзамен",
                    "length": 72,
                },
                {
                    "semester": 5,
                    "discipline": "C",
                    "controlForm": "Экзамен",
                    "length": 108,
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
