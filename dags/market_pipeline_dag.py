from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args={
    'owner': 'yann_mle',
    'depends_on_past':False,
    'email_on_failure':False,
    'email_on_retry': False,
    'retries':1;
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'maket_alert_pipeline',
    default_args=default_args,
    description="Pipeline quotidien d'ingestion de données et de détection d'anomalies ML",
    schedule_interval='0 18 * * 1-5', #S s'éxécute à 18h du lundi au vendredi
    start_date=datetime(2026,1,1),
    catchup=False,
    tags=['market','mlops','isolation_forest'],
) as dag :
    #Tache 1 : Lancer l'ingestion de données brutes
    task_ingest_data=BashOperator(
        task_id='ingest_market_data',
        bash_commands='python /opt/airflow/scripts/ingest.py',
    )

    #Tâche 2 : Attendre la fin de l'ingestion pour lancer le modèle ML

    task_run_ml_model=BashOperator(
        task_id='run_ml_anomaly_detector',
        bash_commands='python /opt/airflow/scritps/model.py',
    )

    #Tâche 3 définition de la dépendance 
    task_ingest_data >> task_run_ml_model