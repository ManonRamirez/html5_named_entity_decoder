# HTML5 Named Entity Decoder
# Exports the public API of the library.

from .core import decode_entities, DECODED_CHARS

__all__ = ["decode_entities", "DECODED_CHARS"]
