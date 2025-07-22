FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir \
    streamlit \
    pymongo \
    pandas \
    matplotlib \
    seaborn \
    plotly \
    wordcloud

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]

