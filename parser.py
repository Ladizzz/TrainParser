import requests      # Библиотека для отправки запросов
# import numpy as np   # Библиотека для матриц, векторов и линала
# import pandas as pd  # Библиотека для табличек
# import time          # Библиотека для тайм-менеджмента

page_link = 'https://pass.rw.by/ru/route/?path=ru%2Froute%2F&from=%D0%9C%D0%B8%D0%BD%D1%81%D0%BA&from_exp=&from_esr=&to=%D0%9E%D1%80%D1%88%D0%B0&to_exp=2100170&to_esr=166403&front_date=20+%D0%BD%D0%BE%D1%8F.+2020&date=2020-11-20'
response = requests.get(page_link)
response