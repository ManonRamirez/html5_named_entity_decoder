import unittest

from html5_named_entity_decoder import decode_entities, DECODED_CHARS


class TestDecodeEntities(unittest.TestCase):

    def test_empty_string(self):
        self.assertEqual(decode_entities(""), "")

    def test_no_entities(self):
        self.assertEqual(decode_entities("Hello World"), "Hello World")

    def test_no_ampersand(self):
        self.assertEqual(decode_entities("plain text"), "plain text")

    def test_basic_entity_with_semicolon(self):
        self.assertEqual(decode_entities("&euro;"), "€")

    def test_multiple_entities(self):
        self.assertEqual(decode_entities("&lt;&gt;&amp;"), "<>&")

    def test_mixed_text_and_entities(self):
        self.assertEqual(
            decode_entities("Price: &euro;5 &amp; &quot;free&quot;"),
            'Price: €5 & "free"',
        )

    def test_case_sensitive_named_entity(self):
        # Greek capital vs lowercase Omega differ only in case.
        self.assertEqual(decode_entities("&Omega;"), "Ω")
        self.assertEqual(decode_entities("&omega;"), "ω")
        self.assertNotEqual(decode_entities("&Omega;"), decode_entities("&omega;"))

    def test_known_entity_table_has_alpha_and_alpha_lowercase(self):
        # Sanity-check the table so the case-sensitivity test is meaningful.
        self.assertIn("alpha", DECODED_CHARS)
        self.assertEqual(DECODED_CHARS["alpha"], "α")

    def test_legacy_entity_without_semicolon_before_space(self):
        # &amp without ; is a legacy entity; before a space it decodes.
        self.assertEqual(decode_entities("Tom &amp Jerry"), "Tom & Jerry")

    def test_legacy_entity_without_semicolon_at_end_of_string(self):
        # At end of string there is no following alphanumeric char, so it decodes.
        self.assertEqual(decode_entities("Tom &amp"), "Tom &")

    def test_legacy_entity_without_semicolon_before_alphanumeric_is_not_decoded(self):
        # The HTML5 rule: legacy entity w/o ; must NOT decode if followed by
        # an alphanumeric character.  The & is preserved literally.
        self.assertEqual(decode_entities("&ampersand"), "&ampersand")

    def test_legacy_entity_without_semicolon_before_equals_is_not_decoded(self):
        # '=' is the other character that blocks legacy-entity decoding.
        self.assertEqual(decode_entities("x&amp=y"), "x&amp=y")

    def test_non_legacy_entity_without_semicolon_is_not_decoded(self):
        # euro is NOT a legacy entity, so it requires a trailing semicolon.
        self.assertEqual(decode_entities("&euro"), "&euro")

    def test_ampersand_alone_at_end(self):
        self.assertEqual(decode_entities("end &"), "end &")

    def test_ampersand_alone(self):
        self.assertEqual(decode_entities("&"), "&")

    def test_ampersand_followed_by_non_letter(self):
        # &123; does not start with a letter, so it is left untouched.
        self.assertEqual(decode_entities("&123;"), "&123;")

    def test_unknown_named_entity_with_semicolon(self):
        self.assertEqual(decode_entities("&notarealentity;"), "&notarealentity;")

    def test_unknown_named_entity_without_semicolon(self):
        self.assertEqual(decode_entities("&notarealentity end"), "&notarealentity end")

    def test_bare_ampersand_then_semicolon(self):
        self.assertEqual(decode_entities("&;"), "&;")

    def test_adjacent_entities(self):
        self.assertEqual(decode_entities("&amp;&amp;"), "&&")

    def test_nbsp_decodes_to_non_breaking_space(self):
        self.assertEqual(decode_entities("a&nbsp;b"), "a\u00a0b")

    def test_shy_decodes_to_soft_hyphen(self):
        self.assertEqual(decode_entities("word&shy;break"), "word\u00adbreak")

    def test_ampersand_in_url_like_text(self):
        # Common real-world string; both &copy and &#169 are distinct. We only
        # handle named references, so the numeric one is left alone.
        self.assertEqual(decode_entities("Copyright &copy &#169;"), "Copyright © &#169;")

    def test_copy_with_semicolon(self):
        self.assertEqual(decode_entities("&copy;"), "©")

    def test_copy_legacy_without_semicolon_at_end(self):
        self.assertEqual(decode_entities("&copy"), "©")

    def test_copy_legacy_without_semicolon_before_digit(self):
        # Followed by a digit -> not decoded.
        self.assertEqual(decode_entities("&copy2"), "&copy2")

    def test_type_error_on_non_string(self):
        with self.assertRaises(TypeError):
            decode_entities(123)


if __name__ == "__main__":
    unittest.main()
