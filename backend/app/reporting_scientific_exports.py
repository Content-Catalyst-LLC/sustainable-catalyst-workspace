"""Export a saved scientific heatmap, never a newly computed figure.

DOCX retains the exact SVG and source JSON alongside a derived PNG for broad
Word compatibility. The editable table retains values and SE, not just pixels.
"""
import csv
from datetime import datetime
import hashlib
from io import BytesIO, StringIO
import json
from zipfile import ZipFile, ZIP_DEFLATED
from fastapi import HTTPException


def table_rows(source):
    provenance = source['source_provenance']
    labels = provenance.get('category_labels')
    for c in provenance['cells']:
        yield [labels['x'][c['xIndex']] if labels else c['x'],
               labels['y'][c['yIndex']] if labels else c['y'],
               c['z'], c.get('standardError', ''), provenance['unit']]


def csv_bytes(source):
    output = StringIO(newline='')
    writer = csv.writer(output)
    generic=source['source_provenance'].get('table')
    writer.writerow(generic['columns'] if generic else ['x', 'y', 'value', 'standard_error', 'unit'])
    # Prevent spreadsheet formulas in user-supplied categorical labels.
    for row in (generic['rows'] if generic else table_rows(source)):
        writer.writerow(["'"+v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v for v in row])
    return output.getvalue().encode('utf-8')


def png_bytes(svg_text):
    try:
        import pypdfium2
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
    except (ImportError, OSError) as exc:
        raise HTTPException(503, 'Install the optional pinned SVG conversion dependencies.') from exc
    svg = svg_text.encode()
    try:
        drawing = svg2rlg(BytesIO(svg))
        if drawing is None: raise ValueError('Invalid saved SVG')
        pdf = renderPDF.drawToString(drawing, invariant=1)
        with pypdfium2.PdfDocument(pdf) as document:
            page = document[0]
            bitmap = page.render(scale=2580/page.get_width())
            image = bitmap.to_pil()
            output = BytesIO(); image.save(output, format='PNG'); png = output.getvalue()
            image.close(); bitmap.close(); page.close()
    except (OSError, ValueError) as exc:
        raise HTTPException(503, 'Saved SVG conversion unavailable; no substitute figure generated.') from exc
    return png


def docx_bytes(result, obj):
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
    except ImportError as exc:
        raise HTTPException(503, 'Install the optional pinned DOCX dependencies.') from exc
    svg = result['view']['svg'].encode()
    png = png_bytes(result['view']['svg'])
    source = result['view']['source']
    context = source['source_provenance'].get('scientific_context')
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(.65)
    for style in doc.styles:
        if style.type == 1:
            style.font.color.rgb = RGBColor(0, 0, 0)
    for border in list(doc.styles.element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pBdr')):
        border.getparent().remove(border)
    normal = doc.styles['Normal']
    normal.font.name = 'Arial'; normal.font.size = Pt(10)
    doc.styles['Title'].font.color.rgb = RGBColor(0, 0, 0)
    doc.add_paragraph(obj.get('title', 'Scientific reference figure'), 'Title')
    doc.add_paragraph(obj.get('description', 'Source-bound scientific figure.'))
    from PIL import Image
    with Image.open(BytesIO(png)) as image:
        fitted_width=min(6.3,(7.0 if source['render_type']=='scientific-composer' else 7.5)*image.width/image.height)
    doc.add_picture(BytesIO(png), width=Inches(fitted_width))
    doc.paragraphs[-1].paragraph_format.keep_with_next=True
    caption=doc.add_paragraph('Figure 1. '+obj.get('title', 'Scientific heatmap'), 'Caption')
    caption.paragraph_format.keep_with_next=False
    caption.paragraph_format.keep_together=True
    doc.add_page_break()
    doc.add_heading('Source data and uncertainty', level=1)
    generic=source['source_provenance'].get('table')
    if generic:
        # Long scientific denominators and protocol fields remain editable and
        # readable; avoid squeezing thirteen columns into a portrait page.
        for index,row in enumerate(generic['rows']):
            doc.add_heading('Record '+str(index+1),level=2)
            table=doc.add_table(rows=0,cols=2);table.style='Light Shading Accent 1';table.autofit=False
            table.columns[0].width=Inches(1.4);table.columns[1].width=Inches(4.9)
            for label,value in zip(generic['columns'],row):
                cells=table.add_row().cells;cells[0].width=Inches(1.4);cells[1].width=Inches(4.9);cells[0].text=str(label);cells[1].text='' if value is None else str(value)
            from docx.oxml import OxmlElement
            for row_index,table_row in enumerate(table.rows):
                table_row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                for cell in table_row.cells:
                    for paragraph in cell.paragraphs:
                        paragraph.paragraph_format.keep_with_next=row_index<len(table.rows)-1
                        paragraph.paragraph_format.keep_together=True
        doc.add_heading('Sources and limitations',level=1)
        for note in source['source_provenance']['limitations']:doc.add_paragraph(note)
        for reference in source['source_provenance']['sources']:
            doc.add_paragraph(reference['citation'])
            doc.add_paragraph(reference['uri']+' | '+reference['locator'])
            doc.add_paragraph('Source SHA256: '+reference['sha256']+' | Review: '+reference['review'])
    else:
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Light Shading Accent 1'
        for cell, text in zip(table.rows[0].cells, ['Category X', 'Category Y', 'Value', 'SE', 'Unit']): cell.text = text
        for row in table_rows(source):
            for cell, value in zip(table.add_row().cells, row): cell.text = str(value)
    if context:
        doc.add_paragraph(context['warning'])
        review = context['source'].get('extraction_review', {}).get('human_review', 'undeclared')
        doc.add_paragraph('Human source extraction review: '+str(review)+'.')
        doc.add_heading('Reference', level=1)
        doc.add_paragraph(context['source']['citation'])
        doc.add_paragraph('Source URL: '+context['source']['url'])
        doc.add_paragraph('Publisher PDF SHA256: '+context['source']['sha256'])
    integrity=doc.add_paragraph('Figure source SHA256: '+result['view']['source_sha256']+'\nSaved SVG SHA256: '+hashlib.sha256(svg).hexdigest())
    integrity.paragraph_format.keep_together=True
    for run in integrity.runs:run.font.size=Pt(8)
    doc.core_properties.created = doc.core_properties.modified = datetime(2000, 1, 1)
    doc.core_properties.author = 'Sustainable Catalyst'
    output = BytesIO(); doc.save(output)
    # Explicitly related package attachments retain canonical sources. Parts use
    # .xml to stay compatible with Word OPC readers; no executable external links.
    from lxml import etree as ET
    from base64 import b64encode
    with ZipFile(BytesIO(output.getvalue())) as original:
        parts = {n: original.read(n) for n in original.namelist()}
    ns = 'http://schemas.openxmlformats.org/package/2006/relationships'
    rels = ET.fromstring(parts['word/_rels/document.xml.rels'])
    for name, data in [('source', json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()), ('figure', svg)]:
        target = 'customXml/sc-'+name+'.xml'
        parts[target] = ('<scientificArtifact encoding="base64">'+b64encode(data).decode()+'</scientificArtifact>').encode()
        ET.SubElement(rels, '{'+ns+'}Relationship', {'Id':'sc-'+name, 'Type':'http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml', 'Target':'../'+target})
    parts['word/_rels/document.xml.rels'] = ET.tostring(rels, encoding='utf-8', xml_declaration=True)
    final = BytesIO()
    with ZipFile(final, 'w', compression=ZIP_DEFLATED) as archive:
        from zipfile import ZipInfo
        for name in sorted(parts):
            entry = ZipInfo(name, (2000, 1, 1, 0, 0, 0)); entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, parts[name])
    return final.getvalue()
