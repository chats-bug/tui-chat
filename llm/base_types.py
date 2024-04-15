from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Optional, Sequence, Tuple


class ModelType(Enum):
    TEXT = "text"
    IMAGE = "image"
    IMAGE_GENERATION = "image_generation"
    EMBEDDING = "embedding"


class OpenAiChatModels(Enum):
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4_TURBO_1106_PREVIEW = "gpt-4-1106-preview"

    GPT_4_VISION_PREVIEW = "gpt-4-vision-preview"

    DALL_E_3 = "dall-e-3"

    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_1106 = "gpt-3.5-turbo-1106"
    GPT_3_5_TURBO_0125 = "gpt-3.5-turbo-0125"

    def __str__(self):
        return f"OpenAiChatModels(Model={self.value}, Token Limit={self.token_limit})"

    @property
    def type(self) -> ModelType:
        if self.value == "gpt-4-vision-preview":
            return ModelType.IMAGE
        elif "dall-e" in self.value:
            return ModelType.IMAGE_GENERATION
        # elif  embedding / image models
        #   return ModelType.EMBEDDING / ModelType.IMAGE
        return ModelType.TEXT

    @property
    def token_limit(self) -> tuple[int, float]:
        # Do a match case here
        match self.value:
            case ["gpt-4-turbo", "gpt-4-1106-preview"]:
                return 128_000, 4096
            case "gpt-4-32k":
                return 32_000, 32_000
            case "gpt-4":
                return 8_192, 8_192
            case ["gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125"]:
                return 16_385, 4095
            case "gpt-3.5-turbo":
                return 4_096, 4_096

    @property
    def cost_per_1000(self) -> Tuple[float, float]:
        if "gpt-4" in self.value:
            # Model belongs to GPT-4 family
            if "32k" in self.value:
                return 0.06, 0.12
            return 0.03, 0.06
        else:
            # Model belongs to GPT-3.5 family
            if "16k" in self.value:
                return 0.003, 0.004
            return 0.0015, 0.002


@dataclass
class OpenAIDecodingArguments:
    max_tokens: int = 4000
    temperature: float = 0.2
    top_p: float = 1.0
    n: int = 1
    stream: bool = False
    stop: Optional[Sequence[str]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    response_format: dict = field(default_factory=dict)
