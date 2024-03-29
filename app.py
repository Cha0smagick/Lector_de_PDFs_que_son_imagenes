import streamlit as st
import fitz
from PIL import Image
import textwrap
import google.generativeai as genai
import time
import base64

# Configurar la clave de la API de Gemini
genai.configure(api_key="your_google_api_key")

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

# Función para descargar las respuestas acumuladas como un archivo .txt
def download_responses_as_txt(prompt, all_responses):
    file_content = f"Pregunta: {prompt}\n\n{all_responses}"

    # Descargar el archivo
    b64 = base64.b64encode(file_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="respuestas.txt">Descargar Respuestas</a>'
    st.markdown(href, unsafe_allow_html=True)

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

        if st.button("Generar Respuestas") and prompt:
            # Contenedor para mostrar imágenes y respuestas
            container = st.container()
            
            # Variable para acumular respuestas
            all_responses = ""

            # Mostrar las imágenes horizontalmente
            for i, img in enumerate(images):
                container.image(img, caption=f"Página {i + 1}", use_column_width=True)

                # Generar contenido basado en la pregunta y la imagen
                response = generate_gemini_content(prompt, model_name='gemini-pro-vision', image=img)

                # Mostrar la respuesta en Markdown si está disponible
                if response and response.candidates:
                    for i, parts in enumerate(response.candidates[0].content.parts):
                        generated_text = parts.text if parts else "No se generó contenido."
                        container.markdown(f"Respuesta {i + 1}:\n{to_markdown(generated_text)}")

                        # Acumular respuestas
                        all_responses += f"\nRespuesta {i + 1}:\n{generated_text}\n"

                else:
                    container.warning("No se encontraron candidatos en la respuesta.")

                # Esperar 10 segundos antes de la siguiente solicitud
                time.sleep(10)

            # Botón de descarga
            download_responses_as_txt(prompt, all_responses)

if __name__ == "__main__":
    main()
