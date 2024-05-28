import streamlit as st
import yake
import nltk
from nltk.corpus import stopwords
import pandas as pd
import os
import textrazor
import requests

# Vérifier si le répertoire de données NLTK existe
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Télécharger les stopwords de nltk si nécessaire
nltk.data.path.append(nltk_data_dir)
nltk.download('stopwords', download_dir=nltk_data_dir)

# Lire les stopwords personnalisés à partir d'un fichier
def load_custom_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

# Charger les stopwords personnalisés
custom_stopwords = load_custom_stopwords('custom_stopwords.txt')

# Fusionner les stopwords NLTK et les stopwords personnalisés
stopword_list = stopwords.words('french') + custom_stopwords

# Titre de l'application
st.title("Extraction de mots-clés avec YAKE et TextRazor")

# Champ de texte pour l'entrée utilisateur
text_input = st.text_area("Entrez le texte ici :")

# Champ de saisie pour l'URL
url_input = st.text_input("Ou entrez l'URL ici :")

# Champs dans la sidebar
textrazor_api_key = st.sidebar.text_input("Entrez votre clé API TextRazor", type="password", value="abe15d2af673d8e637250ff5d573b24bb083bb6af18435b9555513b1")
valueserp_api_key = st.sidebar.text_input("Entrez votre clé API ValueSERP", type="password", value="E18257C59ED24E9AA0E041348E8A989C")
keyword_input = st.sidebar.text_input("Entrez un mot-clé pour la recherche ValueSERP")
location_query = st.sidebar.text_input("Entrez une location pour la recherche ValueSERP")
user_url = st.sidebar.text_input("Votre URL")

# Bouton pour rechercher les locations avec l'API ValueSERP
if st.sidebar.button("Rechercher les locations"):
    if not valueserp_api_key:
        st.sidebar.error("Veuillez entrer votre clé API ValueSERP.")
    else:
        # Rechercher les locations avec l'API ValueSERP
        locations_url = f"https://api.valueserp.com/locations?api_key={valueserp_api_key}&q={location_query}"
        response = requests.get(locations_url)
        if response.status_code == 200:
            locations = response.json().get("locations", [])
            if not locations:
                st.sidebar.warning("Aucune location trouvée.")
            else:
                location_options = [loc['full_name'] for loc in locations]
                selected_location = st.sidebar.selectbox("Sélectionnez une location", location_options)
                st.session_state['selected_location'] = selected_location
        else:
            st.sidebar.error("Erreur lors de la récupération des locations.")

# Afficher la location sélectionnée
if 'selected_location' in st.session_state:
    st.sidebar.write(f"Location sélectionnée : {st.session_state['selected_location']}")

# Fonction pour analyser une URL avec TextRazor
def analyze_url_with_textrazor(url, api_key):
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

# Fonction pour convertir le DataFrame en CSV
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

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

# Initialiser les variables
df = None
combined_text = ""

# Recherche ValueSERP avec le mot-clé et la location sélectionnée
if keyword_input and 'selected_location' in st.session_state:
    search_url = f"https://api.valueserp.com/search?api_key={valueserp_api_key}&q={keyword_input}&location={st.session_state['selected_location']}&num=30"
    search_response = requests.get(search_url)
    if search_response.status_code == 200:
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

        # Filtrer les n-grams de deux mots
        bigrams = df[df["Mot Yake"].apply(lambda x: len(x.split()) == 2)]
        st.subheader("N-grams de deux mots")
        st.dataframe(bigrams)

        # Filtrer les n-grams de trois mots
        trigrams = df[df["Mot Yake"].apply(lambda x: len(x.split()) == 3)]
        st.subheader("N-grams de trois mots")
        st.dataframe(trigrams)

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

        # Créer un tableau pour tous les mots-clés avec les colonnes dynamiques
        dynamic_data = []
        for kw, values in keyword_data.items():
            dynamic_row = [kw, values["total_occurrence"]]
            dynamic_row.extend(values["occurrences"])
            dynamic_data.append(dynamic_row)

        dynamic_columns = ["Mot Yake", "Nombre d'occurrences total"] + urls[:10] + ["Votre URL"]
        dynamic_df = pd.DataFrame(dynamic_data, columns=dynamic_columns)

        # Afficher le tableau dynamique
        st.subheader("Mots-clés avec occurrences par URL")
        st.dataframe(dynamic_df)

        # Convertir le DataFrame dynamique en CSV
        dynamic_csv = convert_df_to_csv(dynamic_df)

        # Nom du fichier CSV
        dynamic_file_name = "mots_cles_yake_valueserp_dynamic.csv"

        # Bouton de téléchargement
        st.download_button(
            label="Télécharger le tableau dynamique en CSV",
            data=dynamic_csv,
            file_name=dynamic_file_name,
            mime='text/csv',
        )
    else:
        st.error("Erreur lors de la recherche avec ValueSERP.")

# Vérifier si les résultats sont disponibles dans st.session_state
if 'df' in st.session_state:
    df = st.session_state['df']

    # Afficher le tableau
    st.subheader("Mots-clés extraits")
    st.subheader("Pour rappel : The lower the score, the more relevant the keyword is.")
    st.dataframe(df)

    # Extraire uniquement les termes des mots-clés
    keyword_terms = df["Mot Yake"].tolist()

    # Afficher les mots-clés sous forme de liste à virgule
    st.subheader("Mots-clés extraits (liste à virgule)")
    st.write(", ".join(keyword_terms))

    # Afficher les 20 mots YAKE avec le score le plus bas et le nombre d'occurrences le plus élevé
    st.subheader("Top 20 mots-clés YAKE")
    top_20_keywords = df.head(20)
    st.write(top_20_keywords[["Mot Yake", "Nombre d'occurrences total", "Nombre d'occurrences max", "URL avec Occurrence Max", "Score", "Ranking", "Moyenne d'occurrences sur le top 3"]])

    # Filtrer les n-grams de deux mots
    bigrams = df[df["Mot Yake"].apply(lambda x: len(x.split()) == 2)]
    st.subheader("N-grams de deux mots")
    st.dataframe(bigrams)

    # Filtrer les n-grams de trois mots
    trigrams = df[df["Mot Yake"].apply(lambda x: len(x.split()) == 3)]
    st.subheader("N-grams de trois mots")
    st.dataframe(trigrams)

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