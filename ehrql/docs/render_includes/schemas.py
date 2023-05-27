SCHEMA_INDEX_TEMPLATE = """\
## [{name}](./{name}/)
<small class="subtitle">
  <a href="./{name}/"> view details → </a>
</small>

{implemented_by_list}

{docstring}
"""


def render_schema_index(schemas):
    return "\n".join(
        SCHEMA_INDEX_TEMPLATE.format(
            **schema,
            implemented_by_list=implemented_by_list(schema["implemented_by"], depth=1),
        )
        for schema in schemas
    )


def implemented_by_list(backends, depth=1):
    if not backends:
        return (
            "_This schema is for development or testing purposes and is not"
            " available on any backend._"
        )
    url_prefix = "/".join([".."] * depth)
    backend_links = [
        f"[**{backend}**]({url_prefix}/backends#{backend.lower()})"
        for backend in backends
    ]
    return f"Available on backends: {', '.join(backend_links)}"


SCHEMA_TEMPLATE = """\
# <strong>{name}</strong> schema

{implemented_by_list}

{docstring}

``` {{.python .copy title='To use this schema in an ehrQL file:'}}
from {dotted_path} import (
{table_imports}
)
```

{table_descriptions}
"""


def render_schema(schema):
    return SCHEMA_TEMPLATE.format(
        **schema,
        implemented_by_list=implemented_by_list(schema["implemented_by"], depth=2),
        table_imports=table_imports(schema["tables"]),
        table_descriptions=table_descriptions(schema["tables"]),
    )


def table_imports(tables):
    return "\n".join(f"    {table['name']}," for table in tables)


TABLE_TEMPLATE = """\
<p class="dimension-indicator"><code>{dimension}</code></p>
## {name}

{docstring}

<dl markdown="block" class="schema-column-list">
{column_descriptions}
</dl>
"""


def table_descriptions(tables):
    return "\n".join(
        TABLE_TEMPLATE.format(
            **table,
            column_descriptions=column_descriptions(table["name"], table["columns"]),
            dimension=(
                "one row per patient"
                if table["has_one_row_per_patient"]
                else "many rows per patient"
            ),
        )
        for table in tables
    )


COLUMN_TEMPLATE = """\
<div markdown="block">
  <dt id="{column_id}">
    <strong>{name}</strong>
    <a class="headerlink" href="#{column_id}" title="Permanent link">🔗</a>
    <code>{type}</code>
  </dt>
  <dd markdown="block">
    {description_with_constraints}
  </dd>
</div>
"""


def column_descriptions(table_name, columns):
    return "\n".join(
        COLUMN_TEMPLATE.format(
            **column,
            column_id=f"{table_name}.{column['name']}",
            description_with_constraints=description_with_constraints(column),
        )
        for column in columns
    )


def description_with_constraints(column):
    return "\n".join(
        [column["description"], "", *[f" * {c}" for c in column["constraints"]]]
    )
