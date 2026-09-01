from fastembed import TextEmbedding


class FastEmbedProvider:
    def __init__(self, model_name: str):
        self._model = TextEmbedding(model_name=model_name)

    def embed(self, text: str) -> list[float]:
        [vector] = list(self._model.embed([text]))
        return vector.tolist()
