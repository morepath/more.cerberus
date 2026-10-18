from collections.abc import Callable, Hashable, Iterable, Iterator, MutableMapping
from typing import Any, Literal, NamedTuple, NoReturn, TypeVar, overload

from cerberus.validator import Validator

_F = TypeVar("_F", bound=Callable[..., Any])

class ErrorDefinition(NamedTuple):
    code: int
    rule: str | None

# custom
CUSTOM: ErrorDefinition

# existence
DOCUMENT_MISSING: str  # rebound from an ErrorDefinition to a message at runtime
REQUIRED_FIELD: ErrorDefinition
UNKNOWN_FIELD: ErrorDefinition
DEPENDENCIES_FIELD: ErrorDefinition
DEPENDENCIES_FIELD_VALUE: ErrorDefinition
EXCLUDES_FIELD: ErrorDefinition

# shape
DOCUMENT_FORMAT: str  # rebound from an ErrorDefinition to a message at runtime
EMPTY_NOT_ALLOWED: ErrorDefinition
NOT_NULLABLE: ErrorDefinition
BAD_TYPE: ErrorDefinition
BAD_TYPE_FOR_SCHEMA: ErrorDefinition
ITEMS_LENGTH: ErrorDefinition
MIN_LENGTH: ErrorDefinition
MAX_LENGTH: ErrorDefinition

# color
REGEX_MISMATCH: ErrorDefinition
MIN_VALUE: ErrorDefinition
MAX_VALUE: ErrorDefinition
UNALLOWED_VALUE: ErrorDefinition
UNALLOWED_VALUES: ErrorDefinition
FORBIDDEN_VALUE: ErrorDefinition
FORBIDDEN_VALUES: ErrorDefinition
MISSING_MEMBERS: ErrorDefinition

# other
NORMALIZATION: ErrorDefinition
COERCION_FAILED: ErrorDefinition
RENAMING_FAILED: ErrorDefinition
READONLY_FIELD: ErrorDefinition
SETTING_DEFAULT_FAILED: ErrorDefinition

# groups
ERROR_GROUP: ErrorDefinition
MAPPING_SCHEMA: ErrorDefinition
SEQUENCE_SCHEMA: ErrorDefinition
KEYSRULES: ErrorDefinition
KEYSCHEMA: ErrorDefinition  # deprecated alias of KEYSRULES
VALUESRULES: ErrorDefinition
VALUESCHEMA: ErrorDefinition  # deprecated alias of VALUESRULES
BAD_ITEMS: ErrorDefinition

LOGICAL: ErrorDefinition
NONEOF: ErrorDefinition
ONEOF: ErrorDefinition
ANYOF: ErrorDefinition
ALLOF: ErrorDefinition

# SchemaError messages
SCHEMA_ERROR_DEFINITION_TYPE: str
SCHEMA_ERROR_MISSING: str

# Error representations

class ValidationError:
    document_path: tuple[Hashable, ...]
    schema_path: tuple[Hashable, ...]
    code: int
    rule: str | None
    constraint: Any
    value: Any
    info: tuple[Any, ...]
    def __init__(
        self,
        document_path: tuple[Hashable, ...],
        schema_path: tuple[Hashable, ...],
        code: int,
        rule: str | None,
        constraint: Any,
        value: Any,
        info: tuple[Any, ...],
    ) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __lt__(self, other: ValidationError) -> bool: ...
    @property
    def child_errors(self) -> list[ValidationError] | None: ...
    @property
    def definitions_errors(self) -> dict[int, list[ValidationError]] | None: ...
    @property
    def field(self) -> Hashable | None: ...
    @property
    def is_group_error(self) -> bool: ...
    @property
    def is_logic_error(self) -> bool: ...
    @property
    def is_normalization_error(self) -> bool: ...

class ErrorList(list[ValidationError]):
    def __contains__(self, error_definition: ErrorDefinition) -> bool: ...  # type: ignore[override]

class ErrorTreeNode(MutableMapping[Any, Any]):
    descendants: dict[Hashable, ErrorTreeNode]
    errors: ErrorList
    parent_node: ErrorTreeNode | None
    path: tuple[Hashable, ...]
    tree_root: ErrorTree
    def __init__(
        self, path: tuple[Hashable, ...], parent_node: ErrorTreeNode
    ) -> None: ...
    def __contains__(self, item: object) -> bool: ...
    def __delitem__(self, key: Any) -> None: ...
    def __iter__(self) -> Iterator[ValidationError]: ...
    @overload
    def __getitem__(self, item: ErrorDefinition) -> ValidationError | None: ...  # type: ignore[overload-overlap]
    @overload
    def __getitem__(self, item: Hashable) -> ErrorTreeNode | None: ...
    def __len__(self) -> int: ...
    def __setitem__(self, key: Any, value: ErrorTreeNode) -> None: ...
    @property
    def depth(self) -> int: ...
    @property
    def tree_type(self) -> str: ...
    def add(self, error: ValidationError) -> None: ...
    def _path_of_(self, error: ValidationError) -> tuple[Hashable, ...]: ...

class ErrorTree(ErrorTreeNode):
    def __init__(self, errors: Iterable[ValidationError] = ()) -> None: ...
    def add(self, error: ValidationError) -> None: ...
    def fetch_errors_from(self, path: tuple[Hashable, ...]) -> ErrorList: ...
    def fetch_node_from(self, path: tuple[Hashable, ...]) -> ErrorTreeNode | None: ...

class DocumentErrorTree(ErrorTree):
    @property
    def tree_type(self) -> Literal["document"]: ...

class SchemaErrorTree(ErrorTree):
    @property
    def tree_type(self) -> Literal["schema"]: ...

class BaseErrorHandler:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __call__(self, errors: Iterable[ValidationError]) -> Any: ...
    def __iter__(self) -> Iterator[Any]: ...
    def add(self, error: ValidationError) -> None: ...
    def emit(self, error: ValidationError) -> None: ...
    def end(self, validator: Validator) -> None: ...
    def extend(self, errors: Iterable[ValidationError]) -> None: ...
    def start(self, validator: Validator) -> None: ...

class ToyErrorHandler(BaseErrorHandler):
    def __call__(self, *args: Any, **kwargs: Any) -> NoReturn: ...
    def clear(self) -> None: ...

def encode_unicode(f: _F) -> _F: ...

class BasicErrorHandler(BaseErrorHandler):
    messages: dict[int, str]
    tree: dict[Any, Any]
    def __init__(self, tree: dict[Any, Any] | None = None) -> None: ...
    def __call__(self, errors: Iterable[ValidationError]) -> dict[Any, Any]: ...
    @property
    def pretty_tree(self) -> dict[Any, Any]: ...
    def add(self, error: ValidationError) -> None: ...
    def clear(self) -> None: ...
    def start(self, validator: Validator) -> None: ...
    def _format_message(self, field: Hashable, error: ValidationError) -> str: ...
    def _insert_error(
        self, path: tuple[Hashable, ...], node: str | dict[Any, Any]
    ) -> None: ...
    def _insert_group_error(self, error: ValidationError) -> None: ...
    def _insert_logic_error(self, error: ValidationError) -> None: ...
    def _purge_empty_dicts(self, error_list: list[Any]) -> None: ...
    def _rewrite_error_path(self, error: ValidationError, offset: int = 0) -> None: ...
    def _rewrite_group_error_path(
        self, error: ValidationError, offset: int = 0
    ) -> None: ...
    def _rewrite_logic_error_path(
        self, error: ValidationError, offset: int = 0
    ) -> None: ...

class SchemaErrorHandler(BasicErrorHandler):
    messages: dict[int, str]
