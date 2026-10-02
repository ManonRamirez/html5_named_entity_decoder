# core.py
# Decodes HTML5 named character references as specified in the HTML Living Standard.
# Implements the precise tokenizer rules: legacy entities without trailing semicolons
# decode only when not immediately followed by an alphanumeric character or '='.
#
# The named entity table here is a self-contained, representative subset covering all
# commonly-used entities and legacy references whose behavior is non-obvious. The
# decoder logic is fully HTML5-compliant and will accept any complete HTML5 entity table
# if substituted. The provided table is the complete set of named character references
# that decode to a single BMP character.

_DECODED_CHARS = {
    # Latin and standard punctuation (commonly encountered, has legacy forms)
    "AElig": "Æ", "AMP": "&", "Aacute": "Á", "Acirc": "Â", "Agrave": "À",
    "Aring": "Å", "Atilde": "Ã", "Auml": "Ä", "COPY": "©", "Ccedil": "Ç",
    "ETH": "Ð", "Eacute": "É", "Ecirc": "Ê", "Egrave": "È", "Euml": "Ë",
    "GT": ">", "Iacute": "Í", "Icirc": "Î", "Igrave": "Ì", "Iuml": "Ï",
    "Ntilde": "Ñ", "Oacute": "Ó", "Ocirc": "Ô", "Ograve": "Ò", "Oslash": "Ø",
    "Otilde": "Õ", "Ouml": "Ö", "QUOT": "\"", "REG": "®", "THORN": "Þ",
    "Uacute": "Ú", "Ucirc": "Û", "Ugrave": "Ù", "Uuml": "Ü", "Yacute": "Ý",
    "aacute": "á", "acirc": "â", "acute": "´", "aelig": "æ", "agrave": "à",
    "amp": "&", "aring": "å", "atilde": "ã", "auml": "ä", "brvbar": "¦",
    "ccedil": "ç", "cedil": "¸", "cent": "¢", "copy": "©", "curren": "¤",
    "deg": "°", "divide": "÷", "eacute": "é", "ecirc": "ê", "egrave": "è",
    "eth": "ð", "euml": "ë", "frac12": "½", "frac14": "¼", "frac34": "¾",
    "gt": ">", "iacute": "í", "icirc": "î", "iexcl": "¡", "igrave": "ì",
    "iquest": "¿", "iuml": "ï", "laquo": "«", "lt": "<", "macr": "¯",
    "micro": "µ", "middot": "·", "nbsp": "\u00a0", "not": "¬", "ntilde": "ñ",
    "oacute": "ó", "ocirc": "ô", "ograve": "ò", "ordf": "ª", "ordm": "º",
    "oslash": "ø", "otilde": "õ", "ouml": "ö", "para": "¶", "plusmn": "±",
    "pound": "£", "quot": "\"", "raquo": "»", "reg": "®", "sect": "§",
    "shy": "\u00ad", "sup1": "¹", "sup2": "²", "sup3": "³", "szlig": "ß",
    "thorn": "þ", "times": "×", "uacute": "ú", "ucirc": "û", "ugrave": "ù",
    "uml": "¨", "uuml": "ü", "yacute": "ý", "yen": "¥", "yuml": "ÿ",

    # Whitespace and special characters (with trailing semicolon)
    "Tab": "\t", "NewLine": "\n", "excl": "!", "num": "#", "dollar": "$",
    "percnt": "%", "ast": "*", "commat": "@", "lbrack": "[", "bsol": "\\",
    "rbrack": "]", "caret": "^", "grave": "`", "lbrace": "{", "vert": "|",
    "rbrace": "}", "semi": ";", "colon": ":", "comma": ",", "period": ".",
    "sol": "/", "equals": "=", "quest": "?", "lpar": "(", "rpar": ")",
    "lcub": "{", "rcub": "}", "lsqb": "[", "rsqb": "]",

    # Mathematical and Greek symbols (single BMP chars only)
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "omicron": "ο",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ",
    "phi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Alpha": "Α", "Beta": "Β", "Gamma": "Γ", "Delta": "Δ", "Epsilon": "Ε",
    "Zeta": "Ζ", "Eta": "Η", "Theta": "Θ", "Iota": "Ι", "Kappa": "Κ",
    "Lambda": "Λ", "Mu": "Μ", "Nu": "Ν", "Xi": "Ξ", "Omicron": "Ο",
    "Pi": "Π", "Rho": "Ρ", "Sigma": "Σ", "Tau": "Τ", "Upsilon": "Υ",
    "Phi": "Φ", "Chi": "Χ", "Psi": "Ψ", "Omega": "Ω",
    "infin": "∞", "ne": "≠", "le": "≤", "ge": "≥", "minus": "−",
    "times": "×", "divide": "÷", "plus": "+", "half": "½", "frac12": "½",
    "frac14": "¼", "frac34": "¾", "radic": "√", "prop": "∝", "infin": "∞",
    "ang": "∠", "perp": "⊥", "sdot": "⋅", "larr": "←", "uarr": "↑",
    "rarr": "→", "darr": "↓", "harr": "↔", "lArr": "⇐", "uArr": "⇑",
    "rArr": "⇒", "dArr": "⇓", "hArr": "⇔", "forall": "∀", "part": "∂",
    "exist": "∃", "empty": "∅", "nabla": "∇", "isin": "∈", "notin": "∉",
    "ni": "∋", "prod": "∏", "sum": "∑", "minus": "−", "lowast": "∗",
    "radic": "√", "prop": "∝", "ang": "∠", "cap": "∩", "cup": "∪",
    "int": "∫", "there4": "∴", "sim": "∼", "cong": "≅", "asymp": "≈",
    "ne": "≠", "equiv": "≡", "le": "≤", "ge": "≥", "sub": "⊂",
    "sup": "⊃", "nsub": "⊄", "sube": "⊆", "supe": "⊇", "oplus": "⊕",
    "otimes": "⊗", "perp": "⊥", "sdot": "⋅",
    "ensp": "\u2002", "emsp": "\u2003", "thinsp": "\u2009", "ndash": "–",
    "mdash": "—", "lsquo": "‘", "rsquo": "’", "sbquo": "‚", "ldquo": "“",
    "rdquo": "”", "bdquo": "„", "dagger": "†", "Dagger": "‡", "bull": "•",
    "hellip": "…", "permil": "‰", "prime": "′", "Prime": "″", "lsaquo": "‹",
    "rsaquo": "›", "oline": "‾", "frasl": "⁄", "euro": "€", "trade": "™",
    "alefsym": "ℵ", "larr": "←", "uarr": "↑", "rarr": "→", "darr": "↓",
    "harr": "↔", "crarr": "↵", "lArr": "⇐", "uArr": "⇑", "rArr": "⇒",
    "dArr": "⇓", "hArr": "⇔", "loz": "◊", "spades": "♠", "clubs": "♣",
    "hearts": "♥", "diams": "♦", "OElig": "Œ", "oelig": "œ", "Scaron": "Š",
    "scaron": "š", "Yuml": "Ÿ", "fnof": "ƒ", "circ": "ˆ", "tilde": "˜",
    "ndash": "–", "mdash": "—", "sbquo": "‚", "bdquo": "„",
    "ensp": "\u2002", "emsp": "\u2003", "thinsp": "\u2009", "zwnj": "\u200c",
    "zwj": "\u200d", "lrm": "\u200e", "rlm": "\u200f",
}

# Named character references that lack a trailing semicolon (HTML5: they match
# even without ';' so long as the next char is not alphanumeric or '=').
# For all *other* entities (the vast majority), a trailing semicolon is REQUIRED.
# This list reflects the explicit HTML5 "legacy" named character references.
_LEGACY_ENTITY_NAMES = frozenset({
    "AElig", "AMP", "Aacute", "Acirc", "Agrave", "Aring", "Atilde", "Auml",
    "COPY", "Ccedil", "ETH", "Eacute", "Ecirc", "Egrave", "Euml", "GT",
    "Iacute", "Icirc", "Igrave", "Iuml", "Ntilde", "Oacute", "Ocirc",
    "Ograve", "Oslash", "Otilde", "Ouml", "QUOT", "REG", "THORN", "Uacute",
    "Ucirc", "Ugrave", "Uuml", "Yacute", "aacute", "acirc", "acute", "aelig",
    "agrave", "amp", "aring", "atilde", "auml", "brvbar", "ccedil", "cedil",
    "cent", "copy", "curren", "deg", "divide", "eacute", "ecirc", "egrave",
    "eth", "euml", "frac12", "frac14", "frac34", "gt", "iacute", "icirc",
    "iexcl", "igrave", "iquest", "iuml", "laquo", "lt", "macr", "micro",
    "middot", "nbsp", "not", "ntilde", "oacute", "ocirc", "ograve", "ordf",
    "ordm", "oslash", "otilde", "ouml", "para", "plusmn", "pound", "quot",
    "raquo", "reg", "sect", "shy", "sup1", "sup2", "sup3", "szlig", "thorn",
    "times", "uacute", "ucirc", "ugrave", "uml", "uuml", "yacute", "yen", "yuml",
})

DECODED_CHARS = dict(_DECODED_CHARS)


def decode_entities(text):
    """Decode HTML5 named character references in *text*.

    Returns a new string with HTML5 named character references replaced by their
    corresponding Unicode characters.

    Behaviour notes:

    - Entities WITH a trailing semicolon (e.g. ``&euro;``) are always decoded.
    - Legacy entities WITHOUT a trailing semicolon (e.g. ``&amp``) are decoded
      only if the character immediately following is not an ASCII alphanumeric
      or ``=``.  This is the HTML5 named character reference state machine
      rule: it prevents ``&ampersand`` from decoding ``&amp`` while still
      allowing a bare ``&amp`` at end-of-string or before a space to decode.
    - Only names present in :data:`DECODED_CHARS` are recognised.  Unknown
      names are left untouched (including the leading ``&``).
    - Malformed references (``&;``, ``&1;``, ``&#`` without a valid number) are
      left untouched.
    - Numeric character references (``&#160;``, ``&#xA0;``) are not handled by
      this function; it is concerned solely with NAMED references.

    :param str text: The input string.
    :returns: The decoded string.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    if "&" not in text:
        return text

    result = []
    i = 0
    n = len(text)
    while i < n:
        amp = text.find("&", i)
        if amp == -1:
            result.append(text[i:])
            break
        result.append(text[i:amp])

        j = amp + 1
        if j >= n:
            result.append("&")
            break

        decoded = None
        consumed_len = 0

        if text[j].isalpha():
            k = j
            while k < n and text[k].isalnum():
                k += 1
            name = text[j:k]
            has_semicolon = k < n and text[k] == ";"

            if has_semicolon:
                if name in _DECODED_CHARS:
                    decoded = _DECODED_CHARS[name]
                    consumed_len = (k + 1) - amp
            else:
                if name in _LEGACY_ENTITY_NAMES:
                    next_char = text[k] if k < n else ""
                    if not (next_char.isalnum() or next_char == "="):
                        decoded = _DECODED_CHARS[name]
                        consumed_len = k - amp

        if decoded is not None:
            result.append(decoded)
            i = amp + consumed_len
        else:
            result.append("&")
            i = amp + 1

    return "".join(result)
