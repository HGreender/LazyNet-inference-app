"""Фоновый воркер: проверка и подтягивание обновлений приложения из git."""
import subprocess
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

# Каталог проекта (где лежит main.py)
APP_DIR = Path(__file__).resolve().parent.parent
REMOTE = "origin"
BRANCH = "main"


class UpdateWorker(QThread):
    """Проверяет новые коммиты ветки main и при наличии подтягивает их."""

    # (статус, сообщение, количество новых коммитов)
    # статус: "up_to_date" | "updated" | "error"
    result = pyqtSignal(str, str, int)
    log_message = pyqtSignal(str)

    def run(self):
        try:
            self._log("Проверка обновлений…")
            self._git("fetch", REMOTE, BRANCH)

            count = self._count_new_commits()
            if count == 0:
                self.result.emit("up_to_date", "Приложение актуально", 0)
                return

            self._log(f"Найдено новых коммитов: {count}")

            # Не трогаем грязное рабочее дерево
            dirty = self._git("status", "--porcelain").stdout.strip()
            if dirty:
                self.result.emit(
                    "error",
                    "Есть незакоммиченные локальные изменения — обновление "
                    "пропущено. Сначала закоммитьте или отложите (stash) изменения.",
                    0,
                )
                return

            self._git("merge", "--ff-only", f"{REMOTE}/{BRANCH}")
            self.result.emit("updated", f"Подтянуто новых коммитов: {count}", count)
        except Exception as e:
            self.result.emit("error", str(e), 0)

    def _git(self, *args, timeout: int = 60):
        """Выполняет git-команду в каталоге проекта, бросает исключение при ошибке."""
        proc = subprocess.run(
            ["git", *args],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            msg = proc.stderr.strip() or f"git {' '.join(args)} завершилась с кодом {proc.returncode}"
            raise RuntimeError(msg)
        return proc

    def _count_new_commits(self) -> int:
        """Сколько коммитов в origin/main ещё нет в локальном HEAD."""
        proc = self._git("rev-list", f"HEAD..{REMOTE}/{BRANCH}", "--count")
        return int(proc.stdout.strip() or 0)

    def _log(self, message: str):
        self.log_message.emit(message)