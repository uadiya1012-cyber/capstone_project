import csv
import io
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from expenses.models import Expense


@login_required
def export_csv(request):
    """Export all of the user's expenses as a CSV file."""
    expenses = Expense.objects.filter(user=request.user).select_related('category', 'budget').order_by('-date', '-created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    today = datetime.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="expenses_{request.user.username}_{today}.csv"'

    # UTF-8 BOM for Excel compatibility
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Огноо', 'Тайлбар', 'Категори', 'Дүн', 'Төсөв', 'Давтамжтай', 'Баримт'])

    total = Decimal('0.00')
    for exp in expenses:
        is_income = exp.category.is_income if exp.category else False
        if not is_income:
            total += exp.amount

        writer.writerow([
            exp.date.strftime('%Y-%m-%d'),
            exp.description or '-',
            exp.category.name if exp.category else '-',
            f'{exp.amount:.2f}',
            exp.budget.name if exp.budget else '-',
            'Тийм' if exp.is_recurring else 'Үгүй',
            'Тийм' if exp.receipt else 'Үгүй',
        ])

    writer.writerow([])
    writer.writerow(['', '', 'Нийт зарлага:', f'{total:.2f}', '', '', ''])

    return response


@login_required
def export_pdf(request):
    """Export a professional PDF report of the user's expenses."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        # Fallback: simple text-based PDF if reportlab is not installed
        return _export_pdf_fallback(request)

    # Register custom fonts for Cyrillic and Unicode support (Tugrik symbol)
    import os
    from django.conf import settings
    
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    regular_font_path = os.path.join(font_dir, 'Arial.ttf')
    bold_font_path = os.path.join(font_dir, 'Arial-Bold.ttf')
    
    font_name = 'Helvetica'
    font_name_bold = 'Helvetica-Bold'
    
    if os.path.exists(regular_font_path) and os.path.exists(bold_font_path):
        try:
            pdfmetrics.registerFont(TTFont('Arial', regular_font_path))
            pdfmetrics.registerFont(TTFont('Arial-Bold', bold_font_path))
            font_name = 'Arial'
            font_name_bold = 'Arial-Bold'
        except Exception:
            pass

    expenses = Expense.objects.filter(user=request.user).select_related('category', 'budget').order_by('-date', '-created_at')

    response = HttpResponse(content_type='application/pdf')
    today = datetime.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="expenses_{request.user.username}_{today}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=18,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    # Title
    elements.append(Paragraph(f"Expense Report - {request.user.username}", title_style))
    elements.append(Paragraph(f"Generated: {today}", subtitle_style))
    elements.append(Spacer(1, 10))

    # Table
    data = [['Date', 'Description', 'Category', 'Amount', 'Budget', 'Recurring']]

    total_expense = Decimal('0.00')
    total_income = Decimal('0.00')

    for exp in expenses:
        is_income = exp.category.is_income if exp.category else False
        if is_income:
            total_income += exp.amount
        else:
            total_expense += exp.amount

        data.append([
            exp.date.strftime('%Y-%m-%d'),
            (exp.description or '-')[:40],
            exp.category.name if exp.category else '-',
            f'{request.user.currency}{exp.amount:.2f}',
            exp.budget.name if exp.budget else '-',
            'Yes' if exp.is_recurring else 'No',
        ])

    data.append(['', '', '', '', '', ''])
    data.append(['', '', 'Total Expense:', f'{request.user.currency}{total_expense:.2f}', '', ''])
    data.append(['', '', 'Total Income:', f'{request.user.currency}{total_income:.2f}', '', ''])
    data.append(['', '', 'Balance:', f'{request.user.currency}{total_income - total_expense:.2f}', '', ''])

    col_widths = [60, 140, 80, 70, 70, 50]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -5), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -5), colors.HexColor('#f8f9fa')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -5), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -5), 0.5, colors.HexColor('#dee2e6')),
        ('FONTNAME', (2, -3), (3, -1), font_name_bold),
        ('FONTSIZE', (2, -3), (3, -1), 9),
        ('TOPPADDING', (0, -3), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def _export_pdf_fallback(request):
    """Simple text-based fallback when reportlab is not installed."""
    expenses = Expense.objects.filter(user=request.user).select_related('category').order_by('-date')

    response = HttpResponse(content_type='text/plain; charset=utf-8')
    today = datetime.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="expenses_{request.user.username}_{today}.txt"'

    lines = [
        f"=== Expense Report for {request.user.username} ===",
        f"Generated: {today}",
        "=" * 60,
        "",
    ]

    total = Decimal('0.00')
    for exp in expenses:
        is_income = exp.category.is_income if exp.category else False
        if not is_income:
            total += exp.amount
        lines.append(f"{exp.date}  |  {exp.description or '-':<30}  |  {exp.amount:>10.2f}")

    lines.append("")
    lines.append(f"{'Total Expense:':>45} {total:>10.2f}")

    response.write('\n'.join(lines))
    return response
