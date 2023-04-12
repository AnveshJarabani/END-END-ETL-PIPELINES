from airflow import DAG
from airflow.operators.python import PythonOperator,BranchPythonOperator
from datetime import datetime
import LBR_BI_PULL,OVS_BI_PULL,PH_BI_PULL,STD_BI_PULL,SHP_BI_PULL,ALL_CUST_QTVSACT
with DAG('my_dag',start_date=datetime(2022,10,19),
schedule_interval='@daily',catchup=False) as dag:
    LBR_PULL=PythonOperator(
        task_id='LABOR BI PULL',
        python_callable=LBR_BI_PULL
    )
    PH_PULL=PythonOperator(
        task_id='PH BI PULL',
        python_callable=PH_BI_PULL
    )
    OVS_PULL=PythonOperator(
        task_id='OVS BI PULL',
        python_callable=OVS_BI_PULL
    )
    STD_PULL=PythonOperator(
        task_id='OVS BI PULL',
        python_callable=STD_BI_PULL
    )
    SHP_PULL=PythonOperator(
        task_id='SHIPMENTS BI PULL',
        python_callable=SHP_BI_PULL
    )
    ALL_QTVSACT=PythonOperator(
        task_id='ALL CUSTOMER QTVSACT',
        python_callable=ALL_CUST_QTVSACT
    )
[LBR_PULL,PH_PULL,OVS_PULL,STD_PULL,SHP_PULL]>>ALL_QTVSACT