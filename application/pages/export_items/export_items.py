"""Exportar artículos de Navision a Excel y Google Drive (per-user OAuth)."""
from datetime import datetime
from io import BytesIO
import traceback

from application.config import param_cache2
from application.config.config import Config
from my_panel_extensions.site import site
import pandas as pd
import panel as pn
import param
import panel_material_ui as pmui
from sqlalchemy import URL

from application.pages.export_items.models import Item, Title
from application.pages.export_items.repository.navision_backend import NavisionRepository
from template import MyMaterialTemplate


pn.extension('tabulator')

LOCALE = 'es'

TRANSLATIONS = {
    'es': {
        'title': 'Exportar artículos',
        'filters': 'Filtros',
        'state': 'Estado',
        'all': 'Todos',
        'active': 'ACTIVO',
        'inactive': 'BAJA',
        'partial': 'PARCIAL',
        'item_line': 'Línea artículo',
        'search': 'No. o descripción...',
        'fetch_button': 'Obtener artículos',
        'fields_section': 'Campos a exportar',
        'download': 'Descargar Excel',
        'no_results': 'No se encontraron artículos',
        'found_count': 'Se encontraron {count} artículo(s)',
        'error_fetch': 'Error al obtener artículos',
        'google_drive': 'Google Drive',
        'connected': 'Conectado',
        'not_connected': 'No conectado',
        'connect': 'Conectar',
        'disconnect': 'Desconectar',
        'export_to_drive': 'Exportar a Google Drive',
        'select_folder': 'Seleccionar carpeta',
        'confirm_upload': 'Confirmar y subir',
        'cancel': 'Cancelar',
        'upload_success': 'Archivo subido a Google Drive',
        'upload_error': 'Error al subir',
        'basic': 'Básicos',
        'product': 'Producto',
        'state_status': 'Estado',
        'barcodes': 'Códigos de barras',
        'sales': 'Ventas',
        'unit_of_measures': 'Unidades de medida',
        'features': 'Características',
        'extended_text': 'Texto extendido',
        'active_option': 'ACTIVO',
        'inactive_option': 'BAJA',
        'partial_option': 'PARCIAL',
    },
    'en': {
        'title': 'Export Items',
        'filters': 'Filters',
        'state': 'State',
        'all': 'All',
        'active': 'ACTIVE',
        'inactive': 'INACTIVE',
        'partial': 'PARTIAL',
        'item_line': 'Item Line',
        'search': 'No. or description...',
        'fetch_button': 'Get Items',
        'fields_section': 'Fields to Export',
        'download': 'Download Excel',
        'no_results': 'No items found',
        'found_count': 'Found {count} item(s)',
        'error_fetch': 'Error fetching items',
        'google_drive': 'Google Drive',
        'connected': 'Connected',
        'not_connected': 'Not connected',
        'connect': 'Connect',
        'disconnect': 'Disconnect',
        'export_to_drive': 'Export to Google Drive',
        'select_folder': 'Select folder',
        'confirm_upload': 'Confirm and upload',
        'cancel': 'Cancel',
        'upload_success': 'File uploaded to Google Drive',
        'upload_error': 'Error uploading',
        'basic': 'Basic',
        'product': 'Product',
        'state_status': 'State',
        'barcodes': 'Barcodes',
        'sales': 'Sales',
        'unit_of_measures': 'Unit of Measures',
        'features': 'Features',
        'extended_text': 'Extended Text',
        'active_option': 'ACTIVE',
        'inactive_option': 'INACTIVE',
        'partial_option': 'PARTIAL',
    },
}


def _(key: str, **kwargs) -> str:
    text = TRANSLATIONS.get(LOCALE, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


APPLICATION_NAME = 'Panel - Exportar producto'
APPLICATION = site.create_application(
    url='export_items',
    name=APPLICATION_NAME,
    description='Exporta artículos de Navision a Excel y Google Drive.',
    description_long=__doc__,
    thumbnail='/assets/images/thumbnails/manage_apps.png',
    tags=['comercial'],
)
FEATURE_PROFILE = 'PRODUCTO'

FIELD_GROUPS = {
    'basic': ['no_', 'description', 'description_2'],
    'product': ['item_line_code', 'item_line_name', 'npd_code', 'npd_name',
                'division_code', 'division_name', 'life_cycle_code',
                'life_cycle_name', 'campaign_code', 'campaign_name'],
    'state_status': ['state', 'blocked', 'blocked___quot__ord__sales_', 'report_order'],
    'barcodes': ['ean_no_', 'dun14_no_', 'vendor_item_no_', 'vendor_item_description'],
    'sales': ['sales_order_multiple', 'unit_volume', 'royalty__', 'vendor_no_',
              'price_a', 'price_b', 'price_i', 'price_p', 'price_ddp', 'price_r',
              'tariff_no_'],
    'unit_of_measures': ['std_quantity', 'std_height', 'std_width', 'std_length',
                         'std_cubage', 'std_weight', 'std_state',
                         'uds_height', 'uds_width', 'uds_length', 'uds_cubage',
                         'uds_weight', 'uds_state',
                         'product_height', 'product_width', 'product_length',
                         'product_weight', 'product_state',
                         'pallet_quantity', 'pallet_height', 'pallet_cubage',
                         'pallet_weight', 'pallet_layers', 'pallet_qty__per_layer',
                         'pallet_state',
                         'cont20_quantity', 'cont40_quantity', 'cont40h_quantity'],
    'features': ['features'],
    'extended_text': ['extended_text_1', 'extended_text_2', 'extended_text_3',
                      'extended_text_4', 'extended_text_5', 'extended_text_6',
                      'extended_text_7', 'extended_text_8', 'extended_text_9',
                      'extended_text_10'],
}

ALL_FIELDS = [f for group in FIELD_GROUPS.values() for f in group]


def get_field_title(field_name: str, locale: str) -> str:
    for metadata in Item.model_fields.get(field_name, {}).metadata or []:
        if isinstance(metadata, Title):
            return getattr(metadata, locale, field_name)
    return field_name


class ExportItemsApp(param.Parameterized):
    """Export items from Navision."""

    get_nav_company = param.Callable()
    get_nav_dburi = param.Callable()
    open_modal = param.Callable()
    close_modal = param.Callable()

    filter_state = param.Selector(objects=['Todos', 'ACTIVO', 'EN-ESTUDIO', 'HISTÓRICO'], default='ACTIVO')
    filter_item_line = param.Selector(objects={'Todos': ''}, default='')
    filter_search = param.String(default='', label=_('search'))

    items_df = param.DataFrame()
    alerts = param.List(default=[])
    loading = param.Boolean(default=False)
    modal_view = param.Parameter()

    _selected_folder_id = param.String(default=None)
    _gdrive_connected = param.Boolean(default=False)

    def __init__(self, **params):
        super().__init__(**params)
        self.repository = NavisionRepository(
            conn_url=self.get_nav_dburi(),
            nav_company=params['get_nav_company'](),
        )
        self._username = self._get_username()
        self._field_states = {f: f in ['no_', 'description'] for f in ALL_FIELDS}
        self._load_saved_fields()
        self._check_gdrive_connection()
        self._load_categories()
        self._build_settings_panel()

    def _get_username(self) -> str | None:
        try:
            request = pn.state.curdoc.session_context.request
            user_cookie = request.cookies.get("user")
            if user_cookie:
                import json
                return json.loads(user_cookie.value)
        except Exception:
            pass
        return None

    def _load_saved_fields(self):
        if self._username:
            try:
                saved = param_cache2.get(
                    ['export_items', self._username, 'selected_fields'],
                    default=['no_', 'description']
                )
                if saved and isinstance(saved, list):
                    for f in ALL_FIELDS:
                        self._field_states[f] = f in saved
            except Exception:
                pass

    def _save_selected_fields(self):
        if self._username:
            try:
                selected = [f for f in ALL_FIELDS if self._field_states.get(f, False)]
                param_cache2.set(['export_items', self._username, 'selected_fields'], selected)
            except Exception:
                pass

    def _get_selected_fields(self) -> list[str]:
        return [f for f in ALL_FIELDS if self._field_states.get(f, False)]

    def _toggle_field(self, field: str):
        self._field_states[field] = not self._field_states.get(field, False)
        self._save_selected_fields()

    def _check_gdrive_connection(self):
        if not self._username:
            self._gdrive_connected = False
            return
        try:
            from application.config.gdrive_oauth import get_credentials
            creds = get_credentials(self._username)
            self._gdrive_connected = creds is not None and creds.valid
        except Exception:
            self._gdrive_connected = False

    def _load_categories(self):
        try:
            lines = self.repository.get_lines()
            self.param.filter_item_line.objects = {'Todos': '', **lines}
        except Exception:
            self.param.filter_item_line.objects = {'Todos': ''}

    def _build_settings_panel(self):
        self.state_select = pmui.Select.from_param(
            self.param.filter_state, name=_('state'), width=200)
        self.line_select = pmui.Select.from_param(
            self.param.filter_item_line, name=_('item_line'), width=200)
        self.search_input = pmui.TextInput.from_param(
            self.param.filter_search, placeholder=_('search'), width=200)
        self.fetch_button = pmui.Button(
            name=_('fetch_button'), button_type='primary', icon='search',
            width=200)
        self.fetch_button.on_click(lambda e: self.fetch_items())

        self.download_button = pmui.Button(
            name=_('download'), button_type='warning', icon='download',
            disabled=True, width=200)
        self.download_button.on_click(lambda _: None)

        self.settings_panel = pn.Column(
            pn.pane.Markdown(f'### {_("filters")}'),
            self.state_select,
            self.line_select,
            self.search_input,
            pn.Spacer(height=10),
            self.fetch_button,
            pn.Spacer(height=10),
            pn.pane.Markdown(f'### {_("fields_section")}'),
            self._build_field_selector(),
            pn.Spacer(height=10),
            pn.pane.Markdown(f'### {_("download")}'),
            self.download_button,
        )

    def _build_field_selector(self) -> pn.Column:
        rows = []
        for group_key, group_fields in FIELD_GROUPS.items():
            all_checked = all(self._field_states.get(f, False) for f in group_fields)
            some_checked = any(self._field_states.get(f, False) for f in group_fields)

            def make_group_toggle(fields):
                def toggle(*_):
                    currently_all = all(self._field_states.get(f, False) for f in fields)
                    for f in fields:
                        self._field_states[f] = not currently_all
                    self._save_selected_fields()
                    self._refresh_field_selector()
                return toggle

            group_cb = pmui.Checkbox(
                name=_(group_key),
                value=all_checked,
                width=200,
            )
            group_cb.param.watch(make_group_toggle(group_fields), 'value')

            rows.append(pn.Row(group_cb, pn.pane.Markdown(f'**{_(group_key)}**')))

            for field in group_fields:
                field_title = get_field_title(field, LOCALE)

                def make_field_toggle(fname):
                    def toggle(*_):
                        self._toggle_field(fname)
                        self._refresh_field_selector()
                    return toggle

                field_cb = pmui.Checkbox(
                    name=field_title,
                    value=self._field_states.get(field, False),
                    width=200,
                )
                field_cb.param.watch(make_field_toggle(field), 'value')
                rows.append(pn.Row(pn.layout.Spacer(width=20), field_cb))

        self._field_selector_container = pn.Column(*rows, scroll=True)
        return self._field_selector_container

    def _refresh_field_selector(self) -> None:
        new_content = self._build_field_selector()
        if hasattr(self, '_field_selector_container'):
            self.settings_panel[4] = new_content

    def fetch_items(self, *args) -> None:
        self.loading = True
        self.alerts = []
        filters = {
            'state': self.filter_state,
            'item_line': self.filter_item_line,
            'search': self.filter_search,
        }
        selected_fields = self._get_selected_fields()
        try:
            lines = self.repository.get_lines()
            self.param.filter_item_line.objects = {'Todos': '', **lines}
            items = list(self.repository.get_items(
                filters=filters,
                fields=selected_fields,
                feature_profile=FEATURE_PROFILE,
            ))
            if items:
                item_dicts = []
                for item in items:
                    item_dict = item.model_dump(exclude_none=False)
                    filtered_keys = set(selected_fields)
                    if 'features' in selected_fields:
                        feature_cols = [k for k in item_dict.keys() if k.startswith('Feature_')]
                        filtered_keys.update(feature_cols)
                    filtered_dict = {k: v for k, v in item_dict.items() if k in filtered_keys}
                    if 'features' in filtered_dict and filtered_dict['features'] is None:
                        del filtered_dict['features']
                    item_dicts.append(filtered_dict)
                self.items_df = pd.DataFrame(item_dicts)
                titles = {f: get_field_title(f, LOCALE) for f in selected_fields if f in self.items_df.columns}
                if 'features' in selected_fields:
                    feature_cols = [c for c in self.items_df.columns if c.startswith('Feature_')]
                    for fc in feature_cols:
                        titles[fc] = fc.replace('_', ' ').replace('Feature ', 'Feature: ')
                self.items_df.columns = [titles.get(c, c) for c in self.items_df.columns]
            else:
                self.items_df = pd.DataFrame()
            self.download_button.disabled = self.items_df.empty
            count = len(self.items_df)
            self.alerts = [pmui.Alert(
                _('found_count', count=count) if count > 0 else _('no_results'),
                alert_type='success' if count > 0 else 'warning'
            )]
        except Exception as e:
            self.alerts = [pmui.Alert(f'{_("error_fetch")}: {e}', alert_type='danger')]
            traceback.print_exc()
            self.items_df = None
        finally:
            self.loading = False

    def _generate_excel(self) -> BytesIO:
        df = self.items_df.copy()
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Artículos')
        bio.seek(0)
        return bio

    @pn.depends('items_df', 'loading', 'alerts')
    def view(self) -> pn.Column:
        if self.loading:
            return pn.Column(
                pn.indicators.LoadingSpinner(value=True, size=50, align='center'),
                pn.pane.Markdown(_('fetch_button') + '...', align='center'))

        elements = [*self.alerts]

        if self.items_df is not None and not self.items_df.empty:
            self.tabulator = pn.widgets.Tabulator(
                self.items_df,
                disabled=True,
                pagination='local',
                page_size=25,
                sortable=True,
                theme='fast',
                sizing_mode='stretch_width',
                height=600,
            )
            elements.append(self.tabulator)
        elif self.items_df is not None:
            elements.append(pn.pane.Markdown(
                _('no_results'), align='center'))

        return pn.Column(*elements, scroll=True)

    @pn.depends('modal_view')
    def modal(self) -> pn.Column:
        return self.modal_view


def get_nav_dburi() -> URL:
    from application.config.urls import mssql_url
    nav_secrets = Config()['navision']
    return mssql_url(nav_secrets, APPLICATION_NAME, Mars_Connection='Yes')


def get_nav_company():
    nav_secrets = Config()['navision']
    return nav_secrets['company']


@site.add(APPLICATION)
def view() -> MyMaterialTemplate:
    pn.config.sizing_mode = "stretch_width"
    app = ExportItemsApp(
        name=APPLICATION.name,
        get_nav_dburi=get_nav_dburi,
        get_nav_company=get_nav_company,
        open_modal=lambda event: template.open_modal(),
        close_modal=lambda event: template.close_modal())
    template = MyMaterialTemplate(title=APPLICATION.name)
    template.append_sidebar(pn.pane.HTML('<hr/>'))
    template.append_sidebar(app.settings_panel)
    template.main.append(app.view)
    template.modal.append(app.modal)

    def generate_excel_callback():
        return app._generate_excel()

    template.download_button = pn.widgets.FileDownload(
        callback=generate_excel_callback,
        filename='articulos.xlsx',
        label=_('download'),
        button_type='warning',
        icon='download',
        disabled=True,
        width=200,
    )
    template.append_sidebar(pn.pane.Markdown(f'### {_("download")}'))
    template.append_sidebar(template.download_button)

    def update_download_state(*_):
        if app.items_df is not None and not app.items_df.empty:
            template.download_button.disabled = False
        else:
            template.download_button.disabled = True

    app.param.watch(update_download_state, 'items_df')

    return template


if __name__.startswith("bokeh"):
    view().servable()
