import streamlit as st
import re
import requests
import unicodedata

def find_occurrences(lines, search_term):
    """
    Encuentra todas las ocurrencias de un término de búsqueda en pares de líneas
    y devuelve una lista de resultados, asegurando el emparejamiento correcto.
    """
    occurrences = []
    current_heading = "Sin encabezado"
    
    # Itera sobre las líneas de dos en dos para emparejar español (i) y griego (i+1)
    for i in range(0, len(lines) - 1, 2):
        line1 = lines[i].strip()
        line2 = lines[i+1].strip()

        # Ignora las líneas vacías o los encabezados de sección
        if not line1:
            continue
        if re.match(r'^[^\d]+\s\d+$', line1):
            current_heading = line1
            continue
        
        # Identifica el versículo y las líneas de texto
        spanish_line_match = re.match(r'^(\d+)\s(.+)$', line1)
        if not spanish_line_match:
            continue
        
        verse_number = spanish_line_match.group(1)
        spanish_text = spanish_line_match.group(2).strip()
        greek_text = line2.strip()
        
        # Lógica de búsqueda separada por idioma
        # Búsqueda en español
        if search_term.lower() in spanish_text.lower():
            occurrences.append({
                "heading": current_heading,
                "verse": verse_number,
                "spanish_text": spanish_text,
                "greek_text": greek_text,
                "found_word": search_term,
                "language": "Español"
            })

        # Búsqueda en griego
        if search_term.lower() in greek_text.lower():
            # Evita duplicar resultados si la palabra se encuentra en ambos idiomas
            if search_term.lower() not in spanish_text.lower():
                occurrences.append({
                    "heading": current_heading,
                    "verse": verse_number,
                    "spanish_text": spanish_text,
                    "greek_text": greek_text,
                    "found_word": search_term,
                    "language": "Griego"
                })

    return occurrences

# --- Lógica para cargar el archivo automáticamente desde GitHub ---
# URL del archivo de texto en formato "raw" en tu repositorio de GitHub.
GITHUB_RAW_URL = "https://raw.githubusercontent.com/consupalabrahoy-cloud/buscadorinterlinealv5/refs/heads/main/NuevoTestamentoInterlineal.txt"

@st.cache_data(ttl=3600)
def load_text_from_github(url):
    """Carga el contenido de un archivo de texto desde una URL de GitHub."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Error al cargar el archivo desde GitHub. Código de estado: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar el archivo: {e}")
        return None

def main():
    """Función principal de la aplicación Streamlit."""
    st.title("Buscador avanzado en texto interlineal 🇬🇷🇪🇸")
    st.markdown("---")
    
    st.write("Esta aplicación busca palabras o secuencias de letras en español o griego en un archivo de texto interlineal y muestra las ocurrencias y su contexto. El archivo se carga automáticamente desde GitHub. 🔍")

    file_content = load_text_from_github(GITHUB_RAW_URL)

    if file_content is None:
        return

    search_term = st.text_input(
        "Ingresa la secuencia de letras a buscar:",
        placeholder="Ejemplo: σπ o am"
    )

    st.markdown("---")
    
    if st.button("Buscar y analizar"):
        if not search_term:
            st.warning("Por favor, ingresa una secuencia de letras a buscar.")
        else:
            try:
                lines = file_content.splitlines()
                lines = [line for line in lines if line.strip()]

                all_occurrences = find_occurrences(lines, search_term)
                
                if not all_occurrences:
                    st.warning(f"No se encontraron coincidencias que contengan '{search_term}' en el archivo.")
                else:
                    st.subheader(f"Resultados encontrados ({len(all_occurrences)}):")
                    for occurrence in all_occurrences:
                        st.markdown(f"**{occurrence['heading']}**")
                        st.markdown(f"{occurrence['verse']} {occurrence['spanish_text']}")
                        st.markdown(f"{occurrence['verse']} {occurrence['greek_text']}")
                        st.markdown(f"**Coincidencia encontrada en {occurrence['language']}:** `{occurrence['found_word']}`")
                        st.markdown("---")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

if __name__ == "__main__":
    main()
