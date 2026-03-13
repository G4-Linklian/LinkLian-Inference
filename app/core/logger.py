import json
from datetime import datetime


class AppLogger:
    def __init__(self):
        pass

    def _format_date(self) -> str:
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def _print(self, level: str, from_: str, title: str, detail=None):
        timestamp = self._format_date()
        header = f"{timestamp} {level.upper()} [{from_}] {title}"

        print("\n")
        if detail is not None:
            try:
                formatted_detail = json.dumps(detail, indent=2, default=str)
            except Exception:
                formatted_detail = str(detail)

            print(f"{header} {formatted_detail}")
        else:
            print(header)

    def log(self, message: str, from_: str = "System", detail=None):
        self._print("log", from_, message, detail)

    def error(self, message: str, from_: str = "System", detail=None):
        self._print("error", from_, message, detail)

    def warn(self, message: str, from_: str = "System", detail=None):
        self._print("warn", from_, message, detail)

    def debug(self, message: str, from_: str = "System", detail=None):
        self._print("debug", from_, message, detail)

    def verbose(self, message: str, from_: str = "System", detail=None):
        self._print("verbose", from_, message, detail)