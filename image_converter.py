import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import sys
import threading
import ctypes

try:
    myappid = 'Conversor de Imagenes' # Un nombre único cualquiera
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ImageConverterApp(ctk.CTk):
    """
    Clase principal de la aplicación de conversión de imágenes.
    Hereda de customtkinter.CTk para construir la interfaz gráfica moderna.
    """
    def __init__(self):
        """
        Inicializa la ventana principal de la aplicación, configura el título,
        dimensiones, variables de estado y construye todos los widgets de la UI.
        """
        super().__init__()

        self.title("Conversor de Imagenes")
        self.geometry("500x500")

        try:
            self.after(200, lambda: self.iconbitmap(resource_path("logo.ico")))
        except:
            pass

        # Variable de estado para almacenar las rutas de las imágenes seleccionadas
        self.input_paths = []
        standard_width = 300 # ancho estándar para uniformidad en los widgets

        # UI Layout - Configuración de la interfaz
        self.label = ctk.CTkLabel(self, text="Conversor de Imagenes", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        # Botón para seleccionar archivos
        self.btn_open = ctk.CTkButton(self, text="Seleccionar Imagenes", 
                                    width=standard_width,
                                    command=self.select_images)
        self.btn_open.pack(pady=10)

        # Entrada para configurar la resolución vertical (opcional)
        self.entry_height = ctk.CTkEntry(self, 
                                        width=standard_width, 
                                        placeholder_text="Resolución vertical (ej: 720)")
        self.entry_height.pack(pady=10)

        # Menú desplegable para elegir el formato de salida
        self.format_menu = ctk.CTkOptionMenu(self, 
                                            width=standard_width,
                                            values=["JPG", "PNG", "GIF", "BMP", "WEBP", "AVIF"])
        self.format_menu.pack(pady=10)
        self.format_menu.set("WEBP")
        
        # Botón para iniciar la conversión
        self.btn_convert = ctk.CTkButton(self, text="Convertir y guardar", 
                                        width=standard_width,
                                        command=self.start_conversion_thread, 
                                        fg_color="green", hover_color="dark green")
        self.btn_convert.pack(pady=10)

        # Etiqueta de estado para feedback al usuario
        self.status_label = ctk.CTkLabel(self, text="No se han seleccionado archivos")
        self.status_label.pack(pady=10)

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(self, width=standard_width)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

    def select_images(self):
        """
        Abre un cuadro de diálogo del sistema para seleccionar una o varias imágenes.
        Actualiza la variable `self.input_paths` y la etiqueta de estado con la cantidad seleccionada.
        """
        files = filedialog.askopenfilenames(
            title="Selecciona las imagenes a convertir",
            filetypes=[("Imagenes", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp;*.avif;*.tiff")]
        )
        if files: 
            self.input_paths = files
            self.status_label.configure(text=f"{len(files)} archivos seleccionados")
            self.progress_bar.set(0) # Resetear barra al elegir nuevos archivos
        else:
            self.status_label.configure(text="No se seleccionaron archivos")

    def get_unique_path(self, folder, name, ext):
        """
        Genera una ruta de archivo única dentro de una carpeta.
        Si el archivo ya existe, agrega un contador al final del nombre (ej: foto (1).jpg)
        para evitar sobrescribir archivos existentes.

        Args:
            folder (str): Ruta de la carpeta de destino.
            name (str): Nombre base del archivo (sin extensión).
            ext (str): Extensión del archivo (ej: 'jpg').

        Returns:
            str: Ruta absoluta completa y única para guardar el archivo.
        """
        # Genera una ruta única para no sobreescribir
        counter = 1
        final_path = os.path.join(folder, f"{name}.{ext}")
        while os.path.exists(final_path):
            final_path = os.path.join(folder, f"{name} ({counter}).{ext}")
            counter += 1
        return final_path

    def convert_images(self):
        """
        Lógica principal de conversión de imágenes.
        Itera sobre las imágenes seleccionadas, aplica reescalado si es necesario,
        convierte el formato y guarda el archivo resultante.
        Actualiza la barra de progreso en cada paso.
        """
        if not self.input_paths:
            messagebox.showwarning("Error", "No se seleccionaron archivos")
            return

        # Solicitar al usuario dónde guardar los resultados
        output_folder = filedialog.askdirectory(title="Carpeta de destino")
        if not output_folder:
            return
        
        self.btn_convert.configure(state="disabled") # Deshabilitar botón durante el proceso
        target_format = self.format_menu.get()
        user_height = self.entry_height.get()
        total_files = len(self.input_paths)

        try:
            for index, path in enumerate(self.input_paths):
                img = Image.open(path)

                # Reescalado manteniendo proporción basada en la altura (ALTO)
                if user_height.isdigit():
                    target_h = int(user_height)
                    orig_w, orig_h = img.size
                    # Calcular el nuevo ancho manteniendo el aspect ratio
                    ratio = target_h / float(orig_h)
                    new_width = int(float(orig_w) * float(ratio))
                    # Usar LANCZOS para un reescalado de alta calidad
                    img = img.resize((new_width, target_h), Image.Resampling.LANCZOS)

                # Obtener nombre original para usarlo en el destino
                filename = os.path.basename(path)
                name_wo_ext = os.path.splitext(filename)[0]
                
                # Si se cambió el tamaño, indicarlo en el nombre
                if user_height.isdigit():
                    name_wo_ext += f"{name_wo_ext}_{user_height}"
                target_ext = target_format.lower()
                
                # Obtener ruta segura para guardar
                final_path = self.get_unique_path(output_folder, name_wo_ext, target_ext)
                
                # Conversión necesaria: JPG no soporta transparencia (RGBA) -> convertir a RGB
                if target_format in ["JPG", "JPEG", "WEBP"] and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Mapeo de formato para Pillow (JPG usa key 'JPEG')
                save_format = "JPEG" if target_format == "JPG" else target_format
                img.save(final_path, save_format)

                # Actualizar progreso
                progress = (index + 1) / total_files
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Procesando {index + 1} de {total_files}...")

            messagebox.showinfo("Completado", f"Proceso finalizado: {total_files} imágenes.")
            self.input_paths = [] # Limpiar selección tras finalizar

        except Exception as e:
            messagebox.showerror("Error", f"Detalle: {str(e)}")

        finally:
            # Restaurar estado del botón y etiqueta
            self.btn_convert.configure(state="normal")
            self.status_label.configure(text="Proceso completado")

    def start_conversion_thread(self):
        """
        Inicia la conversión en un hilo secundario (daemon).
        Esto es crucial para que la interfaz gráfica no se congele durante el procesamiento.
        """
        thread = threading.Thread(target=self.convert_images, daemon=True)
        thread.start()

if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()