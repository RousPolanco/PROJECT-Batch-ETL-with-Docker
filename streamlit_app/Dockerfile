# Dockerfile
# Streamlit_app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir \
    streamlit \
    pymongo \
    pandas \
    matplotlib \
    seaborn 

RUN pip install wordcloud plotly


CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
