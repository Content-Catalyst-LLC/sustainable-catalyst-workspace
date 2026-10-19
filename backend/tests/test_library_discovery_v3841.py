import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.library_discovery_v3841 import _fetch, _url, discover, verified_public_reference

ID = 'wordpress:1:post:8670'


def native_record(record_id=ID, *, status='published', visibility='public', content_hash='sha256:example'):
    return {
        'schema': 'sc-library-research-object/1.0',
        'identity': {'record_id': record_id, 'revision': 3, 'content_hash': content_hash},
        'descriptive': {'title': 'Ocean Chemistry and the Carbonate System', 'abstract': 'DO NOT LEAK'},
        'source': {'canonical_url': 'https://sustainablecatalyst.com/example/'},
        'publication': {'status': status, 'visibility': visibility},
        'content': {'body': 'SECRET NEVER OUTPUT'},
        'metadata': {'private_value': 'SECRET NEVER OUTPUT'},
    }


class DiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, SC_WORKSPACE_LIBRARY_PUBLIC_API_ORIGIN='https://library.sustainablecatalyst.com')
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def loader(self, url):
        path = unquote(urlsplit(url).path)
        if path.endswith('/search'):
            return {'schema': 'sc-library-api-page/1.0', 'items': [{'record_id': ID}, {'record_id': ID}, {'record_id': 'hidden'}]}
        if path.endswith('/' + ID):
            return native_record()
        return native_record('hidden', visibility='private')

    def test_search_dedup_and_public_check(self):
        result = discover('carbon', loader=self.loader)
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['items'][0]['libraryObjectId'], ID)
        self.assertNotIn('SECRET', str(result))
        self.assertNotIn('DO NOT LEAK', str(result))
        self.assertFalse(result['mutationPerformed'])

    def test_reference_not_accepted(self):
        ref = verified_public_reference(ID, loader=self.loader)
        self.assertFalse(ref['acceptedIntoProject'])
        self.assertTrue(ref['referenceOnly'])

    def test_identity_mismatch_rejected(self):
        with self.assertRaises(HTTPException):
            verified_public_reference(ID, loader=lambda _: native_record('wrong'))

    def test_unpublished_rejected(self):
        with self.assertRaises(HTTPException):
            verified_public_reference(ID, loader=lambda _: native_record(status='draft'))

    def test_private_rejected(self):
        with self.assertRaises(HTTPException):
            verified_public_reference(ID, loader=lambda _: native_record(visibility='private'))

    def test_missing_provenance_rejected(self):
        with self.assertRaises(HTTPException):
            verified_public_reference(ID, loader=lambda _: native_record(content_hash=''))

    def test_legacy_wrapper_rejected(self):
        with self.assertRaises(HTTPException):
            verified_public_reference(ID, loader=lambda _: {'item': {'id': ID}})

    def test_bad_record_id(self):
        with self.assertRaises(HTTPException):
            verified_public_reference('../bad', loader=self.loader)

    def test_untrusted_origin(self):
        with patch.dict(os.environ, SC_WORKSPACE_LIBRARY_PUBLIC_API_ORIGIN='http://127.0.0.1:1234'):
            with self.assertRaises(HTTPException):
                _url('/test')

    def test_disabled_by_default(self):
        os.environ.pop('SC_WORKSPACE_LIBRARY_PUBLIC_API_ORIGIN', None)
        with self.assertRaises(HTTPException):
            discover('carbon', loader=self.loader)

    def test_query_validation(self):
        with self.assertRaises(HTTPException):
            discover('x', loader=self.loader)

    def test_search_schema_mismatch(self):
        with self.assertRaises(HTTPException):
            discover('carbon', loader=lambda _: {'items': []})

    def test_oversized_response_without_content_length(self):
        class Response:
            status = 200
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, n): return b'x' * n
        class Opener:
            def open(self, request, timeout): return Response()
        with patch('app.library_discovery_v3841.build_opener', return_value=Opener()):
            with self.assertRaises(HTTPException) as raised:
                _fetch('/api/library/v1/search')
        self.assertEqual(raised.exception.status_code, 502)


if __name__ == '__main__':
    unittest.main()
