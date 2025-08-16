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
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle

pdfmetrics.registerFont(TTFont('CenturyGothic', 'centurygothic.ttf'))
pdfmetrics.registerFont(TTFont('CenturyGothicBold', 'centurygothic_bold.ttf'))

PAGE_WIDTH, PAGE_HEIGHT = A4

# Path to your hardcoded logo file
LOGO_PATH_RIGHT = "Metasol_Logo_Right.png"  # make sure this file is in the same folder as this script
LOGO_PATH_LEFT = "Metasol_Logo_left.png"  # make sure this file is in the same folder as this script
LOGO_PATH_FOOTER = 'Footer.png'

st.set_page_config(page_title="PO PDF Generator", layout="wide")

report_type = st.sidebar.selectbox(
    "Select Report Format",
    ["Local Report Format", "Foreign Report Format"]
)

st.title("Purchase Order PDF Generator")

st.write(f"**Selected Report Type:** {report_type}")

if report_type == "Local Report Format":

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
        c.setFont("CenturyGothic", 10)
        c.drawString(40, PAGE_HEIGHT - 70, ' VAT No. 311863395100003')

        c.setLineWidth(1)
        c.line(40, PAGE_HEIGHT - 80, PAGE_WIDTH - 40, PAGE_HEIGHT - 80)
        # Title
        c.setFont("CenturyGothicBold", 12.5)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 100, "PURCHASE ORDER")

        c.setLineWidth(1)
        c.line(40, PAGE_HEIGHT - 110, PAGE_WIDTH - 40, PAGE_HEIGHT - 110)

        # Details block
        c.setFont("CenturyGothic", 10)
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
        style.fontName = "CenturyGothic"
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
        c.setFont("CenturyGothicBold", 10)
        c.drawString(400, y_pos, f"Total: {total:,.2f}")
        y_pos -= 12
        c.drawString(400, y_pos, f"15% VAT: {vat:,.2f}")
        y_pos -= 12
        c.drawString(400, y_pos, f"Grand Total (SAR): {grand_total:,.2f}")

        y_pos -= 12
        c.setLineWidth(0.5)
        c.line(40, y_pos, PAGE_WIDTH - 40, y_pos)
        y_pos -= 12
        c.setFont("CenturyGothic", 11)
        c.drawString(40, y_pos, "Terms and Conditions")
        #Payment Terms
        y_pos -= 25
        c.setFont("CenturyGothic", 10)
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
        c.setFont("CenturyGothic", 10)
        c.drawString(40, y_pos, "Please confirm the purchase order.")
        y_pos -= 12
        c.drawString(40, y_pos, "Best Regards")
        y_pos -= 12
        c.drawString(40, y_pos, "On behalf of Meta Solutions Industrial Company")

        # Approvals
        y_pos -= 35
        c.setFont("CenturyGothic", 9)
        c.drawString(40, 62, "Prepared & checked by:")
        c.drawString(40, 36, "AMIR RODRIGUEZ")
        c.drawString(180, 62, "Reviewed by:")
        c.drawString(180, 36, "WASIUR REHMAN KHAN")
        c.drawString(320, 62, "Authorized by")
        c.drawString(320, 36, "DR. VIMAL PATEL")
        c.drawString(460, 62, "Approved by:")
        c.drawString(460, 36, " ANVER SADATH")

        y_pos -= 24
        c.setFont("CenturyGothic", 8)
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

elif report_type == "Foreign Report Format":
    st.title("Foreign PO Report")
    st.subheader("Foreign Purchase Order Details")

    # First row: PO No. + Date
    col1, col2 = st.columns(2)
    po_no = col1.text_input("P.O. No.", "MSIC-PO-A051-06-2025")
    po_date = col2.date_input("Date", date(2025, 6, 2))

    # Second row: PR No. (single column)
    pr_no = st.text_input("P.R. No.", "MSIC-PR-A010-06-2025")

    st.markdown("### Supplier Details")

    # To + Designation
    col1, col2 = st.columns(2)
    to_name = col1.text_input("To", "Ms. Joanna Zhang")
    designation = col2.text_input("Designation", "Sales")

    # Company name (full width)
    company = st.text_input("Company", "Shanghai FR Import&Export Co.,Ltd.")

    # Telephone + Email
    col1, col2 = st.columns(2)
    telephone = col1.text_input("Telephone No.", "-")
    email = col2.text_input("Email", "jz@frindustry.com")

    # Fax + Mobile
    col1, col2 = st.columns(2)
    fax = col1.text_input("Fax No.", "-")
    mobile = col2.text_input("Mobile No.", "18301768502")

    # Address (full width)
    address = st.text_area("Address", "No.5588 Caoan Rd ,Jiading District,201800,Shanghai,China")

    st.markdown("### Subject")
    subject = st.text_area("Subject", "Promotional Items")
     # ---- Consignee Details & Notify Party ----
    st.markdown("### Consignee Details & Notify Party")
    consignee_name = st.text_input("Name", "Meta Solutions Industrial Company")
    consignee_address = st.text_area(
        "Address",
        "First Floor, KCT Building No: 8588, Al Firdaws Area, Prince Mohammed Bin Fahad Road, Dammam 31441, Saudi Arabia"
    )
    consignee_contact = st.text_input("Contact", "Mr. Selahadin - +966 535 005 759")
    consignee_tel = st.text_input("Tel.", "+966 13 868 1777")
    consignee_fax = st.text_input("Fax", "+966 13 868 5777")
    consignee_email = st.text_input("Email", "Procurement@metasolco.com")

    # ---- Shipping Documents ----
    st.markdown("### Shipping Documents")
    shipping_docs = [
        ["Bill of Lading / Airway Bill", 2, 1],
        ["Packing List", 2, 1],
        ["Certificate of Origin (Chambered)", 2, 1],
        ["Commercial Invoice (Chambered)", 2, 1],
        ["Insurance Policy", 1, "-"],
        ["Certificate of Analysis", 2, "-"],
        ["Material Safety Data Sheet", 2, "-"]
    ]
    shipping_df = pd.DataFrame(shipping_docs, columns=["Documentation", "Original", "Duplicate"])
    st.table(shipping_df)

    # ---- Purchase Details (Dynamic Table) ----
    st.markdown("### Purchase Details")
    if "foreign_line_items" not in st.session_state:
        st.session_state.foreign_line_items = []

    with st.expander("Add Purchase Item"):
        hs_code = st.text_input("HS Code", "")
        product_desc = st.text_area("Product Description", "")
        uom = st.text_input("UoM", "")
        qty = st.number_input("Qty", min_value=1, value=1)
        unit_cost = st.number_input("Unit Cost", min_value=0.0, value=0.0, step=0.01)
        if st.button("Add Item"):
            total_price = qty * unit_cost
            st.session_state.foreign_line_items.append([
                len(st.session_state.foreign_line_items) + 1,
                hs_code,
                product_desc,
                uom,
                qty,
                f"{unit_cost:,.2f}",
                f"{total_price:,.2f}"
            ])

    if st.session_state.foreign_line_items:
        purchase_df = pd.DataFrame(
            st.session_state.foreign_line_items,
            columns=["S.No.", "HS Code", "Product Description", "UoM", "Qty", "Unit Cost", "Total Price"]
        )
        st.table(purchase_df)

    # Calculate Grand Total from last column of line items
    grand_total = 0.0
    for row in st.session_state.foreign_line_items:
        try:
            # row[-1] is Total Price, remove commas and convert to float
            grand_total += float(str(row[-1]).replace(",", ""))
        except ValueError:
            pass  # skip if conversion fails
    
    
    if st.button("Generate PDF"):
        pdf_path = "foreign_po.pdf"
        c = canvas.Canvas(pdf_path, pagesize=A4)

        # Draw Logo
        if os.path.exists(LOGO_PATH_LEFT):
            c.drawImage(LOGO_PATH_LEFT, 40, PAGE_HEIGHT - 60, width=2.11*inch, height=0.58*inch, preserveAspectRatio=True, mask='auto', anchor="nw")

        right_img_width = 2.33 * inch
        if os.path.exists(LOGO_PATH_RIGHT):
            c.drawImage(LOGO_PATH_RIGHT, PAGE_WIDTH - 40 - right_img_width, PAGE_HEIGHT - 60, width=2.33*inch, height=0.58*inch, preserveAspectRatio=True,mask='auto', anchor='ne')

        #VAT Number
        c.setFont("CenturyGothic", 10)
        c.drawString(40, PAGE_HEIGHT - 70, ' VAT No. 311863395100003')

        c.setLineWidth(1)
        c.line(40, PAGE_HEIGHT - 80, PAGE_WIDTH - 40, PAGE_HEIGHT - 80)
        # Title
        c.setFont("CenturyGothicBold", 12.5)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 100, "FOREIGN PURCHASE ORDER")

        c.setLineWidth(1)
        c.line(40, PAGE_HEIGHT - 110, PAGE_WIDTH - 40, PAGE_HEIGHT - 110)

        # Details block
        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 130, f"P.O. No.:")
        c.drawString(130, PAGE_HEIGHT - 130, f"{po_no}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 132, line_end, PAGE_HEIGHT - 132)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 130, f"Date:")
        c.drawString(po_line_start, PAGE_HEIGHT - 130, f"{po_date.strftime('%A, %B %d, %Y')}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 132, PAGE_WIDTH - 50, PAGE_HEIGHT - 132)

        c.drawString(40, PAGE_HEIGHT - 140, f"P.R. No.:")
        c.drawString(130, PAGE_HEIGHT - 140, f"{pr_no}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 142, line_end, PAGE_HEIGHT - 142)

        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 150, "Supplier Details")

        c.drawString(40, PAGE_HEIGHT - 160, f"To:")
        c.drawString(130, PAGE_HEIGHT - 160, f"{to_name}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 162, line_end, PAGE_HEIGHT - 162)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 160, f"Designation:")
        c.drawString(po_line_start, PAGE_HEIGHT - 160, f"{designation}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 162, PAGE_WIDTH - 50, PAGE_HEIGHT - 162)

        c.drawString(40, PAGE_HEIGHT - 170, f"Company:")
        c.drawString(130, PAGE_HEIGHT - 170, f"{company}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 172, PAGE_WIDTH - 50, PAGE_HEIGHT - 172)

        c.drawString(40, PAGE_HEIGHT - 180, f"Telephone No.:")
        c.drawString(130, PAGE_HEIGHT - 180, f"{telephone}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 182, line_end, PAGE_HEIGHT - 182)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 180, f"Email:")
        c.drawString(po_line_start, PAGE_HEIGHT - 180, f"{email}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 182, PAGE_WIDTH - 50, PAGE_HEIGHT - 182)

        c.drawString(40, PAGE_HEIGHT - 190, f"Fax No:")
        c.drawString(130, PAGE_HEIGHT - 190, f"{fax}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 192, line_end, PAGE_HEIGHT - 192)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 190, f"Mobile No.:")
        c.drawString(po_line_start, PAGE_HEIGHT - 190, f"{mobile}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 192, PAGE_WIDTH - 50, PAGE_HEIGHT - 192)

        c.drawString(40, PAGE_HEIGHT - 200, f"Address:")
        c.drawString(130, PAGE_HEIGHT - 200, f"{address}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 202, PAGE_WIDTH - 50, PAGE_HEIGHT - 202)

        c.drawString(40, PAGE_HEIGHT - 210, f"Subject:")
        c.drawString(130, PAGE_HEIGHT - 210, f"{subject}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 212, PAGE_WIDTH - 50, PAGE_HEIGHT - 212)

        c.setStrokeColorRGB(0, 0, 0)  # black border
        c.setLineWidth(1)
        c.rect(38, PAGE_HEIGHT - 302, PAGE_WIDTH - 80, 80, stroke=1, fill=0)

        c.setFont("CenturyGothicBold", 7.5)
        c.drawString(40, PAGE_HEIGHT - 230, "Saudi Import Regulations:")

        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 240, "This is to notify Saudi Customs authority will not allow to clear the cargo of any material without any origin")

        c.drawString(40, PAGE_HEIGHT - 250, "information identification label, Hazmats or Hazcom, and supplier will be liable for the cost of return and")
        c.drawString(40, PAGE_HEIGHT - 260, "the penalties")
        c.drawString(40, PAGE_HEIGHT - 270, "a. Product Name")
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 270, "e. Date of Production")
        c.drawString(40, PAGE_HEIGHT - 280, "b. Weight(Gross/Net)")
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 280, "f. Hazcom or Hazmat signs as per the MSDS,")
        c.drawString(40, PAGE_HEIGHT - 290, "c. Supplier name,")
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 290, "g. Country of origin for all drums / IBC's etc.")
        c.drawString(40, PAGE_HEIGHT - 300, "d. Batch# or Lot#,")
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 300, "h. SASO Certificate for spares or equipments.")

        c.drawString(40, PAGE_HEIGHT - 320, "Terms & Conditions:")
        c.setFont("CenturyGothicBold", 7.5)
        c.drawString(40, PAGE_HEIGHT - 330, "Please note that this FPO T&C is our standard format; it may not be applicable to your materials or services. We kindly request that")
        c.drawString(40, PAGE_HEIGHT - 340, "you review the clauses and disregard any that do not pertain to your products and services.")

        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 350, "A  Payment Terms   : Advance")
        c.drawString(40, PAGE_HEIGHT - 360, "B  Mode of Payment : 100% Advance through bank")
        c.drawString(40, PAGE_HEIGHT - 370, "C  Regulations :")

        c.setFont("CenturyGothic", 7)
        c.drawString(50, PAGE_HEIGHT - 380, "- Photos of the material must be sent prior to dispatch, with a clear view of the label and the container. Do not ship the goods unless confirmed by")
        c.drawString(50, PAGE_HEIGHT - 390, "  the consignee and/or a COA is provided. (The supplier will not hold the containers once the product is stuffed and ready for shipment.)")

        c.drawString(50, PAGE_HEIGHT - 400, "- Purchase Order number, HS Code, and Weight (Net/Gross) must be mentioned in all documents. ")
        c.drawString(50, PAGE_HEIGHT - 410, "- Please send the draft of the shipping documents before legalization. Send the scan of the shipping documents after legalization, prior to courier.")
    
        c.drawString(50, PAGE_HEIGHT - 420, "- Please mention the bill of lading and container number in the commercial invoice and packing list.")
        c.drawString(50, PAGE_HEIGHT - 430, "- Place the COA, Material Safety Data Sheet, and Packing List along with the goods.")

        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 440, "D  INCO terms          :   DAP - MestaSoL, 2nd Industiral, Dammam")
        c.drawString(40, PAGE_HEIGHT - 450, "E  Place of Delivery   :   Meta Solutions Industrial Company, 2nd Industrial Dammam")
        c.drawString(40, PAGE_HEIGHT - 460, "F  Delivery Priority   :   Immediate")
        c.drawString(40, PAGE_HEIGHT - 470, "G  Delivery Schedule   :   Immediate")
        c.drawString(40, PAGE_HEIGHT - 480, "H  Packing             :   Palletized")
        c.drawString(40, PAGE_HEIGHT - 490, "I  Packaging           :   Palletized and shrink-wrapped")
        c.drawString(40, PAGE_HEIGHT - 500, "J  Additional Terms    :   Logo allocation: 300 pcs - MetaSol, 100 pcs - GIT, and 100 pcs - IAA ")


        # -------- SUPPLIER DETAILS --------
        y = PAGE_HEIGHT - 510
        # c.setFont("Helvetica-Bold", 12)
        # c.drawString(40, y, "Supplier Details")
        # y -= 15
        # c.setFont("Helvetica", 10)
        # supplier_lines = [
        #     f"P.O. No.: {po_no}   Date: {po_date.strftime('%A, %B %d, %Y')}",
        #     f"P.R. No.: {pr_no}",
        #     f"To: {to_name}   Designation: {designation}",
        #     f"Company: {company}",
        #     f"Telephone No.: {telephone}   Email: {email}",
        #     f"Fax No.: {fax}   Mobile No.: {mobile}",
        #     f"Address: {address}",
        #     f"Subject: {subject}"
        # ]
        # for line in supplier_lines:
        #     c.drawString(40, y, line)
        #     y -= 14

        # # -------- CONSIGNEE TABLE --------
        styles = getSampleStyleSheet()
        century_style = ParagraphStyle(
            name="CenturyGothicSmall",  # Just a name for your reference
            fontName="CenturyGothic",   # Must match your registered font
            fontSize=7.5,
            leading=9
        )
        c.setFont("CenturyGothic", 7.5)
        consignee_data = [
        ["Consignee Details & Notify Party", ""],
        ["Name", consignee_name],
        ["Address", Paragraph(consignee_address,century_style)],  # wrapped
        ["Contact", consignee_contact],
        ["Tel.", consignee_tel],
        ["Fax", consignee_fax],
        ["Email", consignee_email]
    ]

        # row heights — make Address row taller (index 2)
        consignee_row_heights = [20, 18, 50, 18, 18, 18, 18]

        consignee_table = Table(consignee_data, colWidths=[80, 180], rowHeights=consignee_row_heights)
        consignee_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("SPAN", (0,0), (-1,0)),
            ("FONTSIZE", (0,0), (-1,-1), 7.5),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("FONTNAME", (0,0), (-1,0), "CenturyGothicBold"), # header bold
            ("FONTNAME", (0,1), (-1,-1), "CenturyGothic"),    # rest normal
            ("ALIGN", (0,0), (-1,0), "CENTER")
        ]))

        # # -------- SHIPPING DOCUMENTS TABLE --------
        shipping_data = [["Shipping Documents", "", ""], ["Documentation", "Original", "Duplicate"]] + shipping_df.values.tolist()
        shipping_table = Table(shipping_data, colWidths=[160, 50, 50])
        shipping_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONTSIZE", (0,0), (-1,-1), 7.5),
            ("SPAN", (0,0), (-1,0)),
            ("ALIGN", (1,1), (-1,-1), "CENTER"),
            ("ALIGN", (0,0), (-1,0), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "CenturyGothicBold"), # header bold
            ("FONTNAME", (0,1), (-1,-1), "CenturyGothic"),    # rest normal
        ]))

        # Draw both tables side-by-side
        y -= 10
        consignee_table.wrapOn(c, 40, y)
        shipping_table.wrapOn(c, 320, y)
        consignee_table.drawOn(c, 40, y - consignee_table._height)
        shipping_table.drawOn(c, 320, y - shipping_table._height)

        # Adjust Y after tallest table
        side_tables_height = max(consignee_table._height, shipping_table._height)
        y = y - side_tables_height - 20

        available_width = PAGE_WIDTH - (2 * 40)
        if os.path.exists(LOGO_PATH_FOOTER):
            c.drawImage(LOGO_PATH_FOOTER, 40, -30, width=available_width, preserveAspectRatio=True, mask='auto')
        c.showPage()
        # # -------- NEW PAGE --------
        # Draw Logo
        if os.path.exists(LOGO_PATH_LEFT):
            c.drawImage(LOGO_PATH_LEFT, 40, PAGE_HEIGHT - 60, width=2.11*inch, height=0.58*inch, preserveAspectRatio=True, mask='auto', anchor="nw")

        right_img_width = 2.33 * inch
        if os.path.exists(LOGO_PATH_RIGHT):
            c.drawImage(LOGO_PATH_RIGHT, PAGE_WIDTH - 40 - right_img_width, PAGE_HEIGHT - 60, width=2.33*inch, height=0.58*inch, preserveAspectRatio=True,mask='auto', anchor='ne')

        #VAT Number
        c.setFont("CenturyGothic", 10)
        c.drawString(40, PAGE_HEIGHT - 70, ' VAT No. 311863395100003')

        c.setLineWidth(1)
        c.line(40, PAGE_HEIGHT - 80, PAGE_WIDTH - 40, PAGE_HEIGHT - 80)
        # Title
        c.setFont("CenturyGothicBold", 12.5)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 100, "FOREIGN PURCHASE ORDER")

        c.setLineWidth(1)
        c.line(40, PAGE_HEIGHT - 110, PAGE_WIDTH - 40, PAGE_HEIGHT - 110)

        # Details block
        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 130, f"P.O. No.:")
        c.drawString(130, PAGE_HEIGHT - 130, f"{po_no}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 132, line_end, PAGE_HEIGHT - 132)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 130, f"Date:")
        c.drawString(po_line_start, PAGE_HEIGHT - 130, f"{po_date.strftime('%A, %B %d, %Y')}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 132, PAGE_WIDTH - 50, PAGE_HEIGHT - 132)

        c.drawString(40, PAGE_HEIGHT - 140, f"P.R. No.:")
        c.drawString(130, PAGE_HEIGHT - 140, f"{pr_no}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 142, line_end, PAGE_HEIGHT - 142)

        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, PAGE_HEIGHT - 150, "Supplier Details")

        c.drawString(40, PAGE_HEIGHT - 160, f"To:")
        c.drawString(130, PAGE_HEIGHT - 160, f"{to_name}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 162, line_end, PAGE_HEIGHT - 162)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 160, f"Designation:")
        c.drawString(po_line_start, PAGE_HEIGHT - 160, f"{designation}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 162, PAGE_WIDTH - 50, PAGE_HEIGHT - 162)

        c.drawString(40, PAGE_HEIGHT - 170, f"Company:")
        c.drawString(130, PAGE_HEIGHT - 170, f"{company}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 172, PAGE_WIDTH - 50, PAGE_HEIGHT - 172)

        c.drawString(40, PAGE_HEIGHT - 180, f"Telephone No.:")
        c.drawString(130, PAGE_HEIGHT - 180, f"{telephone}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 182, line_end, PAGE_HEIGHT - 182)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 180, f"Email:")
        c.drawString(po_line_start, PAGE_HEIGHT - 180, f"{email}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 182, PAGE_WIDTH - 50, PAGE_HEIGHT - 182)

        c.drawString(40, PAGE_HEIGHT - 190, f"Fax No:")
        c.drawString(130, PAGE_HEIGHT - 190, f"{fax}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 192, line_end, PAGE_HEIGHT - 192)

        po_line_start = PAGE_WIDTH / 2 + 70
        c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 190, f"Mobile No.:")
        c.drawString(po_line_start, PAGE_HEIGHT - 190, f"{mobile}")
        c.setLineWidth(0.3)
        c.line(po_line_start, PAGE_HEIGHT - 192, PAGE_WIDTH - 50, PAGE_HEIGHT - 192)

        c.drawString(40, PAGE_HEIGHT - 200, f"Address:")
        c.drawString(130, PAGE_HEIGHT - 200, f"{address}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 202, PAGE_WIDTH - 50, PAGE_HEIGHT - 202)

        c.drawString(40, PAGE_HEIGHT - 220, f"Subject:")
        c.drawString(130, PAGE_HEIGHT - 220, f"{subject}")
        c.setLineWidth(0.3)
        line_end = (PAGE_WIDTH / 2) - 10
        c.line(130, PAGE_HEIGHT - 222, PAGE_WIDTH - 50, PAGE_HEIGHT - 222)
        c.drawString(40, PAGE_HEIGHT - 240, "Harmonized System (HS) Code       : AS PER BELOW")
        c.drawString(40, PAGE_HEIGHT - 260, "Import Permit (Internal Use Only) : -")
        c.drawString(40, PAGE_HEIGHT - 280, "Special Import Requirements       : -")
        c.drawString(40, PAGE_HEIGHT - 300, "Supplier Offer Reference          : FR20250529-JW")
        c.drawString(40, PAGE_HEIGHT - 320, "Purchase Details:")
        # -------- PURCHASE DETAILS TABLE --------
        # Convert long text fields to Paragraphs so they wrap
        wrapped_items = []
        for row in st.session_state.foreign_line_items:
            wrapped_row = row.copy()
            # Product Description is column index 2
            wrapped_row[2] = Paragraph(str(wrapped_row[2]), century_style)
            wrapped_items.append(wrapped_row)

        # Create table data with header + wrapped content
        purchase_data = [
        ["S.No.", "HS Code", "Product Description", "UoM", "Qty", "Unit Cost", "Total Price"]
        ] + wrapped_items

        # Build the table (no fixed rowHeights → auto adjusts)
        purchase_table = Table(
        purchase_data,
        colWidths=[40, 60, 180, 40, 40, 60, 60]
        )

        purchase_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "CenturyGothicBold"), # header bold
        ("FONTNAME", (0,1), (-1,-1), "CenturyGothic"),    # body normal
        ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("ALIGN", (4,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP")  # so wrapped text starts at top
        ]))

        # Draw table
        y = PAGE_HEIGHT - 330
        purchase_table.wrapOn(c, 40, y)
        purchase_table.drawOn(c, 40, y - purchase_table._height)

        y = y - purchase_table._height

        y-=20
        c.drawString(320, y, "Grand Total")
        c.drawString(400, y, "USD")
        c.drawString(PAGE_WIDTH - 100, y, f"{grand_total}")
        y-=10
        c.setLineWidth(0.3)
        c.line(40, y, PAGE_WIDTH - 40, y)

        y -= 30
        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, y, "Note: Please mention the product name and HS code exactly the same in all documents")
        y -= 12
        c.drawString(40, y, "Best Regards")
        y -= 12
        c.drawString(40, y, "On behalf of Meta Solutions Industrial Company")

        # Approvals
        y -= 20
        c.setFont("CenturyGothic", 7.5)
        c.drawString(40, y, "Prepared & checked by:")
        c.drawString(40, y-12, "AMIR RODRIGUEZ")
        c.drawString(180, y, "Reviewed by:")
        c.drawString(180, y-12, "WASIUR REHMAN KHAN")
        c.drawString(320, y, "Authorized by")
        c.drawString(320, y-12, "DR. VIMAL PATEL")
        c.drawString(460, y, "Approved by:")
        c.drawString(460, y-12, " ANVER SADATH")

        y -= 24
        c.setFont("CenturyGothic", 7)
        c.drawString(40, y, "Procurement Manager")
        c.drawString(180, y, "Finance Manager")
        c.drawString(320, y, "General Manager")
        c.drawString(460, y, "Chairman & Managing Director")

        y= 70
        c.drawString(40, y, "Please confirm the purchase order and send the scanned copy by email.")
        y-=30
        c.setLineWidth(0.3)
        c.line(40, y+10, 130, y+10)
        c.drawString(50, y, "Name")
        c.line(170, y+10, 360, y+10)
        c.drawString(180, y, "Supplier Authorized Signature and Date")
        c.line(450, y+10, 550, y+10)
        c.drawString(460, y, "Company Seal")

        available_width = PAGE_WIDTH - (2 * 40)
        if os.path.exists(LOGO_PATH_FOOTER):
            c.drawImage(LOGO_PATH_FOOTER, 40, -30, width=available_width, preserveAspectRatio=True, mask='auto')

        # Save PDF
        c.showPage()
        c.save()

        # Download button in Streamlit
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name="foreign_po.pdf", mime="application/pdf")