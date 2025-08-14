import streamlit as st
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Frame, Paragraph
from reportlab.lib.units import inch
import os
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

PAGE_WIDTH, PAGE_HEIGHT = A4

# Path to your hardcoded logo file
LOGO_PATH_RIGHT = "Metasol_Logo_Right.png"  # make sure this file is in the same folder as this script
LOGO_PATH_LEFT = "Metasol_Logo_left.png"  # make sure this file is in the same folder as this script
LOGO_PATH_FOOTER = 'Footer.png'

st.set_page_config(page_title="PO PDF Generator", layout="wide")

st.title("Purchase Order PDF Generator")

# --- FORM START ---
with st.form("po_form"):
    st.subheader("Purchase Order Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", "Anu Shams")
        designation = st.text_input("Designation", "Sales")
        vat_no = st.text_input("VAT No.", "311863395100003")
        mobile = st.text_input("Mobile No.", "+966 543 824 224")
        company_name = st.text_area("Company Name", "Advanced Solutions Arabia Trading Est.")
    with col2:
        po_no = st.text_input("PO No.", "MSIC-PO-A065-08-2025")
        po_date = st.date_input("PO Date", date(2025, 8, 10))
        fax_no = st.text_input("Fax No.", "-")
        pr_number = st.text_input("PR Number", "MSIC-PR-A020-08-2025")
        supplier = st.text_input("Supplier", "")
        ref_quote = st.text_input("Reference Quotation #", "QT210163")
        telephone = st.text_input("Telephone No.", "+966 13 851 1013 x 1001")
        email = st.text_input("Email", "anu@fssitech.com")
    
    subject = st.text_area("Subject")

    st.subheader("Line Items")
    if "line_items" not in st.session_state:
        st.session_state.line_items = []

    with st.expander("Add Line Item"):
        desc = st.text_area("Description")
        unit = st.text_input("Unit")
        qty = st.number_input("Qty", min_value=1, value=1)
        unit_cost = st.number_input("Unit Cost", min_value=0.0, value=0.0, step=0.01)
        if st.form_submit_button("Add Item", type="secondary"):
            total_price = qty * unit_cost
            st.session_state.line_items.append([
                len(st.session_state.line_items) + 1,
                desc,
                unit,
                qty,
                f"{unit_cost:,.2f}",
                f"{total_price:,.2f}"
            ])

    if st.session_state.line_items:
        df = pd.DataFrame(
        st.session_state.line_items,
        columns=["Sr. No.", "Description", "Unit", "Qty", "Unit Cost", "Total Price"]
        )
        st.table(df)

    total = sum(float(item[5].replace(",", "")) for item in st.session_state.line_items)
    vat = total * 0.15
    grand_total = total + vat

    st.write(f"**Total:** {total:,.2f}")
    st.write(f"**15% VAT:** {vat:,.2f}")
    st.write(f"**Grand Total:** {grand_total:,.2f}")

    submitted = st.form_submit_button("Generate PDF")

# --- FORM END ---

if submitted:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Draw Logo
    if os.path.exists(LOGO_PATH_LEFT):
        c.drawImage(LOGO_PATH_LEFT, 40, PAGE_HEIGHT - 60, width=2.11*inch, height=0.58*inch, preserveAspectRatio=True, mask='auto', anchor="nw")

    right_img_width = 2.33 * inch
    if os.path.exists(LOGO_PATH_RIGHT):
        c.drawImage(LOGO_PATH_RIGHT, PAGE_WIDTH - 40 - right_img_width, PAGE_HEIGHT - 60, width=2.33*inch, height=0.58*inch, preserveAspectRatio=True,mask='auto', anchor='ne')

    #VAT Number
    c.setFont("Helvetica", 10)
    c.drawString(40, PAGE_HEIGHT - 70, ' VAT No. 311863395100003')

    c.setLineWidth(1)
    c.line(40, PAGE_HEIGHT - 80, PAGE_WIDTH - 40, PAGE_HEIGHT - 80)
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 100, "PURCHASE ORDER")

    c.setLineWidth(1)
    c.line(40, PAGE_HEIGHT - 110, PAGE_WIDTH - 40, PAGE_HEIGHT - 110)

    # Details block
    c.setFont("Helvetica", 10)
    c.drawString(40, PAGE_HEIGHT - 130, f"Name:")
    c.drawString(130, PAGE_HEIGHT - 130, f"{name}")
    c.setLineWidth(0.3)
    line_end = (PAGE_WIDTH / 2) - 10
    c.line(130, PAGE_HEIGHT - 132, line_end, PAGE_HEIGHT - 132)

    po_line_start = PAGE_WIDTH / 2 + 70
    c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 130, f"PO No.:")
    c.drawString(po_line_start, PAGE_HEIGHT - 130, f"{po_no}")
    c.setLineWidth(0.3)
    c.line(po_line_start, PAGE_HEIGHT - 132, PAGE_WIDTH - 50, PAGE_HEIGHT - 132)


    c.drawString(40, PAGE_HEIGHT - 150, f"Designation:")
    c.drawString(130, PAGE_HEIGHT - 150, f"{designation}")
    c.setLineWidth(0.3)
    line_end = (PAGE_WIDTH / 2) - 10
    c.line(130, PAGE_HEIGHT - 152, line_end, PAGE_HEIGHT - 152)

    
    c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 150, f"PO Date:")
    c.drawString(po_line_start, PAGE_HEIGHT - 150, f"{po_date.strftime('%A, %B %d, %Y')}")
    c.setLineWidth(0.3)
    c.line(po_line_start, PAGE_HEIGHT - 152, PAGE_WIDTH - 50, PAGE_HEIGHT - 152)    


    
    c.drawString(40, PAGE_HEIGHT - 175, f"Company Name:")
    # Prepare paragraph style
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 10
    style.leading = 12  # line height

    # Create Paragraph object for company name
    company_para = Paragraph(company_name, style)
    # Define frame position & size
    frame_x = 130
    frame_y = PAGE_HEIGHT - 200  # subtract height so text fits
    frame_width = 150         # adjust to fit your layout
    frame_height = 50        # height of the box

    # Create frame
    frame = Frame(frame_x, frame_y, frame_width, frame_height, showBoundary=0)

    # Add paragraph to frame
    frame.addFromList([company_para], c)
    
    c.setLineWidth(0.3)
    line_end = (PAGE_WIDTH / 2) - 10
    c.line(130, PAGE_HEIGHT - 190, line_end, PAGE_HEIGHT - 190)

    c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 175, f"Supplier")
    c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 185, f"Reference:")
    c.drawString(po_line_start, PAGE_HEIGHT - 180, f"Quotation #: {ref_quote}")
    c.setLineWidth(0.3)
    c.line(po_line_start, PAGE_HEIGHT - 190, PAGE_WIDTH - 50, PAGE_HEIGHT - 190)

    c.drawString(40, PAGE_HEIGHT - 210, f"Telephone No.:")
    c.drawString(130, PAGE_HEIGHT - 210, f"{telephone}")
    c.setLineWidth(0.3)
    line_end = (PAGE_WIDTH / 2) - 10
    c.line(130, PAGE_HEIGHT - 212, line_end, PAGE_HEIGHT - 212)

    
    c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 210, f"Email:")
    c.drawString(po_line_start, PAGE_HEIGHT - 210, f"{email}")
    c.setLineWidth(0.3)
    c.line(po_line_start, PAGE_HEIGHT - 212, PAGE_WIDTH - 50, PAGE_HEIGHT - 212)

    c.drawString(40, PAGE_HEIGHT - 230, f"Fax No.:")
    c.drawString(130, PAGE_HEIGHT - 230, f"{fax_no}")
    c.setLineWidth(0.3)
    line_end = (PAGE_WIDTH / 2) - 10
    c.line(130, PAGE_HEIGHT - 232, line_end, PAGE_HEIGHT - 232)

    
    c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 230, f"PR Number:")
    c.drawString(po_line_start, PAGE_HEIGHT - 230, f"{pr_number}")
    c.setLineWidth(0.3)
    c.line(po_line_start, PAGE_HEIGHT - 232, PAGE_WIDTH - 50, PAGE_HEIGHT - 232)

    c.drawString(40, PAGE_HEIGHT - 250, f"Mobile No.:")
    c.drawString(130, PAGE_HEIGHT - 250, f"{mobile}")
    c.setLineWidth(0.3)
    line_end = (PAGE_WIDTH / 2) - 10
    c.line(130, PAGE_HEIGHT - 252, line_end, PAGE_HEIGHT - 252)

    c.drawString(40, PAGE_HEIGHT - 270, f"Subject: {subject}")

    # Subject
    # c.setFont("Helvetica-Bold", 10)
    # c.drawString(40, PAGE_HEIGHT - 225, f"Subject: {subject}")

    # Line Items Table
    table_data = [["Sr. No.", "Description", "Unit", "Qty", "Unit Cost", "Total Price"]] + st.session_state.line_items
    table = Table(table_data, colWidths=[40, 220, 50, 40, 70, 70])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        # ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 9)
    ]))
    table.wrapOn(c, 40, PAGE_HEIGHT - 355)
    table_height = len(table_data) * 18
    table.drawOn(c, 40, PAGE_HEIGHT - 305 - table_height)

    # Totals
    y_pos = PAGE_HEIGHT - 320 - table_height
    c.setFont("Helvetica-Bold", 10)
    c.drawString(400, y_pos, f"Total: {total:,.2f}")
    y_pos -= 12
    c.drawString(400, y_pos, f"15% VAT: {vat:,.2f}")
    y_pos -= 12
    c.drawString(400, y_pos, f"Grand Total (SAR): {grand_total:,.2f}")

    y_pos -= 12
    c.setLineWidth(0.5)
    c.line(40, y_pos, PAGE_WIDTH - 40, y_pos)
    y_pos -= 12
    c.setFont("Helvetica", 10)
    c.drawString(40, y_pos, "Terms and Conditions")
    #Payment Terms
    y_pos -= 25
    c.setFont("Helvetica", 9)
    c.drawString(40, y_pos, "Payment Terms: 100% Advance through bank")
    y_pos -= 12
    c.drawString(40, y_pos, "Contact Person:")
    y_pos -= 12
    c.drawString(40, y_pos, "Incoterm: DPA")
    y_pos -= 12
    c.drawString(40, y_pos, "Place of Delivery: Meta Solutions Industrial Company,  First Floor, KCT Building No: 8588, Al Firdaws Ar")
    y_pos -= 12
    c.drawString(40, y_pos, "Contact Person: ")
    y_pos -= 12
    c.drawString(40, y_pos, "Delivery Schedule: Immediate")
    y_pos -= 12
    c.drawString(40, y_pos, "Packing: N/A")
    y_pos -= 12
    c.drawString(40, y_pos, "Packaging: N/A")
    y_pos -= 12
    c.drawString(40, y_pos, "Note: Duration of Subscription: 7th Aug 2025 to 6th Aug 2026 ")

    # Note
    y_pos -= 70
    c.setFont("Helvetica", 10)
    c.drawString(40, y_pos, "Please confirm the purchase order.")
    y_pos -= 12
    c.drawString(40, y_pos, "Best Regards")
    y_pos -= 12
    c.drawString(40, y_pos, "On behalf of Meta Solutions Industrial Company")

    # Approvals
    y_pos -= 35
    c.setFont("Helvetica", 9)
    c.drawString(40, 62, "Prepared & checked by:")
    c.drawString(40, 36, "AMIR RODRIGUEZ")
    c.drawString(180, 62, "Reviewed by:")
    c.drawString(180, 36, "WASIUR REHMAN KHAN")
    c.drawString(320, 62, "Authorized by")
    c.drawString(320, 36, "DR. VIMAL PATEL")
    c.drawString(460, 62, "Approved by:")
    c.drawString(460, 36, " ANVER SADATH")

    y_pos -= 24
    c.setFont("Helvetica", 8)
    c.drawString(40, 50, "Procurement Manager")
    c.drawString(180, 50, "Finance Manager")
    c.drawString(320, 50, "General Manager")
    c.drawString(460, 50, "Chairman & Managing Director")

    available_width = PAGE_WIDTH - (2 * 40)


    if os.path.exists(LOGO_PATH_FOOTER):
        c.drawImage(LOGO_PATH_FOOTER, 40, -30, width=available_width, preserveAspectRatio=True, mask='auto')


    c.showPage()
    c.save()
    buffer.seek(0)

    st.download_button(
        label="Download PO PDF",
        data=buffer,
        file_name=f"{po_no}.pdf",
        mime="application/pdf"
    )
