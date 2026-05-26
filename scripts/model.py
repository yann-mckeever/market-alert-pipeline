import datetime
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy import text
from database import engine

class MarketAnomalyDetector:
    """  
    Composant ML en charge de la détection d'anomalies sur les séries temporelles
    """
    def __init__(self,contamination: float=0.05):
        #Contamination : proportion d'anomalies estimées dans le modèle ici 5%
        self.model=IsolationForest(contamination=contamination, random_state=42)
        self.version="v1.0.0"

    def load_data_from_db(self, days_history:int=30)->pd.DataFrame:
        """  
        Extrait les données historiques de la base PostgreSQL
        """

        print(f"Extraction des derniers {days_history} jours de la base de données")

        query=text("""
                SELECT date, ticker, open_price, close_price, volume
                FROM market_data
                WHERE date>=NOW()- INTERVAL ':days DAY'
                ORDER BY ticker, DATE ASC;
                   """)
        
        with engine.connect() as connection :
            #On utilise pandas pour lire directement les résultats de la requête SQL
            df=pd.read_sql_query(query,connection,params={"days":days_history})

        return df
    
    def compute_features(self,df : pd.DataFrame)->pd.DataFrame:
        """  
        Calcule les indicateurs statistiques glissants par ticker
        """
        if df.empty:
            return df
        
        print("Calcul des features (Rendements, Moyennes mobiles...)")
        
        #On trie pour s'assurer de la cohérence temporelle
        df=df.sort_values(by=['ticker','date']).reset_index(drop=True)

        #Calcul du rendement journalier 
        df['return']=(df['close_price']-df['open_price'])/df['open_price']

        df['rolling_mean_3']=df.groupby('ticker')['close_price'].transform(lambda x: x.rolling(3, min_periods=1).mean())
        df['rolling_std_3']=df.groupby('ticker')['close_price'].transform(lambda x: x.rolling(3,min_periods=1).std().fillna(0))

        return df
    
    def run_inference(self, df:pd.DataFrame)->pd.DataFrame:
        """ 
        Entraîne les données et détecte les anomalies sur les données  
        """
        if df.empty:
            print("Aucune donnée disponible pour l'inférence")
            return df
        
        print("Exécution de l'algorithm isolation de forêt")
        prediction_list=[]

        #On applique le modèle indépendamment pour chaque ticker

        for ticker, group in df.groupby('ticker'):
            group=group.copy()

            #Sélection des variables numériques pour l'entraînement
            features=['return','rolling_mean_3','rolling_std_3']

            #Entraînement et prédiction simultanée (-1 pour anomalie et 1 pour normale)
            group['anomaly_label']=self.model.fit_predict(group[features])

            #Calcul du score d'anomalie: plus il est bas/négatif : plus c'est anomalie
            group['anomaly_score']=self.model.score_samples(group[features])

            #Cartographie pour correspondre à notre structure SQL (True/False):
            group['is_anomaly']=group['anomaly_label'].apply(lambda x: True if x==-1 else False)

            prediction_list.append(group)

        return pd.concat(prediction_list,ignore_index=True)
    
    def save_predictions(self, df:pd.DataFrame)->None:
        """  
        Sauvegarde des prédictions finales dans la table ml_predictions.

        """

        if df.empty:
            return 
        
        print(f"Sauvegarde de {len(df)} prédictions dans la table ml_predictions...")

        with engine.connect() as connection:
            for _, row in df.iterrows():
                query=text("""
                        INSERT INTO ml_predictions (prediction_date, ticker, predicted_value, is_anomaly, anomaly_score, model_version)
                        VALUES (:prediction_date, :ticker, :predicted_value, :is_anomaly, :anomaly_score, :model_version)
                        ON CONFLICT DO NOTHING;
                           """)
                connection.execute(query,{
                    "prediction_date": row['date'],
                    "ticker": row['ticker'],
                    "predicted_value": float(row['close_price']),
                    "is_anomaly": bool(row['is_anomaly']),
                    "anomaly_score":float(row['anomaly_score']),
                    "model_version":self.version
                })
            connection.commit()
        print("Prédictions enregistrées avec succès")

if __name__=="__main__":
    #Instanciation du détecteur
    detector=MarketAnomalyDetector(contamination=0.05)

    #Exécution de la chaîne de traitement ML
    historical_df=detector.load_data_from_db(days_history=30)

    if not historical_df.empty:
        features_df=detector.compute_features(historical_df)
        results_df=detector.run_inference(features_df)
        detector.save_predictions(results_df)
    else:
        print("La table maket_data est vide. Exécutez ingest.py d'abord")
