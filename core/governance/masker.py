SENSITIVE_PATTERNS = [
    "password", "secret", "token", "ssn",
    "credit_card", "card_number", "api_key",
    "email", "phone", "dob", "birth",
]


class DataMasker:

    def __init__(self, extra_columns: list[str] | None = None):
        self.sensitive = SENSITIVE_PATTERNS + (extra_columns or [])

    def mask(self, rows: list[dict]) -> list[dict]:
        if not rows:
            return rows

        masked_cols = [
            col for col in rows[0].keys()
            if any(s in col.lower() for s in self.sensitive)
        ]

        result = []
        for row in rows:
            masked_row = dict(row)
            for col in masked_cols:
                masked_row[col] = "***MASKED***"
            result.append(masked_row)

        return result
