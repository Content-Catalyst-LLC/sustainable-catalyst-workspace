"""Validate declared categorical labels and uncertainty; never verify source truth."""
from copy import deepcopy
import math
from fastapi import HTTPException


def scientific_metadata(obj, unit):
    labels = obj.get('axisLabels')
    if labels is not None:
        if not isinstance(labels, dict) or set(labels) != {'x', 'y'} or obj.get('spatialReference'):
            raise HTTPException(422, 'Categorical axes require x/y labels and cannot declare a CRS.')
        for key, values in [('x', obj['xValues']), ('y', obj['yValues'])]:
            entries = labels[key]
            if (not isinstance(entries, list) or len(entries) != len(values)
                    or any(not isinstance(v, str) or not v.strip() or len(v) > 80 for v in entries)
                    or len(set(entries)) != len(entries) or len(entries) > 12
                    or values != list(range(len(entries)))):
                raise HTTPException(422, 'Categorical axes need unique labels and ordinal centers 0..n-1 (at most 12).')
    context = obj.get('scientificContext')
    errors = [c.get('standardError') for c in obj['cells']]
    if context is None:
        if any(e is not None for e in errors):
            raise HTTPException(422, 'Standard errors require declared scientific context and units.')
        return deepcopy(labels), None
    if not isinstance(context, dict) or context.get('unit') != unit:
        raise HTTPException(422, 'Scientific source unit must match the requested heatmap unit.')
    if context.get('uncertainty_kind') != 'SE':
        raise HTTPException(422, 'This adapter supports explicitly reported standard errors only, not inferred intervals.')
    if any(type(e) not in (int, float) or not math.isfinite(e) or e < 0 for e in errors):
        raise HTTPException(422, 'Every scientific cell requires a finite, nonnegative standard error.')
    if context.get('depth_semantics') not in ('cumulative', 'not-applicable'):
        raise HTTPException(422, 'Declare cumulative depth semantics or not-applicable.')
    for key, limit in [('warning', 300), ('status', 80)]:
        if not isinstance(context.get(key), str) or not 1 <= len(context[key]) <= limit:
            raise HTTPException(422, 'Scientific context requires bounded status and warning text.')
    source = context.get('source')
    if not isinstance(source, dict) or not isinstance(source.get('citation'), str) or not 1 <= len(source['citation']) <= 1200:
        raise HTTPException(422, 'Scientific context requires a source citation.')
    if not isinstance(source.get('url'), str) or not source['url'].startswith('https://') or len(source['url']) > 2000:
        raise HTTPException(422, 'Source must declare an HTTPS URL (never fetched by this adapter).')
    digest = source.get('sha256')
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise HTTPException(422, 'Declare the original source SHA256, distinct from figure bytes.')
    if context['depth_semantics'] == 'cumulative' and not labels:
        raise HTTPException(422, 'Cumulative depths require explicit category labels; no depth interpolation.')
    return deepcopy(labels), deepcopy(context)
