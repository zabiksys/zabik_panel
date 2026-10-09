from bokeh.models import ColumnDataSource
from bokeh.models.formatters import DatetimeTickFormatter, FuncTickFormatter, NumeralTickFormatter
from bokeh.plotting import figure

import altair as alt
import pandas as pd
import panel as pn
import sqlalchemy


def get_purchase_orders_df(nav_company: str, engine: sqlalchemy.engine.Engine) -> pd.DataFrame:
    return pd.read_sql(f"""
        SELECT
          pl.[Expected Receipt Date] expected_receipt_date,
          --CAST(pl.[Outstanding Quantity] AS int) outstanding_quantity
          pl.[Outstanding Qty_ (Base)] outstanding_quantity,
          pl.[Document No_] document_no_,
          pl.[Gross Weight] * pl.[Outstanding Qty_ (Base)] gross_weight,
          pl.[Unit Volume] * pl.[Outstanding Qty_ (Base)] volume
        FROM [{nav_company}$Purchase Line] pl
        WHERE
          pl.[Document Type] = 1 /* Order */
          AND pl.[Type] = 2 /* Item */
          AND pl.[Outstanding Quantity] > 0
        """, con=engine)


class App:
    def __init__(self):
        self.url = sqlalchemy.URL.create(
            'mssql+pyodbc',
            username='reporting', password='reporting',
            host='europa.local.zabik', database='BIZAK_50',
            query={'driver': 'ODBC Driver 17 for SQL Server'})
        self.engine = sqlalchemy.create_engine(self.url, echo=False)
        self.nav_company = 'Bizak'

    def run_bokeh(self) -> None:
        s = pn.Column('# Hola')
        # locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        # st.markdown("# Cuadro mando almacén")

        purchase_orders_df = (
            get_purchase_orders_df(self.nav_company, self.engine)
            .assign(week=lambda x: x.expected_receipt_date - x.expected_receipt_date.dt.weekday.astype('timedelta64[D]'))
        )

        df = (
            purchase_orders_df
            .groupby(by='week')
            .agg(
                quantity=('outstanding_quantity', 'sum'),
                lines=( 'outstanding_quantity', 'count'),
                orders=('document_no_', 'nunique'),
                gross_weight=('gross_weight', 'sum'),
                volume=('volume', 'sum'))
            .reset_index())

        # print(datetime.now().strftime('%b %Y'))
        p = figure(x_axis_type='datetime')
        source = ColumnDataSource(df)
        p.vbar(x='week', top='quantity', source=source)
        p.xaxis.formatter = DatetimeTickFormatter(months=['%b %Y'])
        # p.xaxis.formatter = FuncTickFormatter(code='''
        #     var d = new Date(tick);
        #     console.log('tick', d);
        #     return d.toLocaleDateString('es-ES', {year: 'numeric', month: 'long'})

        # ''')
        # p.yaxis.formatter = NumeralTickFormatter(language='es')
        p.yaxis.formatter = FuncTickFormatter(code='''
            return tick.toLocaleString('pt-BR')
        ''')
        return pn.pane.Bokeh(p)
        return s  # .servable()

    def run_altair(self) -> None:
        s = pn.Column('# Hola')
        time_locale = {
            "dateTime": "%A, %e de %B de %Y, %X",
            "date": "%d/%m/%Y",
            "time": "%H:%M:%S",
            "periods": ["AM", "PM"],
            "days": ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
            "shortDays": ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
            "months": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
            "shortMonths": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        }
        alt.renderers.set_embed_options(timeFormatLocale=time_locale)
        script = pn.pane.HTML('''<script type="text/javascript">
        vega.timeFormatLocale({
            "dateTime": "%A, %e de %B de %Y, %X",
            "date": "%d/%m/%Y",
            "time": "%H:%M:%S",
            "periods": ["AM", "PM"],
            "days": ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
            "shortDays": ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
            "months": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
            "shortMonths": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        });
        vega.formatLocale({
          "decimal": ",",
          "thousands": ".",
          "grouping": [3],
          "currency": ["", "\u00a0€"]
        });
        </script>''')

        purchase_orders_df = (
            get_purchase_orders_df(self.nav_company, self.engine)
            .assign(week=lambda x: x.expected_receipt_date - x.expected_receipt_date.dt.weekday.astype('timedelta64[D]'))
        )

        df = (
            purchase_orders_df
            .groupby(by='week')
            .agg(
                quantity=('outstanding_quantity', 'sum'),
                lines=( 'outstanding_quantity', 'count'),
                orders=('document_no_', 'nunique'),
                gross_weight=('gross_weight', 'sum'),
                volume=('volume', 'sum'))
            .reset_index())

        chart1 = alt.Chart(df).mark_bar().encode(
            x=alt.X('week:T', title='Fecha recepción esperada'),
            y=alt.Y('quantity:Q', title='Unidades'),
        ).properties(title='Unidades por día')
        return pn.Column(
            script,
            pn.pane.Markdown('# Cuadro de mando almacén'),
            pn.panel(chart1))

    run = run_altair


if __name__ == '__main__':
    App().run().serve()
