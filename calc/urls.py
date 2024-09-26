from django.urls import path
from . import views

urlpatterns = [
    # /calc, opening file via different buttons
    path('', views.CalcHtmlView.as_view(), name="calc_view"),
    # /calc/object
    # path('object', views.ButtonsResponseObjectView.as_view(), name="object_views_2"),
    # /calc/object/..., three methods: path, post, ajax
    path('object/<str:flag>', views.ButtonsResponseObjectView.as_view(), name="object_views"),
    # /calc/raw
    path('raw', views.RawFileView.as_view(), name="open_raw_file_filter"),
    # /calc/raw/...,
    path('raw/<str:flag>', views.RawFileView.as_view(), name="raw_views"),
    # /calc/params/...
    path('params/<str:flag>', views.ParamsSettingView.as_view(), name="params_views"),
    # /calc/thermo/...
    path('thermo', views.ThermoView.as_view(), name="thermo_home"),
    path('thermo/<str:flag>', views.ThermoView.as_view(), name="thermo_views"),
    # api
    path('api/<str:flag>', views.ApiView.as_view(), name="api_views"),
]
