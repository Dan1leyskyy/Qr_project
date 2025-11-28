import io
import qrcode
from PIL import Image
import svgwrite
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib.units import mm
import base64


class QRGenerationError(Exception):
    """Кастомное исключение для ошибок генерации QR-кодов"""
    pass


class QRGenerator:
    @staticmethod
    def generate_qr_code(text: str, format_type: str = 'PNG') -> io.BytesIO:
        """
        Генерирует QR-код для переданного текста/ссылки
        Поддерживаемые форматы: PNG, JPEG, BMP, TIFF, SVG, PDF, EPS
        """
        try:
            format_type = format_type.upper()

            if format_type in ['SVG', 'PDF', 'EPS']:
                return QRGenerator._generate_vector_qr(text, format_type)
            else:
                return QRGenerator._generate_raster_qr(text, format_type)

        except Exception as e:
            raise QRGenerationError(f"Ошибка при генерации QR-кода: {str(e)}")

    @staticmethod
    def _generate_raster_qr(text: str, format_type: str) -> io.BytesIO:
        """Генерация растровых форматов"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Конвертируем в RGB для форматов, которые не поддерживают прозрачность
        if format_type in ['JPEG', 'BMP']:
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, 'white')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

        buf = io.BytesIO()
        img.save(buf, format=format_type)
        buf.seek(0)
        return buf

    @staticmethod
    def _generate_vector_qr(text: str, format_type: str) -> io.BytesIO:
        """Генерация векторных форматов"""
        if format_type == 'SVG':
            return QRGenerator._generate_svg_qr(text)
        elif format_type in ['PDF', 'EPS']:
            return QRGenerator._generate_pdf_eps_qr(text, format_type)
        else:
            raise QRGenerationError(f"Неподдерживаемый векторный формат: {format_type}")

    @staticmethod
    def _generate_svg_qr(text: str) -> io.BytesIO:
        """Генерация SVG формата"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        # Создаем SVG с помощью qrcode
        img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        return buf

    @staticmethod
    def _generate_pdf_eps_qr(text: str, format_type: str) -> io.BytesIO:
        """Генерация PDF и EPS форматов"""
        buf = io.BytesIO()

        qr_code = QrCodeWidget(text)
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        d = Drawing(100, 100, transform=[100. / width, 0, 0, 100. / height, 0, 0])
        d.add(qr_code)

        if format_type == 'PDF':
            from reportlab.graphics import renderPDF
            renderPDF.drawToFile(d, buf, fmt='PDF')
        else:  # EPS
            from reportlab.graphics import renderPS
            renderPS.drawToFile(d, buf, fmt='EPS')

        buf.seek(0)
        return buf

    @staticmethod
    def generate_qr_to_file(text: str, filename: str, format_type: str = 'PNG') -> None:
        """
        Генерирует QR-код и сохраняет в файл
        """
        buf = QRGenerator.generate_qr_code(text, format_type)
        with open(filename, 'wb') as f:
            f.write(buf.getvalue())

    @staticmethod
    def get_supported_formats():
        """Возвращает список поддерживаемых форматов"""
        return {
            'PNG': 'PNG (Растровый)',
            'JPEG': 'JPEG (Растровый)',
            'BMP': 'BMP (Растровый)',
            'TIFF': 'TIFF (Растровый)',
            'SVG': 'SVG (Векторный)',
            'PDF': 'PDF (Векторный)',
            'EPS': 'EPS (Векторный)'
        }

    @staticmethod
    def get_mime_type(format_type: str) -> str:
        """Возвращает MIME type для формата"""
        mime_types = {
            'PNG': 'image/png',
            'JPEG': 'image/jpeg',
            'BMP': 'image/bmp',
            'TIFF': 'image/tiff',
            'SVG': 'image/svg+xml',
            'PDF': 'application/pdf',
            'EPS': 'application/postscript'
        }
        return mime_types.get(format_type, 'image/png')

    @staticmethod
    def get_file_extension(format_type: str) -> str:
        """Возвращает расширение файла для формата"""
        extensions = {
            'PNG': 'png',
            'JPEG': 'jpg',
            'BMP': 'bmp',
            'TIFF': 'tiff',
            'SVG': 'svg',
            'PDF': 'pdf',
            'EPS': 'eps'
        }
        return extensions.get(format_type, 'png')