from django.db.models import Func


class Round(Func):
    # Used by django-admin-totals to round totals
    # https://stackoverflow.com/questions/13793759/django-orm-how-to-round-an-avg-result

    function = "ROUND"
    arity = 2
    # Only works as the arity is 2
    arg_joiner = "::numeric, "

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sqlite(compiler, connection, arg_joiner=", ", **extra_context)
