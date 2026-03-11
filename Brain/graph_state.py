""" Jarvis graph sistemi """
from typing import TypedDict, Annotated, List, Any, Optional
from langchain_core.messages import BaseMessage
import operator

class JarvisState(TypedDict, total=False):
    """
    LangGraph üzerindeki tur boyunca taşınacak olan ortak hafıza (State).
    """
    messages: Annotated[list[BaseMessage], operator.add]
    error: Optional[str]
    intent: Optional[str]
    working_directory: str
    context_docs: list[str]
    expected_inputs: list[str]