import pydantic


class Base(pydantic.BaseModel):
    target_language: str


class TextTranslation(Base):
    original_text: str
    translated_text: str
