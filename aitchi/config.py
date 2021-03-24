import os


class _Env:
    """Configuration set via environment variables."""

    token: str  # Discord bot credentials
    prefix: str  # Command prefix

    def __init__(self) -> None:
        """
        Grab annotated attributes from environment variables.

        Each attribute is converted to their annotated type. It is therefore not possible to dynamically load an
        arbitrary type ~ only those that can be automatically instantiated from a string repr.

        Raises an exception if not all attributes are found.
        """
        missing = []

        for attribute, annotated_type in self.__annotations__.items():
            lookup_name = attribute.upper()
            if (value := os.getenv(lookup_name)) is not None:
                typed_value = annotated_type(value)
                setattr(self, attribute, typed_value)
            else:
                missing.append(attribute)

        if missing:
            as_string = ", ".join(missing)
            raise Exception(f"Attributes not found in environment variables: {as_string}")


Env = _Env()
