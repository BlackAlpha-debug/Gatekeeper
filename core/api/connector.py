import requests
import yaml

REQUEST_TIMEOUT = 30


class OpenAPIConnector:

    def __init__(self, spec_url: str, base_url: str,
                 api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.tools    = self._parse_spec(spec_url)

    def _parse_spec(self, spec_url: str) -> dict:
        try:
            r = requests.get(spec_url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            if spec_url.endswith((".yaml", ".yml")):
                spec = yaml.safe_load(r.text)
            else:
                spec = r.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch spec from {spec_url}: {e}")

        tools = {}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ("get", "post"):
                    continue
                name = details.get(
                    "operationId",
                    f"{method}_{path.replace('/', '_').strip('_')}"
                )
                tools[name] = {
                    "path":    path,
                    "method":  method.lower(),
                    "summary": details.get("summary", "No description"),
                }
        return tools

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def call(self, tool_name: str, params: dict | None = None) -> dict:
        params = params or {}
        if tool_name not in self.tools:
            return {"error": f"Unknown op '{tool_name}'. Available: {list(self.tools)}"}

        tool = self.tools[tool_name]
        url  = self.base_url + tool["path"]

        try:
            if tool["method"] == "get":
                r = requests.get(url, params=params,
                                  headers=self._headers(), timeout=REQUEST_TIMEOUT)
            else:
                r = requests.post(url, json=params,
                                   headers=self._headers(), timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()

        except requests.Timeout:
            return {"error": f"Request to {url} timed out after {REQUEST_TIMEOUT}s"}
        except requests.RequestException as e:
            return {"error": f"HTTP error: {e}"}

    def list_operations(self) -> list[dict]:
        return [
            {"name": n, "method": t["method"],
             "path": t["path"], "summary": t["summary"]}
            for n, t in self.tools.items()
        ]
