"""MD to DOCX converter for research outputs"""
import sys
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def md_to_docx(md_path, docx_path):
    doc = Document()
    
    # Style defaults
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Malgun Gothic'
    font.size = Pt(10)
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.rstrip('\n')
        
        if line.startswith('# '):
            p = doc.add_heading(line[2:], level=1)
        elif line.startswith('## '):
            p = doc.add_heading(line[3:], level=2)
        elif line.startswith('### '):
            p = doc.add_heading(line[4:], level=3)
        elif line.startswith('- '):
            p = doc.add_paragraph(line[2:], style='List Bullet')
        elif line.startswith('|') and '---' not in line:
            # Simple table row - just add as paragraph
            cells = [c.strip() for c in line.split('|')[1:-1]]
            p = doc.add_paragraph(' | '.join(cells))
            p.style.font.size = Pt(9)
        elif line.strip() == '' or line.startswith('|') and '---' in line:
            continue
        else:
            # Bold handling
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            doc.add_paragraph(text)
    
    doc.save(docx_path)
    print(f"Saved: {docx_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python md_to_docx.py input.md output.docx")
        sys.exit(1)
    md_to_docx(sys.argv[1], sys.argv[2])
