FROM python
COPY . .
WORKDIR .
RUN pip install -r requirements.txt
CMD python news.py

