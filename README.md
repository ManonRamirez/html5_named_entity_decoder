# HTML5 Named Entity Decoder

Decodes HTML5 named character references (e.g. `&amp;`, `&copy;`, `&euro;`) into their
Unicode characters, including legacy entities that may appear without a trailing
semicolon.

## Usage

```python
from html5_named_entity_decoder import decode_entities

decode_entities("Tom &amp Jerry &lt;3 &euro;")
# -> 'Tom & Jerry <3 €'

decode_entities("&amp;copy;")
# -> '&copy;'
```

The library exports exactly two names:

- `decode_entities(text)` — returns the decoded string.
- `DECODED_CHARS` — a `dict` mapping supported entity names to their decoded
  characters.

## Why

HTML5 defines a named-character-reference state machine rather than a simple
`&name;` substitution. The awkward part is the legacy set (about 100 entities
like `&amp`, `&copy`, `&lt`) that decode *without* a trailing semicolon, but
only when the next character is not an ASCII alphanumeric or `=`. So `&amp`
decodes to `&`, but `&ampersand` stays literal. Most decoders either ignore the
legacy case entirely or over-decode it; this library implements the precise
HTML5 rule.

The entity table shipped here is a curated subset of the full HTML5 set covering
all named references that decode to a single BMP character (Latin-1 supplement,
Greek, math symbols, whitespace, punctuation, and the full legacy set). The
decoder logic itself is complete; substituting a larger `_DECODED_CHARS` table
would extend coverage without touching the parser.

## Edge cases you will hit

- **Numeric references are not handled.** `&#160;` and `&#xA0;` pass through
  unchanged. This library is only for named references.
- **Case matters.** `&Omega;` and `&omega;` are different characters.
- **Legacy without semicolon.** `&copy` decodes; `&copy2` does not.
