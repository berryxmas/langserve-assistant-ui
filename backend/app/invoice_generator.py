# backend/app/invoice_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
import uuid
from datetime import datetime, timedelta
import io

class InvoiceGenerator:
    def __init__(self, output_dir="invoices"):
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='CenterAlign', alignment=TA_CENTER))
        self.styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))
        
    def generate_invoice(self, invoice_data):
        """
        Generate a PDF invoice based on the provided data
        
        Args:
            invoice_data (dict): Dictionary containing invoice information
            
        Returns:
            str: Path to the generated PDF file
        """
        # Extract invoice data
        customer_name = invoice_data.get('customer', {}).get('name', 'Customer')
        customer_email = invoice_data.get('customer', {}).get('email', '')
        invoice_number = invoice_data.get('invoice_number', f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}")
        invoice_date = invoice_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))
        due_date = invoice_data.get('due_date', (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'))
        items = invoice_data.get('items', [])
        subtotal = invoice_data.get('subtotal', sum(item.get('amount', 0) for item in items))
        tax_rate = invoice_data.get('tax_rate', 0.21)
        tax_amount = invoice_data.get('tax_amount', subtotal * tax_rate)
        total_amount = invoice_data.get('total_amount', subtotal + tax_amount)
        currency = invoice_data.get('currency', 'EUR')
        company_logo = invoice_data.get('company_logo', None)
        company_name = invoice_data.get('company_name', 'Your Company Name')
        company_address = invoice_data.get('company_address', 'Your Company Address')
        company_email = invoice_data.get('company_email', 'company@example.com')
        company_phone = invoice_data.get('company_phone', '+31 123 456 789')
        company_vat = invoice_data.get('company_vat', 'NL123456789B01')
        
        # Create the PDF filename
        filename = f"Invoice-{invoice_number}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create a buffer for the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Header section with logo and company info
        header_data = [
            [Image(company_logo, width=60*mm, height=20*mm) if company_logo else Paragraph(company_name, self.styles['Heading1']), 
             Paragraph(f"<b>INVOICE</b><br/><br/>#{invoice_number}", self.styles['RightAlign'])]
        ]
        header_table = Table(header_data, colWidths=[doc.width/2.0]*2)
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10*mm))
        
        # Company and customer info section
        company_info = f"""
        <b>{company_name}</b><br/>
        {company_address}<br/>
        Email: {company_email}<br/>
        Phone: {company_phone}<br/>
        VAT: {company_vat}
        """
        
        customer_info = f"""
        <b>Bill To:</b><br/>
        {customer_name}<br/>
        Email: {customer_email}
        """
        
        info_data = [
            [Paragraph(company_info, self.styles['LeftAlign']), Paragraph(customer_info, self.styles['LeftAlign'])]
        ]
        info_table = Table(info_data, colWidths=[doc.width/2.0]*2)
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10*mm),
        ]))
        elements.append(info_table)
        
        # Invoice details section
        details_data = [
            [Paragraph("<b>Invoice Date:</b>", self.styles['LeftAlign']), 
             Paragraph("<b>Due Date:</b>", self.styles['LeftAlign'])],
            [Paragraph(invoice_date, self.styles['LeftAlign']), 
             Paragraph(due_date, self.styles['LeftAlign'])]
        ]
        details_table = Table(details_data, colWidths=[doc.width/2.0]*2)
        details_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5*mm),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 5*mm))
        
        # Items section
        items_data = [["Description", "Amount"]]
        for item in items:
            items_data.append([
                item.get('description', ''),
                f"{currency} {item.get('amount', 0):.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[doc.width*0.7, doc.width*0.3])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 5*mm))
        
        # Totals section
        totals_data = [
            ["Subtotal:", f"{currency} {subtotal:.2f}"],
            [f"Tax ({tax_rate*100:.0f}%):", f"{currency} {tax_amount:.2f}"],
            ["Total:", f"{currency} {total_amount:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[doc.width*0.7, doc.width*0.3])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(totals_table)
        
        # Footer with payment information
        elements.append(Spacer(1, 10*mm))
        payment_info = f"""
        <b>Payment Information:</b><br/>
        Please make payment to: {company_name}<br/>
        Bank: Your Bank Name<br/>
        IBAN: NL00 BANK 0123 4567 89<br/>
        Reference: {invoice_number}
        """
        elements.append(Paragraph(payment_info, self.styles['LeftAlign']))
        
        # Thank you note
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph("Thank you for your business!", self.styles['CenterAlign']))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the value from the buffer
        pdf_value = buffer.getvalue()
        buffer.close()
        
        # Write the PDF to a file
        with open(filepath, 'wb') as f:
            f.write(pdf_value)
        
        return {
            'filepath': filepath,
            'filename': filename,
            'size': os.path.getsize(filepath),
            'pages': 1  # For simplicity, we're assuming 1 page
        }