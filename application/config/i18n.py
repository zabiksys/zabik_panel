from bokeh.resources import Resources

import panel as pn
import param


# https://flatpickr.js.org/localization/
# must wait until flatpickr es is available
def datepicker(lang: str) -> pn.Column:
    if lang == 'es':
        # @classmethod
        # def serialize(cls, value):
        #     return value.strftime("%d-%m-%Y")

        # @classmethod
        # def deserialize(cls, value):
        #     return dt.datetime.strptime(value, "%d-%m-%Y").date()
        # if not param.CalendarDate.serialize is serialize:
        #     param.CalendarDate.serialize = serialize
        # if not param.CalendarDate.deserialize is deserialize:
        #     param.CalendarDate.deserialize = deserialize

        #pn.config.js_files['flatpickr-es'] = "https://npmcdn.com/flatpickr/dist/l10n/es.js"
        #res = Resources(mode='inline', version=None, root_dir=None, minified=False, log_level='info', root_url=None, path_versioner=None, components=None)
        #res.js_raw.append('/* my javascript */')
        #return pn.pane.HTML('<script src="https://npmcdn.com/flatpickr/dist/l10n/es.js"></script>\n'
        return pn.pane.HTML(
                       '<script type="text/javascript">\n'
                       'var refreshIntervalId = null;\n'
                       'var checkIfVariableIsSet = function() {\n'
                       '    if(typeof flatpickr.l10ns.es !== "undefined"){\n'
                       '        flatpickr.localize(flatpickr.l10ns.es);\n'
                       '        flatpickr(".flatpickr-input", {dateFormat: "d-m-Y"});\n'
                       '        clearInterval(refreshIntervalId);\n'
                       '    }\n'
                       '};\n'
                       'refreshIntervalId = setInterval(checkIfVariableIsSet, 1000);\n'
                       '</script>')



        # script = pn.pane.HTML('''<script type="text/javascript">
        # vega.timeFormatLocale({
        #     "dateTime": "%A, %e de %B de %Y, %X",
        #     "date": "%d/%m/%Y",
        #     "time": "%H:%M:%S",
        #     "periods": ["AM", "PM"],
        #     "days": ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
        #     "shortDays": ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
        #     "months": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
        #     "shortMonths": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        # });
        # vega.formatLocale({
        #   "decimal": ",",
        #   "thousands": ".",
        #   "grouping": [3],
        #   "currency": ["", "\u00a0€"]
        # });
        # console.log('hola');
        # </script>''')
