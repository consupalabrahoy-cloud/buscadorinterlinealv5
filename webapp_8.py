import streamlit as st
import re
import requests

def parse_interlinear_text(lines):
    """
    Parsea las líneas del texto para agrupar versículos en pares español-griego.
    """
    verses = []
    current_heading = "Sin encabezado"
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Detectar encabezado de sección (ej. "Mateo 1")
        if re.match(r'^[^\d]+\s\d+$', line):
            current_heading = line
            i += 1
            continue

        # Detectar la línea en español
        spanish_line_match = re.match(r'^(\d+)\s(.*)$', line)
        if spanish_line_match:
            verse_number = spanish_line_match.group(1)
            spanish_text = spanish_line_match.group(2).strip()

            # Capturar líneas adicionales de texto español si el versículo se extiende
            j = i + 1
            while j < len(lines) and not re.match(r'^\d+', lines[j].strip()) and lines[j].strip():
                spanish_text += " " + lines[j].strip()
                j += 1
            
            # La siguiente línea numerada es la griega
            if j < len(lines):
                greek_line_match = re.match(r'^\d+\s(.+)$', lines[j].strip())
                if greek_line_match:
                    greek_text = greek_line_match.group(1).strip()
                    verses.append({
                        "heading": current_heading,
                        "verse": verse_number,
                        "spanish": spanish_text,
                        "greek": greek_text
                    })
                    i = j + 1
                    continue
        
        i += 1
    return verses

def find_occurrences(parsed_verses, search_term):
    """
    Busca un término en los versos ya parseados.
    """
    occurrences = []
    
    for verse in parsed_verses:
        # Búsqueda en español
        if search_term.lower() in verse['spanish'].lower():
            occurrences.append({
                "heading": verse['heading'],
                "verse": verse['verse'],
                "spanish_text": verse['spanish'],
                "greek_text": verse['greek'],
                "found_word": search_term,
                "language": "Español"
            })
        
        # Búsqueda en griego
        if search_term.lower() in verse['greek'].lower():
            # Evita duplicar si la palabra está en ambos idiomas
            if search_term.lower() not in verse['spanish'].lower():
                occurrences.append({
                    "heading": verse['heading'],
                    "verse": verse['verse'],
                    "spanish_text": verse['spanish'],
                    "greek_text": verse['greek'],
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
        placeholder="Ejemplo: σπ o libertad"
    )

    st.markdown("---")
    
    if st.button("Buscar y analizar"):
        if not search_term:
            st.warning("Por favor, ingresa una secuencia de letras a buscar.")
        else:
            try:
                lines = file_content.splitlines()
                all_verses = parse_interlinear_text(lines)
                all_occurrences = find_occurrences(all_verses, search_term)
                
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
