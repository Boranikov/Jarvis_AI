""" Jarvis graph sistemi """
from typing import TypedDict, Annotated, List, Any
from langchain_core.messages import BaseMessage
import operator

class JarvisState(TypedDict):
    """
    LangGraph üzerindeki tur boyunca taşınacak olan ortak hafıza (State).
    """
    # Mesaj geçmişi: operator.add sayesinde her node, mevcut listeye ekleme yapar.
    messages: Annotated[list[BaseMessage],operator.add]
    # Tool çağrısı sırasında oluşan potansiyel hataları tutmak için
    error: str | None