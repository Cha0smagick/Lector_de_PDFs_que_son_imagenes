import streamlit as st
import fitz
from PIL import Image
import textwrap
import google.generativeai as genai
import time
import base64

# Configurar la clave de la API de Gemini
genai.configure(api_key="AIzaSyA4k6JoFNZsf8L1ixLMMRjEMoBPns5SHZk")

# Función para mostrar texto con formato Markdown
def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# Función para convertir un archivo PDF en una lista de imágenes
def pdf_to_images(pdf_bytes):
    doc = fitz.open("pdf", pdf_bytes)
    images = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        image = page.get_pixmap()
        img = Image.frombytes("RGB", [image.width, image.height], image.samples)
        images.append(img)

    return images

# Función para generar contenido utilizando la API de Gemini
def generate_gemini_content(prompt, model_name='gemini-pro-vision', image=None):
    model = genai.GenerativeModel(model_name)
    if not image:
        st.warning("Por favor, añade una imagen para usar el modelo gemini-pro-vision.")
        return None

    try:
        response = model.generate_content([prompt, image])
        return response
    except Exception as e:
        st.error(f"Error en la solicitud a Gemini: {str(e)}")
        return None

# Función principal
def main():
    st.title("PDF to Image Converter with Gemini API")

    uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])

    if uploaded_file is not None:
        st.success("¡Archivo PDF subido exitosamente!")

        # Leer el archivo PDF como bytes
        pdf_bytes = uploaded_file.read()

        # Convertir el PDF a una lista de imágenes
        images = pdf_to_images(pdf_bytes)

        # Preguntas y respuestas utilizando Gemini
        prompt = st.text_area("Ingresa tu pregunta:")

        # Contenedor para mostrar imágenes y respuestas
        container = st.container()

        # Mostrar las imágenes horizontalmente
        image_display = '<div style="overflow-x: scroll; white-space: nowrap;">'
        for i, img in enumerate(images):
            image_display += f'<img src="data:image/png;base64,{base64.b64encode(img.tobytes()).decode("utf-8")}" alt="Page {i + 1}" style="max-width: 100%; margin-right: 10px;">'
        image_display += '</div>'
        container.markdown(image_display, unsafe_allow_html=True)

        # Espacio entre imágenes y respuestas
        container.markdown("<br>", unsafe_allow_html=True)

        # Preguntar y obtener respuestas para cada imagen
        for i, img in enumerate(images):
            container.markdown(f"### Respuestas para la Página {i + 1}:")

            # Generar contenido basado en la pregunta y la imagen
            response = generate_gemini_content(prompt, model_name='gemini-pro-vision', image=img)

            # Mostrar la respuesta en Markdown si está disponible
            if response and response.candidates:
                parts = response.candidates[0].content.parts
                generated_text = parts[0].text if parts else "No se generó contenido."
                container.markdown(to_markdown(generated_text))
            else:
                container.warning("No se encontraron candidatos en la respuesta.")

            # Esperar 10 segundos antes de la siguiente solicitud
            time.sleep(10)

if __name__ == "__main__":
    main()