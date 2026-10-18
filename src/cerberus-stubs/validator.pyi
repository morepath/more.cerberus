from collections.abc import Callable, Hashable, Iterable, Mapping, MutableMapping
from typing import Any, ClassVar, Literal, NoReturn, Self, TypeAlias, TypeVar, overload

from cerberus.errors import (
    BaseErrorHandler,
    DocumentErrorTree,
    ErrorDefinition,
    ErrorList,
    SchemaErrorTree,
    ToyErrorHandler,
    ValidationError,
)
from cerberus.schema import DefinitionSchema, Registry
from cerberus.utils import TypeDefinition

_T = TypeVar("_T")
_M = TypeVar("_M", bound=Mapping[Any, Any])
_MM = TypeVar("_MM", bound=MutableMapping[Any, Any])

# A schema can be given as a mapping or as the name of an entry of the schema registry.
_SchemaArg: TypeAlias = Mapping[Any, Any] | str
_ErrorHandlerArg: TypeAlias = (
    type[BaseErrorHandler]
    | BaseErrorHandler
    | tuple[type[BaseErrorHandler], Mapping[str, Any]]
)

RULE_SCHEMA_SEPARATOR: str

toy_error_handler: ToyErrorHandler

def dummy_for_rule_validation(
    rule_constraints: str,
) -> Callable[[Any, Any, Any, Any], NoReturn]: ...

class DocumentError(Exception): ...
class _SchemaRuleTypeError(Exception): ...

class BareValidator:
    mandatory_validations: tuple[str, ...]
    priority_validations: tuple[str, ...]
    types_mapping: dict[str, TypeDefinition]
    _valid_schemas: ClassVar[set[tuple[int, int]]]

    # Attributes of an instance.
    document: Mapping[Any, Any] | None
    recent_error: ValidationError | None
    document_error_tree: DocumentErrorTree
    schema_error_tree: SchemaErrorTree
    document_path: tuple[Hashable, ...]
    schema_path: tuple[Hashable, ...]
    update: bool
    error_handler: BaseErrorHandler
    _errors: ErrorList
    _config: dict[str, Any]
    _remaining_rules: list[str]
    _unrequired_by_excludes: set[Any]
    _schema: DefinitionSchema | Mapping[Any, Any] | str | None

    def __init__(
        self,
        schema: _SchemaArg | None = None,
        ignore_none_values: bool = False,
        allow_unknown: bool | Mapping[Any, Any] | str = False,
        require_all: bool = False,
        purge_unknown: bool = False,
        purge_readonly: bool = False,
        *,
        error_handler: _ErrorHandlerArg = ...,
        **kwargs: Any,
    ) -> None: ...
    @classmethod
    def clear_caches(cls) -> None: ...
    @overload
    def _error(self, errors: Iterable[ValidationError], /) -> None: ...
    @overload
    def _error(self, field: Hashable, message: str, /) -> None: ...
    @overload
    def _error(
        self, field: Hashable, error: ErrorDefinition, /, *info: Any
    ) -> None: ...
    def _get_child_validator(
        self,
        document_crumb: Hashable | tuple[Hashable, ...] | None = None,
        schema_crumb: Hashable | tuple[Hashable, ...] | None = None,
        **kwargs: Any,
    ) -> Self: ...
    def _drop_nodes_from_errorpaths(
        self,
        _errors: Iterable[ValidationError],
        dp_items: Iterable[int],
        sp_items: Iterable[int],
    ) -> None: ...
    def _lookup_field(self, path: str) -> tuple[str | None, Any]: ...
    def _resolve_rules_set(self, rules_set: Any) -> Mapping[Any, Any] | None: ...
    def _resolve_schema(self, schema: Any) -> Mapping[Any, Any] | None: ...
    def _drop_remaining_rules(self, *rules: str) -> None: ...

    # Properties

    @property
    def allow_unknown(self) -> bool | Mapping[Any, Any] | str: ...
    @allow_unknown.setter
    def allow_unknown(self, value: bool | Mapping[Any, Any] | str) -> None: ...
    @property
    def require_all(self) -> bool: ...
    @require_all.setter
    def require_all(self, value: bool) -> None: ...
    @property
    def errors(self) -> Any: ...
    @property
    def ignore_none_values(self) -> bool: ...
    @ignore_none_values.setter
    def ignore_none_values(self, value: bool) -> None: ...
    @property
    def is_child(self) -> bool: ...
    @property
    def _is_normalized(self) -> bool: ...
    @_is_normalized.setter
    def _is_normalized(self, value: bool) -> None: ...
    @property
    def purge_unknown(self) -> bool: ...
    @purge_unknown.setter
    def purge_unknown(self, value: bool) -> None: ...
    @property
    def purge_readonly(self) -> bool: ...
    @purge_readonly.setter
    def purge_readonly(self, value: bool) -> None: ...
    @property
    def root_allow_unknown(self) -> bool | Mapping[Any, Any] | str: ...
    @property
    def root_require_all(self) -> bool: ...
    @property
    def root_document(self) -> Mapping[Any, Any] | None: ...
    @property
    def rules_set_registry(self) -> Registry: ...
    @rules_set_registry.setter
    def rules_set_registry(self, registry: Registry) -> None: ...
    @property
    def root_schema(self) -> DefinitionSchema | Mapping[Any, Any] | str | None: ...
    # The setter also accepts the name of a schema registry entry. It is not part of
    # this annotation so that assignments of mappings work with every type checker
    # that does not support differing types of getters and setters.
    @property
    def schema(self) -> DefinitionSchema | Mapping[Any, Any] | None: ...
    @schema.setter
    def schema(self, schema: DefinitionSchema | Mapping[Any, Any] | None) -> None: ...
    @property
    def schema_registry(self) -> Registry: ...
    @schema_registry.setter
    def schema_registry(self, registry: Registry) -> None: ...
    types: ClassVar[tuple[str, ...]]
    """The constraints that can be used for the 'type' rule."""

    # Normalizing

    @overload
    def normalized(
        self,
        document: _M,
        schema: _SchemaArg | None = None,
        always_return_document: Literal[False] = False,
    ) -> _M | None: ...
    @overload
    def normalized(
        self,
        document: _M,
        schema: _SchemaArg | None = None,
        *,
        always_return_document: Literal[True],
    ) -> _M: ...
    @overload
    def normalized(
        self,
        document: _M,
        schema: _SchemaArg | None = None,
        always_return_document: bool = False,
    ) -> _M | None: ...

    # Normalization rules
    def _normalize_coerce(
        self, mapping: MutableMapping[Any, Any], schema: Mapping[Any, Any]
    ) -> None: ...
    @staticmethod
    def _normalize_purge_unknown(mapping: _MM, schema: Mapping[Any, Any]) -> _MM: ...
    def _normalize_rename(
        self, mapping: MutableMapping[Any, Any], schema: Mapping[Any, Any], field: Any
    ) -> None: ...
    def _normalize_rename_handler(
        self, mapping: MutableMapping[Any, Any], schema: Mapping[Any, Any], field: Any
    ) -> None: ...
    def _normalize_default(
        self, mapping: MutableMapping[Any, Any], schema: Mapping[Any, Any], field: Any
    ) -> None: ...
    def _normalize_default_setter(
        self, mapping: MutableMapping[Any, Any], schema: Mapping[Any, Any], field: Any
    ) -> None: ...

    # Validating

    def validate(
        self,
        document: Mapping[Any, Any],
        schema: _SchemaArg | None = None,
        update: bool = False,
        normalize: bool = True,
    ) -> bool: ...
    def __call__(
        self,
        document: Mapping[Any, Any],
        schema: _SchemaArg | None = None,
        update: bool = False,
        normalize: bool = True,
    ) -> bool: ...
    @overload
    def validated(
        self,
        document: _M,
        schema: _SchemaArg | None = None,
        update: bool = False,
        normalize: bool = True,
        *,
        always_return_document: Literal[False] = False,
    ) -> _M | None: ...
    @overload
    def validated(
        self,
        document: _M,
        schema: _SchemaArg | None = None,
        update: bool = False,
        normalize: bool = True,
        *,
        always_return_document: Literal[True],
    ) -> _M: ...
    @overload
    def validated(
        self,
        document: _M,
        schema: _SchemaArg | None = None,
        update: bool = False,
        normalize: bool = True,
        *,
        always_return_document: bool = False,
    ) -> _M | None: ...

    # Validation rules
    def _validate_allow_unknown(
        self, constraint: Any, field: Any, value: Any
    ) -> NoReturn: ...
    def _validate_allowed(
        self, allowed_values: Any, field: Any, value: Any
    ) -> None: ...
    def _validate_check_with(self, checks: Any, field: Any, value: Any) -> None: ...
    def _validate_contains(
        self, expected_values: Any, field: Any, value: Any
    ) -> None: ...
    def _validate_dependencies(
        self, dependencies: Any, field: Any, value: Any
    ) -> bool | None: ...
    def _validate_empty(self, empty: Any, field: Any, value: Any) -> None: ...
    def _validate_excludes(
        self, excluded_fields: Any, field: Any, value: Any
    ) -> None: ...
    def _validate_forbidden(
        self, forbidden_values: Any, field: Any, value: Any
    ) -> None: ...
    def _validate_items(self, items: Any, field: Any, values: Any) -> None: ...
    def _validate_anyof(self, definitions: Any, field: Any, value: Any) -> None: ...
    def _validate_allof(self, definitions: Any, field: Any, value: Any) -> None: ...
    def _validate_noneof(self, definitions: Any, field: Any, value: Any) -> None: ...
    def _validate_oneof(self, definitions: Any, field: Any, value: Any) -> None: ...
    def _validate_max(self, max_value: Any, field: Any, value: Any) -> None: ...
    def _validate_min(self, min_value: Any, field: Any, value: Any) -> None: ...
    def _validate_maxlength(self, max_length: Any, field: Any, value: Any) -> None: ...
    def _validate_minlength(self, min_length: Any, field: Any, value: Any) -> None: ...
    def _validate_meta(self, constraint: Any, field: Any, value: Any) -> NoReturn: ...
    def _validate_nullable(self, nullable: Any, field: Any, value: Any) -> None: ...
    def _validate_keysrules(self, schema: Any, field: Any, value: Any) -> None: ...
    def _validate_readonly(
        self, readonly: Any, field: Any, value: Any
    ) -> bool | None: ...
    def _validate_regex(self, pattern: Any, field: Any, value: Any) -> None: ...
    def _validate_required(
        self, constraint: Any, field: Any, value: Any
    ) -> NoReturn: ...
    def _validate_require_all(
        self, constraint: Any, field: Any, value: Any
    ) -> NoReturn: ...
    def _validate_schema(self, schema: Any, field: Any, value: Any) -> None: ...
    def _validate_type(self, data_type: Any, field: Any, value: Any) -> None: ...
    def _validate_valuesrules(self, schema: Any, field: Any, value: Any) -> None: ...

class InspectedValidator(type):
    def __new__(
        cls: type[_T], name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> _T: ...
    def __init__(
        cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> None: ...

class Validator(BareValidator, metaclass=InspectedValidator):
    # The metaclass collects the following attributes from the methods of a class
    # that follow the naming conventions for rules, type checkers and normalizers.
    _types_from_methods: ClassVar[tuple[str, ...]]
    validation_rules: ClassVar[dict[str, dict[Any, Any]]]
    checkers: ClassVar[tuple[str, ...]]
    coercers: ClassVar[tuple[str, ...]]
    default_setters: ClassVar[tuple[str, ...]]
    normalization_rules: ClassVar[dict[str, dict[Any, Any]]]
    rules: ClassVar[dict[str, dict[Any, Any]]]
