import io, os
from datetime import datetime
 
from reportlab.lib.pagesizes   import A4
from reportlab.lib             import colors
from reportlab.lib.units       import mm
from reportlab.lib.styles      import ParagraphStyle
from reportlab.lib.enums       import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus        import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable,
)
from reportlab.pdfbase         import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
 
# ── Register Unicode fonts (cross-platform) ───────────────────────────────────
def _register_fonts():
    """
    Tries to register a Unicode TTF font that supports the ₹ symbol.
    Falls back through several known font locations.
    Returns (regular_font_name, bold_font_name)
    """
    candidates = [
        # Linux / Mac (DejaVu — most reliable ₹ support)
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         'DejaVu', 'DejaVu-Bold'),
 
        # Linux alternative
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
         '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
         'Liberation', 'Liberation-Bold'),
 
        # Windows — Arial supports ₹ from Windows 8+
        ('C:/Windows/Fonts/arial.ttf',
         'C:/Windows/Fonts/arialbd.ttf',
         'Arial-Uni', 'Arial-Uni-Bold'),
 
        # Windows fallback — Calibri
        ('C:/Windows/Fonts/calibri.ttf',
         'C:/Windows/Fonts/calibrib.ttf',
         'Calibri', 'Calibri-Bold'),
    ]
 
    for reg_path, bold_path, reg_name, bold_name in candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont(reg_name,  reg_path))
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                else:
                    bold_name = reg_name   # fall back to regular for bold
                print(f"[PDF] Using font: {reg_name} from {reg_path}")
                return reg_name, bold_name
            except Exception as e:
                print(f"[PDF] Font registration failed for {reg_name}: {e}")
                continue
 
    # Last resort — built-in Helvetica (₹ won't render but won't crash)
    print("[PDF] WARNING: No Unicode font found. ₹ may not render correctly.")
    return 'Helvetica', 'Helvetica-Bold'
 
FONT_REG, FONT_BOLD = _register_fonts()
 
 
# ── Colour palette ─────────────────────────────────────────────────────────────
C_GREEN_DARK  = colors.HexColor('#1a6b2f')
C_GREEN_MID   = colors.HexColor('#2e9e4f')
C_GREEN_LIGHT = colors.HexColor('#e8f5ec')
C_GREY_BG     = colors.HexColor('#f7f8f7')
C_GREY_LINE   = colors.HexColor('#e0e0e0')
C_GREY_ROW    = colors.HexColor('#fafafa')
C_GOLD        = colors.HexColor('#f5a623')
C_WHITE       = colors.white
C_BLACK       = colors.HexColor('#1a1a1a')
C_MUTED       = colors.HexColor('#555555')
C_LIGHT       = colors.HexColor('#888888')
C_GREEN_TEXT  = colors.HexColor('#e8f5ec')
 
 
# ── Style factory ──────────────────────────────────────────────────────────────
def _s(name, size, color, bold=False, align=TA_LEFT, leading=None, space_after=0):
    return ParagraphStyle(
        name,
        fontName    = FONT_BOLD if bold else FONT_REG,
        fontSize    = size,
        textColor   = color,
        alignment   = align,
        leading     = leading or size * 1.35,
        spaceAfter  = space_after,
    )
 
 
# ── Main PDF builder ───────────────────────────────────────────────────────────
def generate_invoice_pdf(customer, cart, subtotal, gst, discount, grand,
                         invoice_no, coupon, store):
    """
    Builds a professional A4 invoice PDF.
    Returns: bytes of the PDF file.
    """
    buffer = io.BytesIO()
    W, H   = A4
    MARGIN = 16 * mm
    CW     = W - 2 * MARGIN    # usable content width
 
    doc = SimpleDocTemplate(
        buffer,
        pagesize     = A4,
        leftMargin   = MARGIN,
        rightMargin  = MARGIN,
        topMargin    = MARGIN,
        bottomMargin = MARGIN,
        title        = f"D-mart Invoice {invoice_no}",
        author       = "D-mart Smart Billing",
    )
 
    date_str = datetime.now().strftime('%d %B %Y, %I:%M %p')
    story    = []
 
    # ═══════════════════════════════════
    #  1. HEADER  (dark green band)
    # ═══════════════════════════════════
    left_cell = [
        Paragraph('D-mart',                               _s('h1', 26, C_WHITE,      bold=True,  leading=30)),
        Paragraph('Fresh  ·  Quality  ·  Value',          _s('h2',  9, C_GREEN_TEXT, leading=12)),
        Spacer(1, 4),
        Paragraph(store['address'],                       _s('h3',  8, C_GREEN_TEXT, leading=11)),
        Paragraph(f"Tel: {store['phone']}   |   GSTIN: {store['gstin']}",
                                                          _s('h4',  8, C_GREEN_TEXT, leading=11)),
    ]
    right_cell = [
        Paragraph('TAX INVOICE',                          _s('r1',  8, C_GREEN_TEXT, align=TA_RIGHT, leading=10)),
        Paragraph(invoice_no,                             _s('r2', 16, C_WHITE,      bold=True, align=TA_RIGHT, leading=20)),
        Paragraph(date_str,                               _s('r3',  8, C_GREEN_TEXT, align=TA_RIGHT, leading=10)),
        Spacer(1, 6),
        Paragraph('PAID',                                 _s('r4',  9, C_WHITE,      bold=True, align=TA_RIGHT,
                                                              leading=11)),
    ]
 
    hdr = Table([[left_cell, right_cell]], colWidths=[CW * 0.62, CW * 0.38])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), C_GREEN_DARK),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',  (0,0), (0, -1), 14),
        ('RIGHTPADDING', (1,0), (1, -1), 14),
        ('TOPPADDING',   (0,0), (-1,-1), 14),
        ('BOTTOMPADDING',(0,0), (-1,-1), 14),
    ]))
    story.append(hdr)
 
    # ═══════════════════════════════════
    #  2. CUSTOMER + PAYMENT INFO
    # ═══════════════════════════════════
    addr = customer.get('address') or '—'
    cust = [
        Paragraph('BILL TO',                              _s('cl1',  7, C_MUTED,  leading=9)),
        Paragraph(customer['name'],                       _s('cl2', 13, C_BLACK,  bold=True, leading=16)),
        Paragraph(customer['phone'],                      _s('cl3',  9, C_MUTED,  leading=12)),
        Paragraph(customer['email'],                      _s('cl4',  9, C_MUTED,  leading=12)),
        Paragraph(addr,                                   _s('cl5',  9, C_MUTED,  leading=12)),
    ]
    pay = [
        Paragraph('PAYMENT',                              _s('pr1',  7, C_MUTED,  leading=9)),
        Paragraph('UPI — Paid',                           _s('pr2', 13, C_BLACK,  bold=True, leading=16)),
        Paragraph(f"UPI ID: {store.get('upi_id','dmart@upi')}",
                                                          _s('pr3',  9, C_MUTED,  leading=12)),
        Paragraph('Status: Successful',                   _s('pr4',  9, C_MUTED,  leading=12)),
    ]
 
    info = Table([[cust, pay]], colWidths=[CW * 0.60, CW * 0.40])
    info.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), C_GREY_BG),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',  (0,0), (0,-1),  14),
        ('RIGHTPADDING', (1,0), (1,-1),  14),
        ('TOPPADDING',   (0,0), (-1,-1), 12),
        ('BOTTOMPADDING',(0,0), (-1,-1), 12),
        ('LINEBELOW',    (0,0), (-1,-1), 0.5, C_GREY_LINE),
    ]))
    story.append(info)
    story.append(Spacer(1, 10))
 
    # ═══════════════════════════════════
    #  3. ITEMS TABLE
    # ═══════════════════════════════════
    # Column widths: #  | Product  | Qty | Unit Price | GST 5% | Amount
    cw = [8*mm, CW - 8*mm - 14*mm - 24*mm - 20*mm - 26*mm,
          14*mm, 24*mm, 20*mm, 26*mm]
 
    TH = lambda t, align=TA_LEFT: Paragraph(
        t, ParagraphStyle('th_'+t, fontName=FONT_BOLD, fontSize=8,
                          textColor=C_GREEN_DARK, alignment=align, leading=10))
 
    header_row = [
        TH('#'),
        TH('Product'),
        TH('Qty',        TA_CENTER),
        TH('Unit Price', TA_RIGHT),
        TH('GST 5%',     TA_RIGHT),
        TH('Amount',     TA_RIGHT),
    ]
    rows  = [header_row]
    tstyles = [
        ('BACKGROUND',   (0,0), (-1,0),  C_GREEN_LIGHT),
        ('LINEBELOW',    (0,0), (-1,0),  1.0, C_GREEN_MID),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ]
 
    def TD(t, align=TA_LEFT, bold=False, color=C_BLACK):
        return Paragraph(t, ParagraphStyle(
            'td_'+t[:6], fontName=FONT_BOLD if bold else FONT_REG,
            fontSize=9, textColor=color, alignment=align, leading=11))
 
    for i, item in enumerate(cart):
        r        = i + 1
        line_tot = item['total'] + item['tax_amount']
        prod_cell = [
            Paragraph(item['name'],
                      ParagraphStyle('pn', fontName=FONT_BOLD, fontSize=9,
                                     textColor=C_BLACK, leading=11)),
            Paragraph(f"{item['brand']}  ·  {item['code']}",
                      ParagraphStyle('pb', fontName=FONT_REG, fontSize=7,
                                     textColor=C_LIGHT, leading=9)),
        ]
        rows.append([
            TD(str(r)),
            prod_cell,
            TD(str(item['quantity']),           TA_CENTER),
            TD(f"Rs.{item['price']:.2f}",       TA_RIGHT),
            TD(f"Rs.{item['tax_amount']:.2f}",  TA_RIGHT),
            TD(f"Rs.{line_tot:.2f}",            TA_RIGHT, bold=True, color=C_GREEN_DARK),
        ])
        bg = C_WHITE if i % 2 == 0 else C_GREY_ROW
        tstyles += [
            ('BACKGROUND',   (0,r), (-1,r), bg),
            ('LINEBELOW',    (0,r), (-1,r), 0.3, C_GREY_LINE),
        ]
 
    tbl = Table(rows, colWidths=cw, repeatRows=1)
    tbl.setStyle(TableStyle(tstyles))
    story.append(tbl)
    story.append(Spacer(1, 8))
 
    # ═══════════════════════════════════
    #  4. TOTALS
    # ═══════════════════════════════════
    def TR(label, value, label_style=None, value_style=None):
        ls = label_style or _s('tl', 9, C_MUTED, align=TA_RIGHT)
        vs = value_style or _s('tv', 9, C_BLACK, bold=True, align=TA_RIGHT)
        return [Paragraph(label, ls), Paragraph(value, vs)]
 
    tot_rows = [
        TR('Subtotal (excl. GST)',   f"Rs.{subtotal:.2f}"),
        TR('GST @ 5%',               f"Rs.{gst:.2f}"),
    ]
    if discount > 0:
        code_lbl = coupon.get('code','') if coupon else ''
        tot_rows.append(TR(
            f"Coupon Discount ({code_lbl})",
            f"-Rs.{discount:.2f}",
            label_style=_s('cl', 9, C_GOLD,      bold=True, align=TA_RIGHT),
            value_style=_s('cv', 9, C_GREEN_MID, bold=True, align=TA_RIGHT),
        ))
 
    n = len(tot_rows)
    tot_rows.append(TR(
        'Total Paid',
        f"Rs.{grand:.2f}",
        label_style=_s('gl', 13, C_BLACK,      bold=True, align=TA_RIGHT),
        value_style=_s('gv', 15, C_GREEN_DARK, bold=True, align=TA_RIGHT),
    ))
 
    tot_tbl = Table(tot_rows, colWidths=[CW * 0.76, CW * 0.24])
    tot_tbl.setStyle(TableStyle([
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('LINEABOVE',     (0,n), (-1,n),  1.0, C_GREY_LINE),
        ('BACKGROUND',    (0,n), (-1,n),  C_GREEN_LIGHT),
        ('TOPPADDING',    (0,n), (-1,n),  10),
        ('BOTTOMPADDING', (0,n), (-1,n),  10),
    ]))
    story.append(tot_tbl)
    story.append(Spacer(1, 16))
 
    # ═══════════════════════════════════
    #  5. FOOTER
    # ═══════════════════════════════════
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_GREY_LINE))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Thank you for shopping at D-mart!',
        _s('ft', 11, C_GREEN_DARK, bold=True, align=TA_CENTER),
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'This is a computer-generated invoice. No signature required. '
        f'For queries contact {store["phone"]}.',
        _s('fs', 7, C_MUTED, align=TA_CENTER),
    ))
 
    doc.build(story)
    buffer.seek(0)
    return buffer.read()