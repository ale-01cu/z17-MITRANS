import pandas as pd
import spacy
import re
import unicodedata
from spellchecker import SpellChecker


class NLP:
    def __init__(self):
        # Cargar modelo de Spacy
        self.nlp = spacy.load('es_core_news_sm')

        # Inicializar corrector ortográfico
        self.spell = SpellChecker(language='es')

    def is_token_allowed(self, token) -> bool:
        return bool(
            token
            # and not token.is_stop  # Stopword Removal
            and token.is_alpha  # Eliminar tokens no alfabéticos
            and not token.is_punct  # Eliminar puntuaciones
        )

    def preprocess_token(self, token) -> str:
        return token.lemma_.strip().lower()  # Lemmatization

    def spell_check(self, text: str) -> str:
        corrected_text = []
        for word in text.split():
            corrected_word = self.spell.correction(word)
            corrected_text.append(corrected_word)
        return ' '.join(corrected_text)

    def filters(self, value):
        if value is None or value == '':
            return ''  # Devuelve una cadena vacía para los valores vacíos
        text = str(value)
        text = re.sub(r'[()\-_]', ' ', text)  # Delimiter Removal
        text = re.sub(r'<[^>]*>', '', text)  # Removal of Tags
        text = ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))
        return text

    def process_text(self, df, columns):
        processed_data = []

        for index, row in enumerate(df.iterrows()):
            print(f"Procesando elemento {index}")
            _, row = row  # Desempacar el índice y la fila
            processed_row = {}
            all_empty = True  # Flag para verificar si toda la fila está vacía

            for col in columns:
                value = row[col]
                if isinstance(value, str) and value.strip():  # Verifica si el valor es una cadena no vacía
                    tokens = self.nlp(self.filters(value))
                    processed_value = ' '.join([
                        str(token).lower()
                        for token in tokens
                        if self.is_token_allowed(token)
                    ])
                    all_empty = False  # Si encontramos un valor no vacío, marcamos la fila como no vacía
                elif value is not None:  # Si es None o cualquier otro tipo de dato válido
                    processed_value = str(value)
                    all_empty = False  # Si encontramos un valor no vacío, marcamos la fila como no vacía
                else:  # Si es un valor vacío (None o cadena vacía)
                    processed_value = ''

                processed_row[col] = processed_value

            # Solo agregamos la fila si no está completamente vacía
            if not all_empty:
                processed_data.append(processed_row)

        return pd.DataFrame(processed_data)

class ETL:
    def __init__(self):
        self.nlp_processor = NLP()  # Instancia de la clase NLP

    def extract(self, csv_path):
        """Read the CSV file and return a DataFrame."""
        df = pd.read_csv(csv_path)
        return df

    def transform(self, df, columns):
        """Remove documents with empty fields and apply NLP."""
        # Remove rows with any empty fields
        df = df.dropna(how='any')

        # Process the text using NLP
        processed_df = self.nlp_processor.process_text(df, columns)
        return processed_df


if __name__ == "__main__":
    etl_processor = ETL()
    etl_processor.run('./datasets/picta_publicaciones_crudas.csv')
