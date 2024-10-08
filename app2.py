import streamlit as st
import yake
import nltk
from nltk.corpus import stopwords
import pandas as pd
import os

# Initialisation de Streamlit
st.set_page_config(page_title="Extraction de mots-clés avec YAKE", layout="wide")

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

# Charger les stopwords personnalisés si vous en avez
custom_stopwords = []  # Remplacez par votre liste personnalisée si nécessaire
try:
    stopword_list = stopwords.words('french') + custom_stopwords
except LookupError:
    stopword_list = custom_stopwords
    st.warning("Impossible de charger les stopwords NLTK. Utilisation des stopwords personnalisés uniquement.")

# Titre de l'application
st.title("Extraction de mots-clés avec YAKE")

# Champ de texte pour l'entrée utilisateur
text_input = st.text_area("Entrez le texte ici :")

# Bouton pour lancer l'analyse
if st.button("Analyser"):
    if text_input.strip():
        # Extraction des mots-clés avec YAKE
        kw_extractor = yake.KeywordExtractor(lan="fr", n=3, dedupLim=0.9, top=20, features=None, stopwords=stopword_list)
        keywords = kw_extractor.extract_keywords(text_input)

        # Créer un DataFrame avec les mots-clés et les scores
        data = {
            "Mot Yake": [kw for kw, score in keywords],
            "Score": [score for kw, score in keywords],
            "Nombre d'occurrences": [text_input.lower().count(kw.lower()) for kw, score in keywords]
        }
        df = pd.DataFrame(data)

        # Afficher le tableau avec les mots-clés, scores et occurrences
        st.subheader("Mots-clés extraits")
        st.dataframe(df)

        # Convertir le DataFrame en CSV
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Télécharger le tableau en CSV",
            data=csv,
            file_name="mots_cles_yake.csv",
            mime='text/csv',
        )
    else:
        st.warning("Veuillez entrer un texte pour procéder à l'analyse.")
