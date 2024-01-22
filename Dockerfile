FROM python:3.11

# EXPOSE 8000

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3
ENV PATH="/opt/poetry/bin:$PATH"

WORKDIR /app/
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* ./alembic.ini /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app

ENV PYTHONPATH=/app
#RUN chmod 777 /app/app/entrypoint.sh
#CMD ["./app/entrypoint.sh"]
#RUN alembic revision --autogenerate -m "first db creation"
#RUN alembic upgrade head
#RUN python arq_runner.py
#RUN arq arq_runner.WorkerSettings
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
