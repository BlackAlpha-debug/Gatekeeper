import re

BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE",
    "ALTER", "CREATE", "INSERT", "UPDATE",
]

DANGEROUS_PATTERNS = ["--", ";--", "/*", "*/", "xp_"]


class QueryValidator:

    def __init__(self, allow_writes: bool = False):
        self.allow_writes = allow_writes

    def validate(self, sql: str) -> tuple[bool, str]:
        sql_upper = sql.upper().strip()

        if not self.allow_writes:
            for keyword in BLOCKED_KEYWORDS:
                # \b = word boundary: blocks DROP but NOT "created_at"
                if re.search(rf'\b{keyword}\b', sql_upper):
                    return False, (
                        f"Write operation '{keyword}' is blocked. "
                        "Server is in read-only mode."
                    )

        for pattern in DANGEROUS_PATTERNS:
            if pattern in sql:
                return False, f"Dangerous pattern detected: '{pattern}'"

        return True, "OK"
