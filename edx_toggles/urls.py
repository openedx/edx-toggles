# -*- coding: utf-8 -*-
"""
URLs for edx_toggles.
"""


from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url("", TemplateView.as_view(template_name="edx_toggles/base.html")),
]
