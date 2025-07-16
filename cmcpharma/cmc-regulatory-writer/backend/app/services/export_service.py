import io
import re
from typing import List, Dict, Tuple
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from ..models.document import GeneratedDocument

class RegulatoryPDFExporter:
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for regulatory documents"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='RegulatoryTitle',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1f4e79')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor('#1f4e79')
        ))
        
        # Regular content style
        self.styles.add(ParagraphStyle(
            name='RegulatoryContent',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            firstLineIndent=20
        ))

    def generate_regulatory_document(self, document: GeneratedDocument) -> bytes:
        """Generate a PDF document from a GeneratedDocument model"""
        content = document.dict()  # Convert Pydantic model to dict for processing
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Document title
        story.append(Paragraph(content.get('title', 'Regulatory Document'), self.styles['RegulatoryTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Add generation metadata
        story.append(Paragraph(f"Generated on: {content.get('generated_at', '')}", self.styles['Normal']))
        story.append(Paragraph(f"Session ID: {content.get('session_id', '')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add sections
        for section in content.get('sections', []):
            # Section title
            story.append(Paragraph(section.get('title', ''), self.styles['SectionHeader']))
            
            # Section content
            content_text = section.get('content', '')
            # Clean and escape the content
            content_text = self._clean_content(content_text)
            story.append(Paragraph(content_text, self.styles['RegulatoryContent']))
            
            # Add source count info
            source_count = section.get('source_count', 0)
            if source_count > 0:
                story.append(Paragraph(f"<i>Sources referenced: {source_count}</i>", self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _clean_content(self, content: str) -> str:
        """Clean and format content for PDF generation"""
        if not content:
            return ""
        
        # Escape HTML entities
        content = escape(content)
        
        # Replace line breaks with paragraph breaks
        content = content.replace('\n\n', '<br/><br/>')
        content = content.replace('\n', '<br/>')
        
        return content
