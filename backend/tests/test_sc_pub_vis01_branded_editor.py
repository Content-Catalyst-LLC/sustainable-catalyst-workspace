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
        self.assertGreater(len(data), 1000)
        self.assertIn(b'%%EOF', data[-200:])

    def test_pdf_svg_clip_path_survives_as_bounded_raster(self):
        # Synthetic Matplotlib-style clipped axes, no real research assets.
        from fastapi import HTTPException
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" '
               b'width="600pt" height="300pt" viewBox="0 0 600 300">'
               b'<rect width="600" height="300" fill="#ffffff"/>'
               b'<defs><clipPath id="axes"><rect x="40" y="30" width="500" height="220"/></clipPath></defs>'
               b'<g clip-path="url(#axes)">'
               b'<rect x="50" y="40" width="300" height="170" fill="#b00020"/>'
               b'<path d="M40 240 L180 65 L520 100" stroke="#15633e" stroke-width="9" fill="none"/>'
               b'</g><text x="80" y="270" font-size="20">SDG heatmap</text></svg>')
        figure = pub._pdf_svg_image(svg)
        self.assertGreater(figure.imageWidth, 1000)
        self.assertLessEqual(figure.imageWidth, 1230)
        self.assertLessEqual(figure.imageHeight, 1125)
        self.assertAlmostEqual(figure.drawWidth / figure.drawHeight, 2.0, places=2)

        # Raster must contain ink from the clipped plot; an all-white SVG
        # would otherwise pass a superficial PDF file-signature check.
        pixels = figure._img.getRGBData()
        non_white = sum(1 for i in range(0, len(pixels), 3)
                        if min(pixels[i:i + 3]) < 200)
        self.assertGreater(non_white, 10000)
        marked = {**self.sample,
                  'markdown': '## Figure\\n\\n![Synthetic chart](asset:chart)'}
        pdf = pub._pdf(marked, {'chart': svg})
        self.assertIn(b'/Subtype /Image', pdf)
        self.assertIn(b'%%EOF', pdf[-200:])

    def test_pdf_svg_validates_dimensions_and_fails_closed(self):
        from fastapi import HTTPException
        from unittest.mock import patch
        good = (b'<svg xmlns="http://www.w3.org/2000/svg" width="200pt" height="100pt">'
                b'<rect width="200" height="100" fill="#b00020"/></svg>')
        self.assertAlmostEqual(pub._pdf_svg_image(good).drawWidth /
                               pub._pdf_svg_image(good).drawHeight, 2.0, places=2)
        invalid = (b'<svg xmlns="http://www.w3.org/2000/svg" width="0" height="100">'
                   b'<rect width="1" height="10"/></svg>')
        with self.assertRaises(HTTPException) as ctx:
            pub._pdf_svg_image(invalid)
        self.assertEqual(ctx.exception.status_code, 422)
        # No fallback to a blank figure when raster conversion fails.
        with patch('cairosvg.svg2png', side_effect=ValueError('private source details')):
            with self.assertRaises(HTTPException) as ctx:
                pub._pdf({**self.sample,
                          'markdown': '![Synthetic chart](asset:chart)'},
                         {'chart': good})
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertNotIn('private source details', str(ctx.exception.detail))

    def test_visual_script_is_loaded_with_existing_csp_hash(self):
        source = Path(pub.__file__).read_text()
        self.assertIn("reporting_publication_visual.js", source)
        self.assertIn("script_hash=base64.b64encode", source)
        html = Path(pub.__file__).with_name('reporting_publication_ui.html').read_text()
        self.assertIn('id="publicationType"', html)
        self.assertIn('id="visualBlocks"', html)


if __name__ == '__main__':
    unittest.main()
