import pandas as pd
import random

class DummyClassifier:
    """
    Stub model for testing. Later replace with joblib.load(model_path).
    """
    def predict(self, df: pd.DataFrame):
        return [random.choice([0, 1]) for _ in range(len(df))]
