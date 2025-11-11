# Features Overview

This page showcases various MkDocs features.

## Superfences Test

```python title="example.py"
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

# Usage
message = greet("World")
print(message)
```

## Tables with Caption

| Column A | Column B | Column C |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Value X  | Value Y  | Value Z  |

^Table 1: Sample data table^

## Extended Table Features

Testing `markdown_tables_extended`:

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Span across columns ||

## Navigation Links

- [Home](../index.md)
- [Getting Started](../getting-started.md)
- [Advanced Features](advanced.md)
- [API Reference](../api.md)

## Attributes Test

This paragraph has attributes.
{: .custom-class }

[Click here](#features-overview){: .button }
