# Image Converter

Una aplicación de escritorio moderna y sencilla para convertir imágenes, construida con Python y CustomTkinter.

##  Características

- **Interfaz Moderna**: Utiliza `customtkinter` para una apariencia limpia y soporte de modo oscuro/claro.
- **Procesamiento de Imágenes**: Potenciado por `Pillow` para soportar múltiples formatos de imagen.
- **Portabilidad**: Configurado para ser empaquetado fácilmente como ejecutable de Windows.

##  Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/EnriqueKloosterman/image_converter.git
   cd image_converter
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

##  Uso

Ejecuta el script principal para iniciar la aplicación:

```bash
python main.py
```
*(Nota: Si tu archivo principal tiene otro nombre, por favor actualiza este comando).*

##  Crear Ejecutable (.exe)

Este proyecto incluye `pyinstaller` para generar un ejecutable independiente (sin necesidad de instalar Python en la máquina destino).

```bash
pyinstaller --noconsole --onefile main.py
```

El archivo `.exe` se generará en la carpeta `dist`.