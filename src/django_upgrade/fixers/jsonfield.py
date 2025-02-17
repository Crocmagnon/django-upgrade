"""
Replace JSONField imports:
https://docs.djangoproject.com/en/3.1/releases/3.1/#features-deprecated-in-3-1
"""
from __future__ import annotations

import ast
from functools import partial
from typing import Iterable

from tokenize_rt import Offset

from django_upgrade.ast import ast_start_offset, is_rewritable_import_from
from django_upgrade.data import Fixer, State, TokenFunc
from django_upgrade.tokens import update_import_modules

fixer = Fixer(
    __name__,
    min_version=(3, 1),
)

REWRITES = {
    "django.contrib.postgres.fields": {
        "JSONField": "django.db.models",
        "KeyTextTransform": "django.db.models.fields.json",
        "KeyTransform": "django.db.models.fields.json",
    },
    "django.contrib.postgres.fields.jsonb": {
        "JSONField": "django.db.models",
        "KeyTextTransform": "django.db.models.fields.json",
        "KeyTransform": "django.db.models.fields.json",
    },
    "django.contrib.postgres.forms": {
        "JSONField": "django.forms",
    },
    "django.contrib.postgres.forms.jsonb": {
        "JSONField": "django.forms",
    },
}


@fixer.register(ast.ImportFrom)
def visit_ImportFrom(
    state: State,
    node: ast.ImportFrom,
    parents: list[ast.AST],
) -> Iterable[tuple[Offset, TokenFunc]]:
    if (
        node.module in REWRITES
        and not state.looks_like_migrations_file()
        and is_rewritable_import_from(node)
        and any(alias.name in REWRITES[node.module] for alias in node.names)
    ):
        yield ast_start_offset(node), partial(
            update_import_modules, node=node, module_rewrites=REWRITES[node.module]
        )
