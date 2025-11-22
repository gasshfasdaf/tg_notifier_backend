from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any, Annotated
import re


class TelegramChatID(int):
    """Custom type for Telegram Chat ID validation."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.int_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v: int, info: core_schema.ValidationInfo):
        """Validate Telegram Chat ID."""
        if not isinstance(v, int):
            raise ValueError('Telegram Chat ID must be an integer')

        # Telegram Chat ID can be positive (users) or negative (groups/channels)
        # Personal chats: positive numbers
        # Groups: negative numbers starting with -100
        # Supergroups: negative numbers starting with -100
        # Channels: negative numbers starting with -100

        if v == 0:
            raise ValueError('Telegram Chat ID cannot be zero')

        return cls(v)


class URLString(str):
    """Custom type for URL validation."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )

    @classmethod
    def validate(cls, v: str, info: core_schema.ValidationInfo):
        """Validate URL string."""
        if not isinstance(v, str):
            raise ValueError('URL must be a string')

        # Basic URL validation
        url_pattern = re.compile(
            r'^(https?|ftp)://'  # http://, https://, or ftp://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')

        return cls(v)


class PositiveInt(int):
    """Custom type for positive integers."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.int_schema(),
        )

    @classmethod
    def validate(cls, v: int, info: core_schema.ValidationInfo):
        """Validate positive integer."""
        if not isinstance(v, int):
            raise ValueError('Must be an integer')

        if v <= 0:
            raise ValueError('Must be a positive integer')

        return cls(v)


# Type aliases for better readability
TelegramChatIDType = Annotated[TelegramChatID, "Telegram Chat ID"]
URLStringType = Annotated[URLString, "URL String"]
PositiveIntType = Annotated[PositiveInt, "Positive Integer"]