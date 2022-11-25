FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install --upgrade pip && pip3 install ngboost loguru

COPY ["scripts/lambda_app.py", "${LAMBDA_TASK_ROOT}/app.py"]
COPY ["models/ngboost_model.pkl", "${LAMBDA_TASK_ROOT}/model.pkl"]

CMD [ "app.handler" ]
