from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
from tasks.extract_realtor import extract_realtor_data



api_host_key = Variable.get("redfin_api_credentials", deserialize_json=True)

now  = datetime.now()
dt_now_string = now.strftime("%Y-%m-%d-%H-%M-%S")


default_args = {
    'owner': 'Abdulwajeed',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 25),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

with DAG('redfin_etl',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False) as dag:
    
    exract_redfin_data = PythonOperator(
        task_id='extract_redfin_data',
        python_callable=extract_realtor_data,
        op_kwargs={'url': "https://redfin-com-data.p.rapidapi.com/properties/search-rent",
                   'querystring': {"regionId":"6_13410"},
                   'date_string': dt_now_string},
        dag=dag)
    load_to_s3 = LocalFilesystemToS3Operator(
        task_id = 'Load_to_s3',
        filename = '{{ task_instance.xcom_pull(task_ids="extract_redfin_data") }}',
        dest_key='redfin_data_{{ ds }}.json',
        dest_bucket='redfinraw-data',
        replace=True,
        aws_conn_id='aws_default',
        dag=dag)
    
    check_s3_file = S3KeySensor(
    task_id='check_transformed_data',
    bucket_name='transformed-redfin-data',
    bucket_key='redfin_data_{{ ds }}.csv',
    aws_conn_id='aws_default',
    poke_interval=60,
    timeout=3600,
    mode='poke',
    dag=dag)


    load_to_redshift = S3ToRedshiftOperator(
    task_id='load_to_redshift',
    schema='public',
    table='Realtordata',
    s3_bucket='transformed-realtor-data',
    s3_key='redfin_data_{{ ds }}.csv',
    aws_conn_id='aws_default',
    redshift_conn_id='conn_id_redshift',
    copy_options=[
        "CSV",
        "IGNOREHEADER 1",
        "DELIMITER ','",
        "REGION 'us-east-1'",
        "IAM_ROLE 'arn:aws:iam::268892761349:role/service-role/AmazonRedshift-CommandsAccessRole-20240101T004306'"
    ],
    autocommit=True,
    retries=5,
    retry_delay=timedelta(minutes=2),
    execution_timeout=timedelta(minutes=10),
    dag=dag)



    
    
    

    exract_redfin_data >> load_to_s3 >> check_s3_file >> load_to_redshift

    

    