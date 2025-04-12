from sentence_transformers import SentenceTransformer
import xgboost as xgb
import joblib
from django.conf import settings
import os
import pandas as pd

MODEL_PATH = os.path.join(settings.BASE_DIR, 'apps/classification/ml/model/')  # Ruta absoluta al archivo

try:
    print("Cargando modelos...")
    sentence_model = SentenceTransformer(MODEL_PATH + 'paraphrase-MiniLM-L6-v2-tunned')
    xgb_model = xgb.Booster()
    xgb_model.load_model(MODEL_PATH + "xgboost_model.json")
    label_encoder = joblib.load(MODEL_PATH + "label_encoder.pkl")
except Exception as e:
    raise RuntimeError(f"Error loading models: {str(e)}")


def predict_comment_label(comment: str = None):
    """
    Función para predecir la etiqueta de un comentario
    Args:
        comment (str): Texto a clasificar
    Returns:
        str: Etiqueta predicha
    """
    if comment is None:
        raise ValueError("Comment cannot be None")

    try:
        # Generar embedding
        embedding = sentence_model.encode(str(comment))

        # Preparar datos para XGBoost
        input_df = pd.DataFrame([embedding])
        dmatrix = xgb.DMatrix(input_df)

        # Predecir
        prediction = xgb_model.predict(dmatrix)
        predicted_label = label_encoder.inverse_transform([int(prediction)])[0]

        return predicted_label
    except Exception as e:
        raise RuntimeError(f"Prediction error: {str(e)}")