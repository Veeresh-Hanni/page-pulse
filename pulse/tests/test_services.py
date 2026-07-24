from django.test import SimpleTestCase

from pulse.services import parse_html_metrics


class ParseHtmlMetricsTests(SimpleTestCase):
    def test_happy_path_parses_expected_metrics(self):
        html = """
        <html>
          <head>
            <title>Sample Page</title>
            <meta name="description" content="A sample description">
          </head>
          <body>
            <h1>Main Heading</h1>
            <h1>Another Heading</h1>
            <p>This is a short paragraph with seven words.</p>
            <img src="/a.png" alt="">
            <img src="/b.png" alt="Logo">
            <img src="/c.png">
          </body>
        </html>
        """
        metrics = parse_html_metrics(html)

        self.assertEqual(metrics["page_title"], "Sample Page")
        self.assertEqual(metrics["meta_description"], "A sample description")
        self.assertEqual(metrics["h1_count"], 2)
        self.assertEqual(metrics["images_missing_alt"], 2)
        self.assertGreater(metrics["approx_word_count"], 0)

    def test_raises_type_error_when_html_is_not_string(self):
        with self.assertRaises(TypeError):
            parse_html_metrics(None)  # type: ignore[arg-type]

    def test_raises_value_error_when_html_is_empty(self):
        with self.assertRaises(ValueError):
            parse_html_metrics("   ")
