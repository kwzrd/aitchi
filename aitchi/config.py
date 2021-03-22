import os


class _Env:
    """Configuration set via environment variables."""

    token: str  # Discord bot credentials
    prefix: str  # Command prefix

    def __init__(self) -> None:
        """
        Grab annotated attributes from environment variables.

        Raises an exception if not all attributes are found.
        """
        missing = []

        for attribute in self.__annotations__:
            lookup_name = attribute.upper()
            if (value := os.getenv(lookup_name)) is not None:
                setattr(self, attribute, value)
            else:
                missing.append(attribute)

        if missing:
            as_string = ", ".join(missing)
            raise Exception(f"Attributes not found in environment variables: {as_string}")


Env = _Env()
