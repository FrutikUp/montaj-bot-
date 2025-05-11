from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# Регистрируем шрифт
pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

# Пример генерации PDF
c = canvas.Canvas("output.pdf")
c.setFont("DejaVuSans", 12)
c.drawString(100, 750, "Пример коммерческого предложения")
c.save()
