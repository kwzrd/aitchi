import json
import logging
import typing as t
from pathlib import Path

log = logging.getLogger(__name__)

# Each key can either map to a JSON-recognised primitive, or a list thereof. This is not strictly true with regards
# to what JSON can store, but we cannot express recursive types and this is sufficient for our purposes.
ValuePrimitive = t.Union[str, int, float, None]
Value = t.Union[ValuePrimitive, list[ValuePrimitive]]

Namespace = t.Dict[str, Value]  # Namespace maps string keys to values
Database = t.Dict[str, Namespace]  # Database then maps namespace names to objects

DB = Path("database.json")

if not DB.exists():
    DB.write_text("{}", encoding="UTF-8")  # Initialize with an empty object


def read() -> Database:
    """Read the current `DB` state into a Python object."""
    text = DB.read_text(encoding="UTF-8")
    return json.loads(text)


def write(db: Database) -> None:
    """Persist `db` in the filesystem."""
    text = json.dumps(db)
    DB.write_text(text, encoding="UTF-8")


class Store:
    """Primitive namespace-aware persistence."""

    def __init__(self, namespace: str) -> None:
        """
        Prepare an instance with a `namespace`.

        All operations on the instance will be automatically applied on the `namespace`.
        """
        self.namespace = namespace

    def __repr__(self) -> str:
        """
        String representation.

        This is primarily useful for logging.
        """
        return f"Store(namespace={self.namespace!r})"

    def get(self, key: str, default: t.Optional[Value] = None) -> Value:
        """
        Retrieve the value of `key` from the namespace.

        Return `default` if not found.
        """
        log.debug(f"{self} getting {key!r} with default of {default!r}")

        try:
            return read()[self.namespace][key]
        except KeyError:
            return default

    def set(self, key: str, value: Value) -> None:
        """
        Write `value` under `key` in the namespace.

        If `key` already exists, it will be overwritten.
        """
        log.debug(f"{self} setting {key!r} to {value!r}")

        db = read()

        if self.namespace not in db:
            db[self.namespace] = {}

        db[self.namespace][key] = value

        write(db)
