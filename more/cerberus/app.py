import morepath
from .error import ValidationError


class App(morepath.App):
    pass


@App.json(model=ValidationError)
def validation_error_default(self, request):
    @request.after
    def adjust_status(response):
        response.status = 422
    return self.errors
