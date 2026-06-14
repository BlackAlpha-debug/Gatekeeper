import pytest
from core.governance.masker import DataMasker, SENSITIVE_PATTERNS


class TestDefaultMasking:
    """Masker with default sensitive patterns."""

    def setup_method(self):
        self.masker = DataMasker()

    def test_password_masked(self, sample_rows):
        result = self.masker.mask(sample_rows)
        for row in result:
            assert row["password"] == "***MASKED***"

    def test_email_masked(self, sample_rows):
        result = self.masker.mask(sample_rows)
        for row in result:
            assert row["email"] == "***MASKED***"

    def test_id_not_masked(self, sample_rows):
        result = self.masker.mask(sample_rows)
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert result[2]["id"] == 3

    def test_name_not_masked(self, sample_rows):
        result = self.masker.mask(sample_rows)
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"
        assert result[2]["name"] == "Charlie"

    def test_empty_rows(self):
        result = self.masker.mask([])
        assert result == []

    def test_no_sensitive_columns(self):
        rows = [{"id": 1, "name": "Alice", "age": 30}]
        result = self.masker.mask(rows)
        assert result == [{"id": 1, "name": "Alice", "age": 30}]

    def test_original_rows_not_mutated(self, sample_rows):
        original_email = sample_rows[0]["email"]
        self.masker.mask(sample_rows)
        assert sample_rows[0]["email"] == original_email

    def test_ssn_column_masked(self):
        rows = [{"id": 1, "ssn": "123-45-6789"}]
        result = self.masker.mask(rows)
        assert result[0]["ssn"] == "***MASKED***"

    def test_credit_card_masked(self):
        rows = [{"id": 1, "credit_card": "4111-1111-1111-1111"}]
        result = self.masker.mask(rows)
        assert result[0]["credit_card"] == "***MASKED***"

    def test_api_key_masked(self):
        rows = [{"id": 1, "api_key": "sk-abc123"}]
        result = self.masker.mask(rows)
        assert result[0]["api_key"] == "***MASKED***"

    def test_token_column_masked(self):
        rows = [{"id": 1, "auth_token": "xyz"}]
        result = self.masker.mask(rows)
        assert result[0]["auth_token"] == "***MASKED***"

    def test_phone_masked(self):
        rows = [{"id": 1, "phone": "555-1234"}]
        result = self.masker.mask(rows)
        assert result[0]["phone"] == "***MASKED***"

    def test_dob_masked(self):
        rows = [{"id": 1, "dob": "1990-01-01"}]
        result = self.masker.mask(rows)
        assert result[0]["dob"] == "***MASKED***"


class TestExtraColumns:
    """Masker with custom extra_columns."""

    def test_extra_column_masked(self):
        masker = DataMasker(extra_columns=["salary"])
        rows = [{"id": 1, "name": "Alice", "salary": 100000}]
        result = masker.mask(rows)
        assert result[0]["salary"] == "***MASKED***"
        assert result[0]["name"] == "Alice"

    def test_extra_does_not_remove_defaults(self):
        masker = DataMasker(extra_columns=["salary"])
        rows = [{"id": 1, "password": "secret", "salary": 100000}]
        result = masker.mask(rows)
        assert result[0]["password"] == "***MASKED***"
        assert result[0]["salary"] == "***MASKED***"
