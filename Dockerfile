FROM python
COPY . /app
WORKDIR /app

# # 镜像内挂载，不用run时的-t
# VOLUME [ "data" ]
RUN pip install -r requirements.txt
CMD python news.py

