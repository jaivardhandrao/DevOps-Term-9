"""Create a disposable local password without printing or committing it."""
import os
from pathlib import Path
import secrets

directory = Path(__file__).resolve().parent.parent / ".runtime"
directory.mkdir(mode=0o700, exist_ok=True)
password_file = directory / "postgres-password"
try:
    descriptor = os.open(password_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
except FileExistsError:
    print("Existing local password preserved.")
else:
    with os.fdopen(descriptor, "w") as stream:
        stream.write(secrets.token_urlsafe(36))
    # Parent directory is private; the mounted file must be readable by the
    # non-root application user inside its isolated container.
    password_file.chmod(0o644)
    print("Created disposable Compose password in .runtime (value not displayed).")
