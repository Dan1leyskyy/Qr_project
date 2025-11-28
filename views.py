from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import QRForm
from .qr_utils import QRGenerator, QRGenerationError
import base64


@csrf_exempt
def index(request):
    qr_image = None
    error = None
    selected_format = 'PNG'

    if request.method == 'POST':
        form = QRForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            selected_format = form.cleaned_data['format_type']
            try:
                # Генерируем QR-код
                buf = QRGenerator.generate_qr_code(text, selected_format)

                # Для растровых форматов показываем превью (конвертируем в PNG для отображения)
                if selected_format in ['PNG', 'JPEG', 'BMP', 'TIFF']:
                    image_base64 = base64.b64encode(buf.getvalue()).decode('ascii')
                    qr_image = image_base64
                else:
                    # Для векторных форматов показываем сообщение
                    qr_image = "vector_format"

            except QRGenerationError as e:
                error = str(e)
    else:
        form = QRForm()

    return render(request, 'qr_generator/index.html', {
        'form': form,
        'qr_image': qr_image,
        'error': error,
        'selected_format': selected_format,
        'supported_formats': QRGenerator.get_supported_formats()
    })


@csrf_exempt
def download_qr(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        format_type = request.POST.get('format_type', 'PNG')
        if text:
            buf = QRGenerator.generate_qr_code(text, format_type)
            mime_type = QRGenerator.get_mime_type(format_type)
            file_extension = QRGenerator.get_file_extension(format_type)

            response = HttpResponse(buf.getvalue(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="qrcode.{file_extension}"'
            return response
    return HttpResponse(status=400)
