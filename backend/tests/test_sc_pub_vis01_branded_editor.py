"""SC-PUB-VIS-01 — branded, revision-bound publishing on existing Workspace."""
import importlib
from io import BytesIO
from pathlib import Path
import unittest

pub = importlib.import_module('app.reporting_publication')


class BrandedPublicationTests(unittest.TestCase):
    def setUp(self):
        self.sample = {
            'title': 'Wexford ERW — Independent Research',
            'revision': 2,
            'markdown': '## Methods\n\nA verified source is required for publication.',
            'markdownSHA256': 'a' * 64,
            'publicationType': 'policy-brief',
        }

    def test_type_is_saved_and_invalid_types_refused(self):
        from pydantic import ValidationError
        row = pub.Draft.model_validate({
            'title': 'A report',
            'markdown': '## Introduction\n\nText',
            'publicationType': 'policy-brief',
        })
        self.assertEqual(row.publicationType, 'policy-brief')
        self.assertEqual(pub.Draft.model_validate({
            'title': 'Legacy', 'markdown': '# Methods'}).publicationType, 'report')
        with self.assertRaises(ValidationError):
            pub.Draft.model_validate({
                'title': 'A report', 'markdown': 'Text', 'publicationType': 'secret',
            })

    def test_html_branding_and_provenance_are_escaped(self):
        sample = {**self.sample, 'title': '<script>alert(1)</script>'}
        html = pub._as_html(sample).decode()
        self.assertIn('SUSTAINABLE CATALYST', html)
        self.assertIn('INDEPENDENT RESEARCH / Policy Brief', html)
        self.assertIn('SHA-256 ' + 'a'*64, html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)

    def test_docx_branding(self):
        from docx import Document
        data = pub._docx(self.sample, {})
        doc = Document(BytesIO(data))
        self.assertIn('SUSTAINABLE CATALYST', doc.sections[0].header.paragraphs[0].text)
        self.assertIn('Policy Brief', doc.sections[0].footer.paragraphs[0].text)
        self.assertTrue(any('Wexford ERW' in p.text for p in doc.paragraphs))

    def test_pdf_branding_and_basic_export(self):
        data = pub._pdf(self.sample, {})
        self.assertTrue(data.startswith(b'%PDF'))
        self.assertGreater(len(data), 2000)

    def test_visual_script_is_loaded_with_existing_csp_hash(self):
        source = Path(pub.__file__).read_text()
        self.assertIn("reporting_publication_visual.js", source)
        self.assertIn("script_hash=base64.b64encode", source)
        html = Path(pub.__file__).with_name('reporting_publication_ui.html').read_text()
        self.assertIn('id="publicationType"', html)
        self.assertIn('id="visualBlocks"', html)


if __name__ == '__main__':
    unittest.main()
