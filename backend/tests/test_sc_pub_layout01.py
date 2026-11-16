"""SC-PUB-LAYOUT-01: immutable scientific manuscript layout and figure placement.

No database, private source file, or production service is touched by these tests.
"""
from __future__ import annotations

import hashlib
from io import BytesIO
import importlib
import unittest

from app import publication_layout as layout

pub = importlib.import_module('app.reporting_publication')


class LayoutAuditTests(unittest.TestCase):
    def setUp(self):
        self.sample = (
            '# Metrics of Sustainable Development\n\n'
            'Introduction text.\n\n'
            '## Human Development Index\n\n'
            '[FIGURE_HDI]\n\n'
            '## Index comparisons\n\n'
            '[FIGURE_RANK]\n\n'
            '## References\n\n'
            'Bibliography entry.\n\n'
            '![01 rank comparison](asset:rank-123)\n\n'
            '![01 rank comparison](asset:rank-123)\n'
        )
        self.title = 'Metrics of Sustainable Development'

    def test_audit_preserves_source_and_identifies_all_real_problems(self):
        before = self.sample.encode()
        report = layout.audit_layout(self.sample, self.title)
        self.assertEqual(report['status'], 'needs-attention')
        self.assertEqual(report['markdownSHA256'], hashlib.sha256(before).hexdigest())
        self.assertTrue(report['titleDeduplicatedInExport'])
        self.assertEqual(report['figureOccurrences'], 2)
        self.assertEqual(report['distinctFigureAssets'], 1)
        self.assertEqual([m['marker'] for m in report['markers']], ['FIGURE_HDI','FIGURE_RANK'])
        codes = [issue['code'] for issue in report['issues']]
        self.assertIn('repeated-document-title', codes)
        self.assertEqual(codes.count('unresolved-figure-marker'), 2)
        self.assertEqual(codes.count('figure-after-references'), 2)
        self.assertEqual(codes.count('repeated-figure-asset'), 1)
        self.assertEqual(self.sample.encode(),before)

    def test_explicit_move_collapses_only_selected_duplicates_in_draft(self):
        planned = layout.propose_figure_move(self.sample,'FIGURE_RANK','rank-123')
        source = planned['markdown']
        self.assertEqual(planned['movedExistingPlacements'],2)
        self.assertEqual(planned['removedDuplicatePlacements'],1)
        self.assertEqual(source.count('![01 rank comparison](asset:rank-123)'),1)
        self.assertIn('## Index comparisons\n\n![01 rank comparison](asset:rank-123)', source)
        self.assertIn('[FIGURE_HDI]',source)  # no HDI figure mapping invented
        self.assertNotIn('[FIGURE_RANK]',source)
        self.assertEqual(self.sample.count('![01 rank comparison](asset:rank-123)'),2)
        report = layout.audit_layout(source,self.title)
        self.assertEqual(len(report['figures']),1)
        self.assertFalse(any(x['code'] in ('repeated-figure-asset','figure-after-references')
                             for x in report['issues']))
        self.assertEqual(len(report['markers']),1)

    def test_move_no_existing_placement_requires_explicit_caption(self):
        source = '## Results\n\n[FIGURE_HDI]\n'
        with self.assertRaisesRegex(ValueError,'caption'):
            layout.propose_figure_move(source,'FIGURE_HDI','new-hdi')
        moved = layout.propose_figure_move(source,'FIGURE_HDI','new-hdi','HDI trend 1990-2023')
        self.assertEqual(moved['markdown'],'## Results\n\n![HDI trend 1990-2023](asset:new-hdi)\n')

    def test_duplicate_marker_conflicting_captions_and_missing_asset_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'exactly once'):
            layout.propose_figure_move('[FIGURE_HDI]\n[FIGURE_HDI]\n','FIGURE_HDI','rank-123','HDI')
        conflict = '[FIGURE_RANK]\n![One](asset:rank-123)\n![Two](asset:rank-123)\n'
        with self.assertRaisesRegex(ValueError,'conflicting captions'):
            layout.propose_figure_move(conflict,'FIGURE_RANK','rank-123')
        with self.assertRaisesRegex(ValueError,'valid figure asset'):
            layout.propose_figure_move('[FIGURE_RANK]\n','FIGURE_RANK','../../secrets','Figure')
        with self.assertRaisesRegex(ValueError,'once'):
            layout.propose_figure_move('No marker\n','FIGURE_RANK','rank-123','Figure')

    def test_moved_source_respects_crlf_and_does_not_interpret_code_or_math(self):
        source = (
            '## Figures\r\n'
            '```text\r\n[FIGURE_RANK]\r\n'
            '![Code image](asset:rank-123)\r\n```\r\n'
            '[FIGURE_RANK]\r\n'
            '$$\r\n![Equation image](asset:rank-123)\r\n$$\r\n'
            '![Actual figure](asset:rank-123)\r\n'
        )
        proposal = layout.propose_figure_move(source,'FIGURE_RANK','rank-123')
        self.assertIn('```text\r\n[FIGURE_RANK]\r\n',proposal['markdown'])
        self.assertIn('$$\r\n![Equation image](asset:rank-123)\r\n$$',proposal['markdown'])
        self.assertEqual(proposal['markdown'].count('![Actual figure](asset:rank-123)'),1)
        self.assertIn('[FIGURE_RANK]\r\n',proposal['markdown'])  # only the code block
        self.assertEqual(layout.audit_layout(proposal['markdown'],'Figures')['status'],'ready')

    def test_title_single_in_html_pdf_and_docx_with_original_markdown_unchanged(self):
        from docx import Document
        source = '# Metrics of Sustainable Development\n\n## Results\n\nThe SDG index.\n'
        snapshot = {
            'title':self.title, 'revision':3, 'markdown':source,
            'markdownSHA256':hashlib.sha256(source.encode()).hexdigest(),
            'publicationType':'report',
        }
        html=pub._as_html(snapshot).decode()
        self.assertEqual(html.count('<h1>Metrics of Sustainable Development</h1>'),1)
        docx=Document(BytesIO(pub._docx(snapshot,{})))
        self.assertEqual([p.text for p in docx.paragraphs].count(self.title),1)
        self.assertEqual(pub._publication_blocks(snapshot)[0]['text'],'Results')
        pdf=pub._pdf(snapshot,{})
        self.assertTrue(pdf.startswith(b'%PDF-'))
        self.assertEqual(snapshot['markdown'],source)
        self.assertEqual(snapshot['markdownSHA256'],hashlib.sha256(source.encode()).hexdigest())

    def test_render_html_default_compatibility_and_opt_in_dedup(self):
        source='# Example\n\nBody'
        default,_=pub.render_html(source)
        self.assertIn('<h1>Example</h1>',default)
        compact,_=pub.render_html(source,document_title='Example')
        self.assertNotIn('<h1>Example</h1>',compact)
        self.assertIn('<p>Body</p>',compact)
        distinct,_=pub.render_html(source,document_title='Different')
        self.assertIn('<h1>Example</h1>',distinct)

    def test_marker_does_not_automatically_map_semantically_similar_figures(self):
        text='[FIGURE_HDI]\n\n![HDI trends?](asset:rank-123)\n'
        report=layout.audit_layout(text,'Another study')
        self.assertEqual(report['markers'][0]['marker'],'FIGURE_HDI')
        self.assertEqual(report['figures'][0]['assetId'],'rank-123')
        self.assertEqual(report['status'],'needs-attention')


    def test_move_proposal_route_is_authenticated_project_gated_and_non_mutating(self):
        import json
        from contextlib import nullcontext
        from unittest.mock import patch
        source = '[FIGURE_RANK]\n\n![01 rank comparison](asset:rank-123)\n'
        body = pub.FigureMove.model_validate({
            'title': self.title, 'markdown': source, 'marker':'FIGURE_RANK',
            'assetId':'rank-123', 'expectedSHA256':hashlib.sha256(source.encode()).hexdigest(),
        })
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10" fill="#b00020"/></svg>'
        meta={'artifactId':'rank-123','filename':'ranking.svg','sha256':hashlib.sha256(svg).hexdigest()}
        with patch.object(pub,'_subject',return_value='owner') as subject, \
             patch.object(pub,'session_scope',return_value=nullcontext(object())), \
             patch.object(pub,'_project',return_value=object()) as project, \
             patch.object(pub,'_original_asset',return_value=(meta,svg)) as asset, \
             patch.object(pub,'_verify_figures',return_value=[meta]) as verify:
            response=pub.propose_layout_figure_move('owned-project',body,request=object())
        payload=json.loads(response.body)
        self.assertFalse(payload['saved'])
        self.assertFalse(payload['sourceModified'])
        self.assertEqual(payload['selectedFigure']['sha256'],meta['sha256'])
        self.assertEqual(payload['proposedMarkdown'].count('asset:rank-123'),1)
        subject.assert_called_once()
        project.assert_called_once()
        asset.assert_called_once()
        verify.assert_called_once()

    def test_move_proposal_refuses_stale_editor_and_foreign_project(self):
        from contextlib import nullcontext
        from fastapi import HTTPException
        from unittest.mock import patch
        source='[FIGURE_HDI]\n'
        kwargs={'title':'T','markdown':source,'marker':'FIGURE_HDI',
                'assetId':'hdi-chart','caption':'HDI 2026',
                'expectedSHA256':hashlib.sha256(b'different').hexdigest()}
        stale=pub.FigureMove.model_validate(kwargs)
        with patch.object(pub,'_subject',return_value='owner'), \
             patch.object(pub,'session_scope') as sessions:
            with self.assertRaises(HTTPException) as caught:
                pub.propose_layout_figure_move('project',stale,object())
            self.assertEqual(caught.exception.status_code,409)
            sessions.assert_not_called()

        valid=pub.FigureMove.model_validate({
            **kwargs, 'expectedSHA256':hashlib.sha256(source.encode()).hexdigest()
        })
        with patch.object(pub,'_subject',side_effect=HTTPException(401,'No valid session')), \
             patch.object(pub,'_original_asset') as asset:
            with self.assertRaises(HTTPException) as caught:
                pub.propose_layout_figure_move('foreign-project',valid,object())
            self.assertEqual(caught.exception.status_code,401)
            asset.assert_not_called()


if __name__ == '__main__':
    unittest.main()
