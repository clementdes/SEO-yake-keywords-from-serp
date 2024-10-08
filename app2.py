import streamlit as st
import yake
import nltk
from nltk.corpus import stopwords
import pandas as pd
import os
import textrazor
import requests

# Initialisation de Streamlit
st.set_page_config(page_title="Extraction de mots-clés avec YAKE et TextRazor", layout="wide")

# Vérifier si le répertoire de données NLTK existe
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Télécharger les stopwords de nltk si nécessaire
nltk.data.path.append(nltk_data_dir)
try:
    nltk.download('stopwords', download_dir=nltk_data_dir)
except Exception as e:
    st.error(f"Erreur lors du téléchargement des stopwords : {e}")

# Lire les stopwords personnalisés à partir d'un fichier
def load_custom_stopwords(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        st.warning("Le fichier de stopwords personnalisé n'a pas été trouvé. Utilisation des stopwords par défaut.")
        return []

# Charger les stopwords personnalisés
custom_stopwords = load_custom_stopwords('custom_stopwords.txt')

# Fusionner les stopwords NLTK et les stopwords personnalisés
try:
    stopword_list = stopwords.words('french') + custom_stopwords
except LookupError:
    stopword_list = custom_stopwords
    st.warning("Impossible de charger les stopwords NLTK. Utilisation des stopwords personnalisés uniquement.")

# Titre de l'application
st.title("Extraction de mots-clés avec YAKE et TextRazor")

# Champ de texte pour l'entrée utilisateur
text_input = st.text_area("Entrez le texte ici :")

# Bouton pour extraire les mots-clés
generate_keywords_button = st.button("Extraire les mots-clés")

# Fonction pour extraire les mots-clés avec YAKE
def extract_keywords_with_yake(text, stopword_list, max_ngram_size=3, deduplication_threshold=0.9, num_of_keywords=100):
    kw_extractor = yake.KeywordExtractor(
        lan="fr",
        n=max_ngram_size,
        dedupLim=deduplication_threshold,
        top=num_of_keywords,
        features=None,
        stopwords=stopword_list
    )
    return kw_extractor.extract_keywords(text)

# Extraction des mots-clés à partir du texte fourni si le bouton est cliqué
if generate_keywords_button:
    if text_input:
        keywords = extract_keywords_with_yake(text_input, stopword_list)
        if keywords:
            st.subheader("Mots-clés extraits")
            # Créer un DataFrame pour les mots-clés
            keyword_data = []
            for kw, score in keywords:
                occurrence = text_input.lower().count(kw.lower())
                keyword_data.append([kw, occurrence, score])
            df_keywords = pd.DataFrame(keyword_data, columns=["Mot clé extrait", "Nombre d'occurrences", "Score"])

            # Afficher le tableau des mots-clés extraits
            st.dataframe(df_keywords)
        else:
            st.warning("Aucun mot-clé trouvé. Veuillez entrer un texte valide.")
    else:
        st.warning("Veuillez entrer du texte pour extraire les mots-clés.")

# Champ de saisie pour l'URL
url_input = st.text_input("Ou entrez l'URL ici :")

# Bouton pour extraire les mots-clés de l'URL
generate_keywords_url_button = st.button("Extraire les mots-clés de l'URL")

# Fonction pour analyser une URL avec TextRazor
def analyze_url_with_textrazor(url, api_key):
    if not api_key:
        st.error("Clé API TextRazor manquante.")
        return None
    textrazor.api_key = api_key
    client = textrazor.TextRazor(extractors=["entities", "topics"])
    client.set_cleanup_mode("cleanHTML")
    client.set_cleanup_return_cleaned(True)
    try:
        response = client.analyze_url(url)
        if response.ok:
            return response.cleaned_text
        else:
            st.error(f"Erreur lors de l'analyse de l'URL avec TextRazor : {response.error}")
            return None
    except textrazor.TextRazorAnalysisException as e:
        st.error(f"Erreur lors de l'analyse de l'URL avec TextRazor : {e}")
        return None

# Extraction des mots-clés à partir de l'URL fournie si le bouton est cliqué
if generate_keywords_url_button:
    if url_input:
        api_key = textrazor_api_key
        if not api_key:
            st.error("Veuillez entrer votre clé API TextRazor.")
        else:
            analyzed_text = analyze_url_with_textrazor(url_input, api_key)
            if analyzed_text:
                keywords = extract_keywords_with_yake(analyzed_text, stopword_list)
                if keywords:
                    st.subheader("Mots-clés extraits de l'URL")
                    # Créer un DataFrame pour les mots-clés
                    keyword_data = []
                    for kw, score in keywords:
                        occurrence = analyzed_text.lower().count(kw.lower())
                        keyword_data.append([kw, occurrence, score])
                    df_keywords = pd.DataFrame(keyword_data, columns=["Mot clé extrait", "Nombre d'occurrences", "Score"])

                    # Afficher le tableau des mots-clés extraits
                    st.dataframe(df_keywords)
                else:
                    st.warning("Aucun mot-clé trouvé. Veuillez entrer une URL valide.")
            else:
                st.warning("Impossible d'analyser le contenu de l'URL.")
    else:
        st.warning("Veuillez entrer une URL pour extraire les mots-clés.")

# Champs dans la sidebar
textrazor_api_key = st.sidebar.text_input("Entrez votre clé API TextRazor", type="password")
valueserp_api_key = st.sidebar.text_input("Entrez votre clé API ValueSERP", type="password")
keyword_input = st.sidebar.text_input("Entrez un mot-clé pour la recherche ValueSERP")
location_query = st.sidebar.text_input("Entrez une localisation pour les SERP")
user_url = st.sidebar.text_input("Votre URL")

# Bouton pour rechercher les locations avec l'API ValueSERP
if st.sidebar.button("Rechercher les locations"):
    if not valueserp_api_key:
        st.sidebar.error("Veuillez entrer votre clé API ValueSERP.")
    else:
        # Rechercher les locations avec l'API ValueSERP
        locations_url = f"https://api.valueserp.com/locations?api_key={valueserp_api_key}&q={location_query}"
        try:
            response = requests.get(locations_url)
            response.raise_for_status()
            locations = response.json().get("locations", [])
            if not locations:
                st.sidebar.warning("Aucune location trouvée.")
            else:
                location_options = [loc['full_name'] for loc in locations]
                selected_location = st.sidebar.selectbox("Sélectionnez une location", location_options)
                st.session_state['selected_location'] = selected_location
        except requests.RequestException as e:
            st.sidebar.error(f"Erreur lors de la récupération des locations : {e}")

# Afficher la location sélectionnée
if 'selected_location' in st.session_state:
    st.sidebar.write(f"Location sélectionnée : {st.session_state['selected_location']}")

# Fonction pour convertir le DataFrame en CSV
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

# Initialiser les variables
df = None
combined_text = ""

# Recherche ValueSERP avec le mot-clé et la location sélectionnée
if keyword_input and 'selected_location' in st.session_state:
    if not valueserp_api_key:
        st.error("Clé API ValueSERP manquante.")
    else:
        search_url = f"https://api.valueserp.com/search?api_key={valueserp_api_key}&q={keyword_input}&location={st.session_state['selected_location']}&num=30"
        try:
            search_response = requests.get(search_url)
            search_response.raise_for_status()
            search_results = search_response.json()

            # Extraire les URLs des résultats organiques
            organic_results = search_results.get('organic_results', [])
            urls = [result['link'] for result in organic_results]
            st.subheader("URLs des résultats organiques")
            st.write(urls[:30])  # Afficher uniquement les 30 premières URLs

            # Vérifier si l'URL de l'utilisateur est dans le top 30
            if user_url in urls[:30]:
                rank = urls.index(user_url) + 1
                st.write(f"Votre URL est classée #{rank} dans les résultats de Google.")

            # Analyser chaque URL avec TextRazor et extraire les mots-clés avec YAKE
            keyword_data = {}
            for rank, result in enumerate(organic_results[:10]):  # Limiter à 10 URLs
                url = result['link']
                text = analyze_url_with_textrazor(url, textrazor_api_key)
                if text:
                    combined_text += text + " "
                    keywords = extract_keywords_with_yake(text, stopword_list)
                    for kw, score in keywords:
                        if kw not in keyword_data:
                            keyword_data[kw] = {"total_occurrence": 0, "max_occurrence": 0, "max_url": "", "score": score, "ranking": rank, "occurrences": [0]*11}
                        occurrence = text.lower().count(kw.lower())
                        keyword_data[kw]["total_occurrence"] += occurrence
                        keyword_data[kw]["occurrences"][rank] = occurrence
                        if occurrence > keyword_data[kw]["max_occurrence"]:
                            keyword_data[kw]["max_occurrence"] = occurrence
                            keyword_data[kw]["max_url"] = url

            # Analyser l'URL de l'utilisateur avec TextRazor et extraire les mots-clés avec YAKE
            if user_url:
                user_text = analyze_url_with_textrazor(user_url, textrazor_api_key)
                if user_text:
                    combined_text += user_text + " "
                    user_keywords = extract_keywords_with_yake(user_text, stopword_list)
                    for kw, score in user_keywords:
                        if kw not in keyword_data:
                            keyword_data[kw] = {"total_occurrence": 0, "max_occurrence": 0, "max_url": "", "score": score, "ranking": None, "occurrences": [0]*11}
                        occurrence = user_text.lower().count(kw.lower())
                        keyword_data[kw]["total_occurrence"] += occurrence
                        keyword_data[kw]["occurrences"][10] = occurrence  # Index 10 pour "Votre URL"
                        if occurrence > keyword_data[kw]["max_occurrence"]:
                            keyword_data[kw]["max_occurrence"] = occurrence
                            keyword_data[kw]["max_url"] = user_url

            # Convertir les données des mots-clés en DataFrame
            data = []
            for kw, values in keyword_data.items():
                mean_top_3 = sum(values["occurrences"][:3]) / 3
                data.append([kw, values["total_occurrence"], values["max_occurrence"], values["max_url"], values["score"], values["ranking"], mean_top_3])
            df = pd.DataFrame(data, columns=["Mot Yake", "Nombre d'occurrences total", "Nombre d'occurrences max", "URL avec Occurrence Max", "Score", "Ranking", "Moyenne d'occurrences sur le top 3"])

            # Trier le DataFrame par nombre d'occurrences total (ordre descendant)
            df = df.sort_values(by=["Nombre d'occurrences total"], ascending=False)

            # Stocker les résultats dans st.session_state
            st.session_state['df'] = df

            # Afficher le tableau
            st.subheader("Mots-clés extraits des résultats ValueSERP")
            st.subheader("Pour rappel : The lower the score, the more relevant the keyword is.")
            st.dataframe(df)

            # Convertir le DataFrame en CSV
            csv = convert_df_to_csv(df)

            # Nom du fichier CSV
            file_name = "mots_cles_yake_valueserp.csv"

            # Bouton de téléchargement
            st.download_button(
                label="Télécharger le tableau en CSV",
                data=csv,
                file_name=file_name,
                mime='text/csv',
            )
        except requests.RequestException as e:
            st.error(f"Erreur lors de la recherche avec ValueSERP : {e}")

# Affichage des résultats précédemment calculés
if 'df' in st.session_state:
    df = st.session_state['df']

    # Afficher le tableau
    st.subheader("Mots-clés extraits")
    st.subheader("Pour rappel : The lower the score, the more relevant the keyword is.")
    st.dataframe(df)

    # Afficher les mots-clés sous forme de liste à virgule
    st.subheader("Mots-clés extraits (liste à virgule)")
    st.write(", ".join(df["Mot Yake"].tolist()))

    # Convertir le DataFrame en CSV
    csv = convert_df_to_csv(df)

    # Nom du fichier CSV
    file_name = "mots_cles_yake.csv"

    # Bouton de téléchargement
    st.download_button(
        label="Télécharger le tableau en CSV",
        data=csv,
        file_name=file_name,
        mime='text/csv',
    )
else:
    st.warning("Veuillez entrer un texte ou une URL pour extraire les mots-clés.")
