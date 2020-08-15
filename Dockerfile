FROM python as base

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install update \
    && pip install -r requirements.txt

COPY covid.py .

FROM base as dev

RUN pip install --upgrade pip \
    && pip install update \
    && pip install jupyter pylint