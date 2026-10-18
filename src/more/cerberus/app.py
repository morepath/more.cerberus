from __future__ import annotations

from typing import TYPE_CHECKING, Any

import morepath

from .error import ValidationError

if TYPE_CHECKING:
    from morepath import Request, Response


class App(morepath.App):
    pass


@App.json(model=ValidationError)
def validation_error_default(self: ValidationError, request: Request) -> dict[str, Any]:
    @request.after
    def adjust_status(response: Response) -> None:
        response.status = 422

    return self.errors
