from typing import Optional, List

from pydantic import BaseModel, model_validator


class MainResponse(BaseModel):
    thoughts: str
    ui_required: bool
    # html_structure: str
    components: Optional[List[str]]
    functionality: Optional[List[str]]


class HTMLResponse(BaseModel):
    raw_markdown: str

    @property
    def raw(self) -> str:
        return self.raw_markdown

    @property
    def get_html(self) -> str:
        """
        :return: The parsed HTML content.
        """
        # strip ```html and ```
        self.validate_html({"raw_markdown": self.raw_markdown})
        return self.raw_markdown[7:-3]

    # write a pydantic validator to check if the raw_markdown is a valid HTML content
    # if not valid, do not allow creation of the object
    # @model_validator(mode='before')
    @classmethod
    def validate_html(cls, v):
        # check if the raw_markdown is a valid HTML content
        v["raw_markdown"] = v["raw_markdown"].strip()
        if v["raw_markdown"].startswith("```html") and v["raw_markdown"].endswith("```"):
            return v
        raise ValueError("The raw_markdown is not a valid HTML content")


class CSSResponse(BaseModel):
    raw_markdown: str

    @property
    def raw(self) -> str:
        return self.raw_markdown

    @property
    def get_css(self) -> str:
        """
        :return: The parsed CSS content.
        """
        # strip ```css and ```
        self.validate_css({"raw_css": self.raw_markdown})
        return self.raw_markdown[6:-3]

    # write a pydantic validator to check if the raw_css is a valid CSS content
    # if not valid, do not allow creation of the object
    # @model_validator(mode='before')
    @classmethod
    def validate_css(cls, v):
        # check if the raw_css is a valid CSS content
        v["raw_css"] = v["raw_css"].strip()
        if v["raw_css"].startswith("```css") and v["raw_css"].endswith("```"):
            return v
        raise ValueError("The raw_css is not a valid CSS content")


class JSResponse(BaseModel):
    raw_markdown: str

    @property
    def raw(self) -> str:
        return self.raw_markdown

    @property
    def get_js(self) -> str:
        """
        :return: The parsed JS content.
        """
        # strip ```js and ```
        self.validate_js({"raw_js": self.raw_markdown})
        return self.raw_markdown[5:-3]

    # write a pydantic validator to check if the raw_js is a valid JS content
    # if not valid, do not allow creation of the object
    # @model_validator(mode='before')
    @classmethod
    def validate_js(cls, v):
        # check if the raw_js is a valid JS content
        v["raw_js"] = v["raw_js"].strip()
        if v["raw_js"].startswith("```js") and v["raw_js"].endswith("```"):
            return v
        raise ValueError("The raw_js is not a valid JS content")
