from src.llm.fastembed_provider import FastEmbedProvider

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EXPECTED_DIMENSION = 384


def test_embed_returns_vector_of_expected_dimension():
    provider = FastEmbedProvider(model_name=MODEL_NAME)

    vector = provider.embed("My dog's name is Bruno.")

    assert isinstance(vector, list)
    assert len(vector) == EXPECTED_DIMENSION
    assert all(isinstance(x, float) for x in vector)
    assert any(x != 0.0 for x in vector)
