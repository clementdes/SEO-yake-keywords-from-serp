# Extraction de mots-clés avec YAKE et TextRazor

**English version below**

Bienvenue dans l'application **Extraction de mots-clés avec YAKE et TextRazor** ! Cette application vous permet d'extraire des mots-clés pertinents à partir de textes ou d'URLs en utilisant les bibliothèques YAKE et TextRazor, ainsi que de rechercher des mots-clés avec l'API ValueSERP.

## Fonctionnalités

- Extraction de mots-clés à partir de textes fournis par l'utilisateur.
- Extraction de mots-clés à partir de contenus d'URLs.
- Recherche de mots-clés et de locations avec l'API ValueSERP.
- Analyse des résultats de recherche Google pour un mot-clé donné et une location sélectionnée.
- Comparaison des mots-clés extraits pour des URLs spécifiques.
- Téléchargement des résultats sous forme de fichiers CSV.

## Prérequis

- Python 3.7 ou supérieur
- Clé API TextRazor
- Clé API ValueSERP
- Fichier `custom_stopwords.txt` contenant des stopwords personnalisés

## Installation

1. Clonez ce dépôt GitHub :

    ```bash
    git clone https://github.com/votre_nom/votre_repo.git
    cd votre_repo
    ```

2. Installez les dépendances :

    ```bash
    pip install -r requirements.txt
    ```

3. Assurez-vous d'avoir les stopwords de NLTK :

    ```python
    import nltk
    nltk.download('stopwords')
    ```

## Utilisation

1. Lancez l'application Streamlit :

    ```bash
    streamlit run app.py
    ```

2. Ouvrez votre navigateur et accédez à `http://localhost:8501`.

3. Entrez votre texte ou URL dans les champs appropriés.

4. Fournissez vos clés API TextRazor et ValueSERP dans la barre latérale.

5. Cliquez sur "Rechercher les locations" pour obtenir des suggestions de locations avec l'API ValueSERP.

6. Cliquez sur "Analyser" pour extraire les mots-clés et afficher les résultats.

## Exemple de code

Voici un extrait du code principal de l'application :

```python
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
textrazor_api_key = st.sidebar.text_input("Entrez votre clé API TextRazor", type="password", value="")
valueserp_api_key = st.sidebar.text_input("Entrez votre clé API ValueSERP", type="password", value="")
keyword_input = st.sidebar.text_input("Entrez un mot-clé pour la recherche ValueSERP")
location_query = st.sidebar.text_input("Entrez une location pour la recherche ValueSERP")
user_url = st.sidebar.text_input("Votre URL")

# ... (le reste du code)
```

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre des problèmes et des demandes de fonctionnalités via les issues GitHub. Pour contribuer au code, veuillez créer une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Remerciements

Merci à toutes les bibliothèques et API utilisées dans ce projet :

- [Streamlit](https://streamlit.io/)
- [YAKE](https://github.com/LIAAD/yake)
- [TextRazor](https://www.textrazor.com/)
- [ValueSERP](https://www.valueserp.com/)
- [NLTK](https://www.nltk.org/)

---

# Keyword Extraction with YAKE and TextRazor

Welcome to the **Keyword Extraction with YAKE and TextRazor** application! This application allows you to extract relevant keywords from texts or URLs using the YAKE and TextRazor libraries, as well as search for keywords using the ValueSERP API.

## Features

- Keyword extraction from user-provided texts.
- Keyword extraction from URL contents.
- Keyword and location search using the ValueSERP API.
- Analysis of Google search results for a given keyword and selected location.
- Comparison of extracted keywords for specific URLs.
- Download results as CSV files.

## Prerequisites

- Python 3.7 or higher
- TextRazor API key
- ValueSERP API key
- `custom_stopwords.txt` file containing custom stopwords

## Installation

1. Clone this GitHub repository:

    ```bash
    git clone https://github.com/your_name/your_repo.git
    cd your_repo
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have the NLTK stopwords:

    ```python
    import nltk
    nltk.download('stopwords')
    ```

## Usage

1. Run the Streamlit application:

    ```bash
    streamlit run app.py
    ```

2. Open your browser and go to `http://localhost:8501`.

3. Enter your text or URL in the appropriate fields.

4. Provide your TextRazor and ValueSERP API keys in the sidebar.

5. Click "Search locations" to get location suggestions using the ValueSERP API.

6. Click "Analyze" to extract keywords and display the results.

## Code Example

Here is an excerpt from the main application code:

```python
import streamlit as st
import yake
import nltk
from nltk.corpus import stopwords
import pandas as pd
import os
import textrazor
import requests

# Check if the NLTK data directory exists
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Download NLTK stopwords if necessary
nltk.data.path.append(nltk_data_dir)
nltk.download('stopwords', download_dir=nltk_data_dir)

# Read custom stopwords from a file
def load_custom_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

# Load custom stopwords
custom_stopwords = load_custom_stopwords('custom_stopwords.txt')

# Merge NLTK stopwords and custom stopwords
stopword_list = stopwords.words('french') + custom_stopwords

# Application title
st.title("Keyword Extraction with YAKE and TextRazor")

# Text input field for user input
text_input = st.text_area("Enter text here:")

# URL input field
url_input = st.text_input("Or enter URL here:")

# Sidebar fields
textrazor_api_key = st.sidebar.text_input("Enter your TextRazor API key", type="password", value="")
valueserp_api_key = st.sidebar.text_input("Enter your ValueSERP API key", type="password", value="")
keyword_input = st.sidebar.text_input("Enter a keyword for ValueSERP search")
location_query = st.sidebar.text_input("Enter a location for ValueSERP search")
user_url = st.sidebar.text_input("Your URL")

# ... (rest of the code)
```

## Contributing

Contributions are welcome! Please submit issues and feature requests via GitHub issues. To contribute code, please create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

Thanks to all the libraries and APIs used in this project:

- [Streamlit](https://streamlit.io/)
- [YAKE](https://github.com/LIAAD/yake)
- [TextRazor](https://www.textrazor.com/)
- [ValueSERP](https://www.valueserp.com/)
- [NLTK](https://www.nltk.org/)

---

N'hésitez pas à adapter ce fichier README en fonction de vos besoins spécifiques et de votre dépôt GitHub.

Feel free to adapt this README file according to your specific needs and your GitHub repository.
