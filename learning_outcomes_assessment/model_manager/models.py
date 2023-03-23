from django.db import models
from django.db.models import F, Value, IntegerField, TextField
from django.contrib.postgres.fields import ArrayField
from django.db.models.expressions import Func
from django.db.models.functions import Cast


class TextNumberModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            number = Cast(
                Func(
                    F('nama'),
                    Value(r'\d+'),  # Not digit
                    function='regexp_matches',
                ),
                output_field=ArrayField(IntegerField())
            ),
            char = Func(
                F('nama'),
                Value(r'\D+'),  # Digit
                function='regexp_matches',
                output_field=ArrayField(TextField())
            ),
        ).order_by('char', 'number')
