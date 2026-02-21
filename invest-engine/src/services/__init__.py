"""
Services module
"""
from .translator import news_translator, translate_news_batch, translate_title

__all__ = ['news_translator', 'translate_news_batch', 'translate_title']