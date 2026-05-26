from abc import ABC, abstractmethod
import datetime
import pandas as pd
import yfinance as yf
from sqlalchemy import text
from database import engine

class BaseIngestor(ABC):
    """  
    Classe abstraite définissant l'interface d'un pipeline d'ingestion.
    """
    @abstractmethod
    def fetch_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_data(self, df: pd.DataFrame) -> None:
        pass

class YahooFinanceIngestor(BaseIngestor):
    """  
    Implémentation concrète pour l'extraction depuis Yahoo finance
    """
    def __init__(self, tickers: list):
        self.tickers = tickers
    
    def fetch_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """  
        Télécharge les données boursières et renvoie un DataFrame formaté
        """
        all_data = []
        for ticker in self.tickers:
            print(f"Extraction des données pour {ticker}...")
            
            # Téléchargement des données
            data = yf.download(ticker, start=start_date, end=end_date)

            if not data.empty:
                # 1. Si yfinance renvoie un MultiIndex (dépend des versions/tickers), on l'aplatit
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                # 2. On extrait immédiatement l'index temporel pour en faire une vraie colonne
                data = data.reset_index()
                
                # 3. On force le renommage de toutes les colonnes existantes en minuscules
                data.columns = [str(col).lower() for col in data.columns]
                
                # 4. Sécurité : yfinance nomme parfois la colonne 'date' ou 'date-time'.
                # On renomme explicitement la première colonne du DataFrame en 'date'
                data.rename(columns={data.columns[0]: 'date'}, inplace=True)
                
                # 5. Ajout de la colonne ticker
                data['ticker'] = ticker

                # 6. Sélection et ordonnancement strict des colonnes pour correspondre à PostgreSQL
                data = data[['date', 'ticker', 'open', 'close', 'volume']]
                data.columns = ['date', 'ticker', 'open_price', 'close_price', 'volume']
                
                all_data.append(data)
        
        if not all_data:
            return pd.DataFrame()
        
        return pd.concat(all_data, ignore_index=True)

    def save_data(self, df: pd.DataFrame) -> None:
        """  
        Insère les données dans PostgreSQL en gérant les doublons
        """
        if df.empty:
            print("Aucune donnée à sauvegarder")
            return
        print(f"Insertion de {len(df)} lignes dans la base de données...")

        with engine.connect() as connection:
            for _, row in df.iterrows():
                query = text(""" 
                    INSERT INTO market_data (date, ticker, open_price, close_price, volume)
                    VALUES (:date, :ticker, :open_price, :close_price, :volume)
                    ON CONFLICT (date, ticker) DO NOTHING;
                 """)
                connection.execute(query, {
                    "date": row['date'],
                    "ticker": row['ticker'],
                    "open_price": float(row['open_price']),
                    "close_price": float(row['close_price']),
                    "volume": int(row['volume'])
                })
            connection.commit()
        print("Données sauvegardées avec succès")

# Bloc pour valider le script fonctionnel en local
if __name__ == "__main__":
    tickers_to_track = ["TTE.PA", "ENGI.PA", "^STOXX50E"]
    ingestor = YahooFinanceIngestor(tickers=tickers_to_track)

    end = datetime.datetime.now().strftime("%Y-%m-%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    raw_data = ingestor.fetch_data(start_date=start, end_date=end)
    ingestor.save_data(raw_data)