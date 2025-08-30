import streamlit as st
import re
import requests

def find_and_display_occurrences(lines, search_term):
    """
    Encuentra y muestra todas las ocurrencias de una subcadena en las líneas de texto,
    incluyendo la línea en español y la línea en griego,
    y además el encabezado de la sección y el número de versículo.
    """
    occurrences = []
    current_heading = "Sin encabezado"
    
    # Itera sobre las líneas de dos en dos para emparejar español (i) y griego (i+1)
    for i in range(0, len(lines), 2):
        # Ignora las líneas que no siguen el patrón
        if not lines[i].strip():
            continue

        # 1. Identifica los encabezados de sección
        if re.match(r'^[^\d]+\s\d+$', lines[i].strip()):
            current_heading = lines[i].strip()
            continue
            
        # 2. Busca el patrón de versículo y texto en español
        spanish_line_match = re.match(r'^(\d+)\s(.+)$', lines[i].strip())
        
        # 3. Si se encuentra una línea en español y hay una siguiente línea (griego)
        if spanish_line_match and i + 1 < len(lines):
            verse_number = spanish_line_match.group(1)
            spanish_text = spanish_line_match.group(2)
            greek_line_raw = lines[i + 1].strip()
            
            # --- Lógica de búsqueda en español ---
            if search_term.lower() in spanish_text.lower():
                occurrences.append({
                    "heading": current_heading,
                    "verse": verse_number,
                    "spanish_text": spanish_text,
                    "greek_text": greek_line_raw,
                    "found_word": search_term,
                    "language": "Español"
                })

            # --- Lógica de búsqueda en griego ---
            words_in_greek_line = re.findall(r'[\w’]+', greek_line_raw)
            for word in words_in_greek_line:
                if search_term.lower() in word.lower():
                    occurrences.append({
                        "heading": current_heading,
                        "verse": verse_number,
                        "spanish_text": spanish_text,
                        "greek_text": greek_line_raw,
                        "found_word": word,
                        "language": "Griego"
                    })
    
    return occurrences

# --- Lógica para cargar el archivo automáticamente desde GitHub ---
# URL del archivo de texto en formato "raw" en tu repositorio de GitHub.
GITHUB_RAW_URL = "https://raw.githubusercontent.com/consupalabrahoy-cloud/buscadorinterlinealv5/refs/heads/main/NuevoTestamentoInterlineal.txt"

@st.cache_data(ttl=3600)
def load_text_from_github(url):
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
    """
    Función principal de la aplicación Streamlit.
    Configura la interfaz y maneja la lógica.
    """
    st.title("Buscador avanzado en texto interlineal 🇬🇷🇪🇸")
    st.markdown("---")
    
    st.write("Esta aplicación busca palabras o secuencias de letras en español o griego en un archivo de texto interlineal y muestra las ocurrencias y su contexto. El archivo se carga automáticamente desde GitHub. 🔍")

    # Carga el contenido del archivo
    file_content = load_text_from_github(GITHUB_RAW_URL)

    if file_content is None:
        return # Detiene la ejecución si el archivo no se pudo cargar

    # Widget para la entrada de la subcadena a buscar
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
                # Lee el contenido del archivo y lo divide en líneas
                lines = file_content.splitlines()

                # Elimina las líneas vacías para un mejor procesamiento
                lines = [line for line in lines if line.strip()]

                # Llama a la función principal para buscar y obtener las ocurrencias
                all_occurrences = find_and_display_occurrences(lines, search_term)
                
                # Filtra las ocurrencias por idioma
                greek_occurrences = [o for o in all_occurrences if o["language"] == "Griego"]
                spanish_occurrences = [o for o in all_occurrences if o["language"] == "Español"]

                if not all_occurrences:
                    st.warning(f"No se encontraron palabras que contengan '{search_term}' en el archivo.")
                else:
                    # Crea las pestañas para mostrar los resultados
                    tab_greek, tab_spanish = st.tabs([
                        f"Resultados en Griego ({len(greek_occurrences)})",
                        f"Resultados en Español ({len(spanish_occurrences)})"
                    ])

                    # Muestra los resultados en la pestaña de Griego
                    with tab_greek:
                        if greek_occurrences:
                            st.subheader("Ocurrencias y su contexto en griego:")
                            for occurrence in greek_occurrences:
                                st.markdown(f"**{occurrence['heading']}**")
                                st.markdown(f"{occurrence['verse']} {occurrence['spanish_text']}")
                                st.markdown(f"{occurrence['verse']} {occurrence['greek_text']}")
                                st.markdown(f"**Palabra encontrada:** `{occurrence['found_word']}`")
                                st.markdown("---")
                        else:
                            st.info("No se encontraron coincidencias en griego.")

                    # Muestra los resultados en la pestaña de Español
                    with tab_spanish:
                        if spanish_occurrences:
                            st.subheader("Ocurrencias y su contexto en español:")
                            for occurrence in spanish_occurrences:
                                st.markdown(f"**{occurrence['heading']}**")
                                st.markdown(f"{occurrence['verse']} {occurrence['spanish_text']}")
                                st.markdown(f"{occurrence['verse']} {occurrence['greek_text']}")
                                st.markdown(f"**Palabra encontrada:** `{occurrence['found_word']}`")
                                st.markdown("---")
                        else:
                            st.info("No se encontraron coincidencias en español.")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

# Ejecuta la función principal si el script se ejecuta directamente
if __name__ == "__main__":
    main()
