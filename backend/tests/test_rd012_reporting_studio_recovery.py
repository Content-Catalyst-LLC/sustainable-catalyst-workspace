"""RD-01.2 Reporting Studio, recovered from the deployed ``sc-reporting-rd012`` image into canonical Workspace.

Publication rendering, sanitisation, exports and save contracts (the RD-01.2 release tests, run against the real
Workspace modules), plus the integrated entrypoint: the Studio mounts beside, never instead of, the existing routes.
"""
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from fastapi import HTTPException

pub = importlib.import_module('app.reporting_publication')


class _Payload:
    @staticmethod
    def model_validate(data):
        return types.SimpleNamespace(data=data)


class PublicationTests(unittest.TestCase):
    def test_html_escaping_and_citations(self):
        source='# Results\n\n<script>alert(1)</script> **robust** [@UN2026]\n\n| Name | Count |\n|---|---|\n| SDG | 17 |'
        html,assets=pub.render_html(source)
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('<script>',html)
        self.assertIn('<strong>robust</strong>',html)
        self.assertIn('<table>',html)
        self.assertIn('class="citation"',html)
        self.assertEqual(assets,[])

    def test_figures_are_sanitized(self):
        bad=b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>alert(1)</script><rect width="20" height="20" fill="#abc"/><image href="https://evil.example/x"/></svg>'
        clean=pub.sanitize_svg(bad)
        self.assertNotIn(b'onload',clean)
        self.assertNotIn(b'script',clean)
        self.assertNotIn(b'https://evil',clean)
        self.assertIn(b'rect',clean)
        with self.assertRaises(HTTPException):pub.sanitize_svg(b'<!DOCTYPE svg><svg/>')

    def test_rich_blocks_and_reference_figure(self):
        md='## Methods\n\n$$\nE=mc^2\n$$\n\n![Rank comparison](asset:abc123)\n\n- x\n- y'
        html,ids=pub.render_html(md,lambda x:'/private/'+x+'/svg')
        self.assertEqual(ids,['abc123'])
        self.assertIn('src="/private/abc123/svg"',html)
        self.assertIn('equation',html)
        self.assertIn('<ul>',html)

    def test_immutable_publication_versions(self):
        a={'schema':pub.SCHEMA,'documentId':'publication-abc','revision':1,
           'title':'M','markdown':'first','createdAt':'now','projectRevision':2}
        b={**a,'revision':2,'markdown':'second','projectRevision':3}
        pack={'project':{'objects':[{'id':'s1','type':'scientific-publication','publication':a},
                                    {'id':'s2','type':'scientific-publication','publication':b}]}}
        self.assertEqual(len(pub.snapshots(pack,'publication-abc')),2)
        self.assertEqual(pub.latest_documents(pack)[0]['revision'],2)
        self.assertEqual(pub.snapshots(pack,'unknown'),[])

    def test_docx_text_is_read_only_extraction(self):
        from docx import Document
        d=Document();d.add_heading('Metrics of Sustainable Development',1)
        d.add_paragraph('The source is preserved.')
        data=io.BytesIO();d.save(data)
        markdown=pub.docx_to_markdown(data.getvalue())
        self.assertIn('Metrics of Sustainable Development',markdown)
        self.assertIn('The source is preserved.',markdown)
        with self.assertRaises(HTTPException):pub.docx_to_markdown(b'not docx')

    def test_pdf_docx_html_exports_valid(self):
        md='# Executive summary\n\nThe **SDG** metrics report.\n\n| Area | Score |\n|---|---|\n| Social | 7 |\n\n- Data\n- Evidence'
        document={'title':'Metrics of Sustainable Development','markdown':md,
                  'revision':1,'markdownSHA256':hashlib.sha256(md.encode()).hexdigest()}
        html=pub._as_html(document)
        self.assertIn(b'<table>',html)
        pdf=pub._pdf(document,{})
        self.assertTrue(pdf.startswith(b'%PDF-'))
        docx=pub._docx(document,{})
        self.assertTrue(docx.startswith(b'PK'))
        from docx import Document
        d=Document(io.BytesIO(docx))
        self.assertIn('Metrics',d.paragraphs[0].text)

    def test_input_model_rejects_extra_fields_and_oversized(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):pub.Draft(title='T',markdown='ok',userKey='cross-owner')
        with self.assertRaises(ValidationError):pub.Draft(title='T',markdown='x'*(pub.MAX_MANUSCRIPT+1))

    def test_legacy_artifact_reads_verify_sha_and_project_scope(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            content=b'# Verified source\n\nOriginal manuscript is unchanged.'
            digest=hashlib.sha256(content).hexdigest()
            asset_dir=Path(directory)/'private-research'/digest[:2];asset_dir.mkdir(parents=True)
            (asset_dir/digest).write_bytes(content)
            source={'artifactId':'owned','filename':'research/final_manuscript.md',
                    'sha256':digest,'bytes':len(content)}
            with patch.object(pub,'get_settings',return_value=types.SimpleNamespace(object_storage_root=directory)),\
                 patch.object(pub,'read_legacy_artifacts',return_value=([source],True)):
                info,read=pub._original_asset(None,'actual-owner','actual-project','owned')
                self.assertEqual(read,content)
                self.assertEqual(info['sha256'],digest)
            with patch.object(pub,'read_legacy_artifacts',return_value=([],True)),\
                 patch.object(pub.object_store,'get_artifact',return_value=None,create=True):
                with self.assertRaises(HTTPException) as error:
                    pub._original_asset(None,'another-owner','another-project','owned')
                self.assertEqual(error.exception.status_code,404)
            (asset_dir/digest).write_bytes(b'TAMPERED')
            with patch.object(pub,'get_settings',return_value=types.SimpleNamespace(object_storage_root=directory)),\
                 patch.object(pub,'read_legacy_artifacts',return_value=([source],True)):
                with self.assertRaises(HTTPException) as error:
                    pub._original_asset(None,'actual-owner','actual-project','owned')
                self.assertEqual(error.exception.status_code,409)

    def test_svg_safe_style_preserves_plot_lines(self):
        raw=b'<svg xmlns="http://www.w3.org/2000/svg"><path style="fill:none;stroke:#aa1010;stroke-width:2" d="M 0 0 L 9 9"/><rect style="fill:url(javascript:alert(1))" width="10" height="10"/></svg>'
        safe=pub.sanitize_svg(raw)
        self.assertIn(b'#aa1010',safe)
        self.assertNotIn(b'javascript',safe)

    def test_save_revision_contract_does_not_mutate_original(self):
        class ProjectRow:
            revision=7; title='Metrics of Sustainable Development'
            package={'project':{'schema':'sc-workspace-project/20.0','title':title,
                                'objects':[{'id':'existing','type':'research-note'}]}}
        row=ProjectRow()
        before=json.dumps(row.package,sort_keys=True)
        class Store:
            payload=None
            @staticmethod
            def store_project(db,owner,payload):
                Store.payload=payload.data
                return types.SimpleNamespace(revision=8),False
            @staticmethod
            def project_metadata(x):return {'revision':x.revision}
        class FakeDB:
            def __enter__(self):return self
            def __exit__(self,*args):pass
        body=pub.Save(title='Metrics of Sustainable Development',markdown='# A real paper',
                      expectedProjectRevision=7)
        with patch.object(pub,'session_scope',return_value=FakeDB()),\
             patch.object(pub,'_subject',return_value='existing-owner'),\
             patch.object(pub,'_write',return_value=None),\
             patch.object(pub,'_locked_project',return_value=row),\
             patch.object(pub,'_source_meta',return_value=None),\
             patch.object(pub,'_verify_figures',return_value=[]),\
             patch.object(pub,'ProjectStoreRequest',_Payload),\
             patch.object(pub.repository,'store_project',Store.store_project),\
             patch.object(pub.repository,'project_metadata',Store.project_metadata):
            r=pub.save_document('existing-project',body,object())
        self.assertEqual(r.status_code,201)
        self.assertEqual(json.dumps(row.package,sort_keys=True),before)
        self.assertEqual(Store.payload['expectedRevision'],7)
        self.assertEqual(Store.payload['sourceProjectId'],'existing-project')
        self.assertEqual(Store.payload['project']['objects'][0]['id'],'existing')
        self.assertEqual(Store.payload['project']['objects'][1]['publication']['revision'],1)

    def test_update_replaces_live_head_preserving_canonical_history(self):
        ident='publication-'+'f'*32
        older={'schema':pub.SCHEMA,'documentId':ident,'revision':1,
               'title':'Metrics','markdown':'old manuscript','createdAt':'prior',
               'projectRevision':4,'source':None}
        row=types.SimpleNamespace(revision=4,title='Metrics',package={
            'project':{'schema':'sc-workspace-project/20.0','title':'Metrics',
                       'objects':[{'id':'publication-head-'+'f'*32,
                                   'type':'scientific-publication','publication':older}]}})
        captured={}
        def store(db,owner,payload):
            captured.update(payload.data)
            return types.SimpleNamespace(revision=5),False
        class FakeDB:
            def __enter__(self):return self
            def __exit__(self,*args):pass
        body=pub.Save(title='Metrics',markdown='revised manuscript',
                      expectedProjectRevision=4,documentId=ident,
                      expectedDocumentRevision=1)
        with patch.object(pub,'session_scope',return_value=FakeDB()),\
             patch.object(pub,'_subject',return_value='owner'),\
             patch.object(pub,'_write',return_value=None),\
             patch.object(pub,'_locked_project',return_value=row),\
             patch.object(pub,'_source_meta',return_value=None),\
             patch.object(pub,'_verify_figures',return_value=[]),\
             patch.object(pub,'ProjectStoreRequest',_Payload),\
             patch.object(pub.repository,'store_project',store,create=True),\
             patch.object(pub.repository,'project_metadata',lambda obj:{'revision':obj.revision},create=True):
             result=pub.save_document('existing-project',body,object())
        self.assertEqual(result.status_code,201)
        objects=captured['project']['objects']
        self.assertEqual(len(objects),1)
        self.assertEqual(objects[0]['publication']['revision'],2)
        self.assertEqual(objects[0]['publication']['markdown'],'revised manuscript')
        self.assertEqual(row.package['project']['objects'][0]['publication']['markdown'],'old manuscript')

    def test_save_rejects_stale_project_revision(self):
        row=types.SimpleNamespace(revision=5,title='X',package={'project':{'objects':[]}})
        class FakeDB:
            def __enter__(self):return self
            def __exit__(self,*args):pass
        with patch.object(pub,'session_scope',return_value=FakeDB()),\
             patch.object(pub,'_subject',return_value='owner'),\
             patch.object(pub,'_write',return_value=None),\
             patch.object(pub,'_locked_project',return_value=row),\
             patch.object(pub,'ProjectStoreRequest',_Payload):
            with self.assertRaises(HTTPException) as ctx:
                pub.save_document('project',pub.Save(title='X',markdown='abc',expectedProjectRevision=4),object())
        self.assertEqual(ctx.exception.status_code,409)




def _paths(app):
    return {getattr(r, "path", None) for r in app.router.routes}


def test_the_studio_mounts_beside_the_existing_workspace_routes(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_REPORTING_STUDIO_ENABLED", "1")
    for name in ("app.reporting_production_entry", "app.reporting_integrated_entry"):
        sys.modules.pop(name, None)
    entry = importlib.import_module("app.reporting_production_entry")
    paths = _paths(entry.app)
    studio = "/v1/private-research/reporting-studio"
    for route in ("", "/catalog/projects", "/catalog/projects/{project_id}", "/publication",
                  "/publication/projects/{project_id}/documents",
                  "/publication/projects/{project_id}/documents/{document_id}/export.{format}"):
        assert studio + route in paths, route
    # The production entrypoint drops only the developer docs; Notebook Desk, research access and sessions stay.
    assert "/docs" not in paths
    for kept in ("/v1/desk/notebooks", "/v1/research-access", "/v1/session", "/v1/private-research/ui"):
        assert any(p and p.startswith(kept) for p in paths), kept


def test_the_studio_refuses_anonymous_requests(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("SC_WORKSPACE_REPORTING_STUDIO_ENABLED", "1")
    from app.research_reporting import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    for path in ("/v1/private-research/reporting-studio/catalog/projects",
                 "/v1/private-research/reporting-studio/publication/projects/p/documents"):
        r = client.get(path)
        assert r.status_code == 401, (path, r.status_code)
    monkeypatch.setenv("SC_WORKSPACE_REPORTING_STUDIO_ENABLED", "0")
    assert client.get("/v1/private-research/reporting-studio/catalog/projects").status_code == 503
