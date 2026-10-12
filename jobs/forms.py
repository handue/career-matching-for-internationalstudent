"""Validate collection options from the web form. / 웹 폼의 수집 옵션을 검증합니다."""
from django import forms


class CollectionForm(forms.Form):
    discover = forms.BooleanField(required=False, label="Discover new companies")
    search_limit = forms.IntegerField(min_value=1, initial=5, label="Postings to save")
    analyze_limit = forms.IntegerField(min_value=1, initial=1, label="Postings to analyze")
    model = forms.CharField(max_length=100, initial="qwen3:8b", label="Ollama model")
