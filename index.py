"""Vercel giriş noktası.

Uygulama `src/ekozeka26/` altında (src düzeni) olduğu için Vercel onu kendiliğinden
bulamıyor. Bu ince sarmalayıcı `src/` dizinini import yoluna ekleyip FastAPI
uygulamasını dışa açar. `pyproject.toml` içindeki `[tool.vercel] entrypoint`
bu dosyayı gösterir. Yerelde yine `bash scripts/run.sh` kullanılır.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ekozeka26.app import app  # noqa: E402

__all__ = ["app"]
