import os.path
from pathlib import Path

import pandas as pd
import numpy as np
import itertools

import matplotlib as mpl
import matplotlib.pyplot as plt
from django.templatetags.static import static
from matplotlib.pyplot import figure

import warnings

from gradProject import settings
from fpdf import FPDF

from gradProject.settings import MEDIA_ROOT, STATIC_ROOT

warnings.filterwarnings('ignore')

from scipy import stats
import statsmodels.api as sm

from statsmodels.tsa.stattools import adfuller


def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_missing_freq(df: pd.DataFrame):
    not_missing = df.notna().sum().sum()
    missing = df.isna().sum().sum()
    return missing, not_missing


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    return df.interpolate()


def process_missing(df: pd.DataFrame) -> pd.DataFrame:
    missing, not_missing = get_missing_freq(df)

    if missing != 0:  # заполнение пропусков интерполяцией
        df_filled = fill_missing(df)
        return df_filled

    return df


def fullertest(df: pd.DataFrame):
    result = adfuller(df)

    # print('ADF Statistic: %f' % result[0])
    # print('p-value: %f' % result[1])
    # print('Critical Values:')
    # for key, value in result[4].items():
    #     print('\t%s: %.3f' % (key, value))

    return result[0], result[4]['5%']


# стационирование ряда и удаление ряда
def stationate_data(df: pd.DataFrame):
    adf, critval = fullertest(df)
    integr = 0
    diff_values = pd.DataFrame()

    while adf > critval:
        diff_values = df.diff(periods=1).dropna()
        adf, critval = fullertest(diff_values)
        integr += 1

    #    if integr > 0:
    #        df_stat = replace_outliers(diff_values, col)
    #    else:
    #        df_stat = replace_outliers(df)

    return integr


# замена выбросов
def replace_outliers(df: pd.core.frame.DataFrame, col):
    z_thresh = 3
    z = np.abs(stats.zscore(df[col]))  # определяем z-score для каждого значения
    df['outliers'] = z > z_thresh
    incl = df.index[df['outliers'] == True].tolist()
    df.loc[df.index.isin(incl), col] = np.nan
    df[col] = np.where((df[col].isnull()) & (df.index.isin(incl)), df[col].mean(), df[col])
    df = df.drop('outliers', axis=1)
    return df


def search_optimal_arima(df: pd.DataFrame, d):
    ps = range(0, 2)  # порядок AR (авторегрессии)
    qs = range(0, 3)  # порядок MA (скользящего среднего)
    # Ps = range(0, 5) # порядок AR (авторегрессии) сезонный
    # Qs = range(0, 1) # порядок MA (скользящего среднего) сезонный
    parameters = itertools.product(ps, qs)
    pdq_combinations = list(parameters)

    smallest_aic = float('inf')
    optimal_order_param = (0, 0, 0)

    for param in pdq_combinations:
        try:
            arima_model = sm.tsa.arima.ARIMA(df, order=(param[0], d, param[1]), freq='MS')
            model_results = arima_model.fit()
        except ValueError:
            continue

        m_aic = float(str(model_results.aic))

        if m_aic < smallest_aic:
            smallest_aic = m_aic
            optimal_order_param = (param[0], d, param[1])

    return optimal_order_param


def parse_excel(file):
    df = pd.read_excel(file)
    columns = df.columns.values.tolist()

    return columns


def get_forecast(model, df, val):
    st_pred = model.get_forecast(steps=12)

    forecast_values = pd.Series([df[val].iloc[-1]])
    forecast_values = pd.concat([forecast_values, st_pred.predicted_mean], ignore_index=True)
    forecast_period = pd.date_range(start=df.index[-1], periods=13, freq='MS')

    forecast_df = pd.DataFrame({'Дата': forecast_period, 'Значения': forecast_values})
    forecast_df = forecast_df.set_index('Дата')

    return forecast_df


def data_processing(file, filename):
    df = pd.read_excel(file)
    cols = df.columns.values.tolist()
    df = df.set_index(cols[0])
    df = df[[cols[1]]]

    # очистка данных
    clean_df = process_missing(df)
    integr = stationate_data(clean_df)

    # настройка модели
    model_param = search_optimal_arima(clean_df, integr)
    model = sm.tsa.arima.ARIMA(clean_df, order=model_param)
    results = model.fit()

    # получение прогноза
    forecast = get_forecast(results, clean_df, cols[1])
    graph_url = make_graph(forecast, clean_df, cols, filename)
    return forecast, clean_df, graph_url


def make_graph(forecast, df, cols, filename):
    plt.figure(figsize=(16,4))
    plt.plot(df, label="Реальные значения", color="blue")
    plt.plot(forecast, label='Прогноз', color='red')

    plt.title(filename)
    plt.xlabel(cols[1])
    plt.ylabel(cols[0])
    plt.legend()

    filename = filename.replace(".xlsx", "")
    figname = f'graphs/{filename}_forecast.png'

    plt.savefig(os.path.join(settings.MEDIA_ROOT, figname))

    return figname


class FPDF(FPDF):

    def header(self):
        self.set_xy(15, 7)
        self.set_font("Montserrat", "B", 14)
        self.set_text_color(42, 24, 158)
        self.cell(50, 10, "PREVISION")
        self.set_font( style="", size=10)
        self.cell(130, 10, "www.prevision.com", align="R")
        self.set_xy(20, 30)

    def footer(self):
        self.set_y(-15)
        pageNum = self.page_no()

        self.set_font("Montserrat", "", 10)
        self.cell(0, 10, str(pageNum), align="C")


def render_table_header(pdf, cols):
    """Вывод строки с заголовками колонок таблицы"""
    # включение жирного текста
    pdf.set_fill_color(205, 184, 238)
    pdf.set_font(style="B")
    pdf.cell(80, 8, str(cols[0]), 1, 0, align='C', fill=True)
    pdf.cell(80, 8, str(cols[1]), 1, 1, align='C', fill=True)
    pdf.set_x(30)
    # отключение жирного текста
    pdf.set_font(style="")


def make_report(filename, df_cols, df, forecast, graph):
    pdf = FPDF()
    pdf.add_font("Montserrat", style="", fname=r"C:\Users\Яна\PycharmProjects\GradProject\project\static\static_files\Montserrat-Regular.ttf")
    pdf.add_font("Montserrat", style="B", fname=r"C:\Users\Яна\PycharmProjects\GradProject\project\static\static_files\Montserrat-Bold.ttf")
    w = 210
    h = 297
    filename = filename.replace(".xlsx", "")
    graph_url = os.path.join(MEDIA_ROOT, graph)

    pdf.add_page()
    pdf.set_font("Montserrat", "B", 12)
    pdf.cell(75, 10, f"Прогноз для {filename}", 0, 2, 'L')
    pdf.image(graph_url, x=5, w=210)
    pdf.cell(0, 5, " ", 0, 2, 'C')

    # вывод прогноза
    pdf.set_font("Montserrat", "", 12)
    pdf.set_text_color(117, 78, 153)
    pdf.cell(19, 10, 'Прогноз', 0, 0, align='L')
    pdf.set_text_color(0, 0, 0)
    pdf.cell(8, 10, ' | ', 0, 0, align='C')
    pdf.set_text_color(78, 84, 153)
    pdf.cell(50, 10, 'Изначальные данные', 0, 1, align='R')

    pdf.set_font("Montserrat", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(30)
    render_table_header(pdf, df_cols)

    pdf.set_fill_color(243, 243, 255)
    # проходим по строкам с данными
    for f in reversed(forecast):
        if pdf.will_page_break(6):
            # то запускаем функцию заголовка таблицы
            render_table_header(pdf, df_cols)
            pdf.set_fill_color(243, 243, 255)
        # выводим в цикле колонки с данными
        pdf.cell(80, 6, str(f[0]), 1, 0, align='C', fill=True)
        pdf.cell(80, 6, str(f[1]), 1, 1, align='C', fill=True)
        pdf.set_x(30)

    # вывод изначального датафрейма
    for d in reversed(df):
        if pdf.will_page_break(6):
            # то запускаем функцию заголовка таблицы
            render_table_header(pdf, df_cols)

        pdf.cell(80, 6, str(d[0]), 1, 0, align='C')
        pdf.cell(80, 6, str(d[1]), 1, 1, align='C')
        pdf.set_x(30)

    report_name = f'reports/{filename}_report.pdf'
    pdf.output(os.path.join(MEDIA_ROOT, report_name))
    return report_name
