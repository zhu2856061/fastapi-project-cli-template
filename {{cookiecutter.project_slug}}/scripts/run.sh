export PYTHONPATH=..
export CONFIG_PATH="../config.yaml"
export ENV_PATH="../.env"
export LOGGING_PATH="../logging.ini"
export WORK_ENV="dev"

uv run uvicorn main:app --host 0.0.0.0 --port 2022