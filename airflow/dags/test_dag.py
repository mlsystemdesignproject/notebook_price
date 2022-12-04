import airflow
from airflow.models import DAG
from airflow.operators.bash import BashOperator

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
}

dag = DAG(
    dag_id='test_dag',
    default_args=args,
    schedule_interval=None
)

t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag
)

t2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    retries=3,
    dag=dag
)

t3 = BashOperator(
    task_id='write_date_to_file',
    bash_command='date >> /tmp/date.txt',
    dag=dag
)


t1 >> t2 >> t3





