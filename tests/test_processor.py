from src.transcriber import Transcription, Segment


def test_full_text():
    # cria uma transcrição com 2 segmentos
    segment1 = Segment(start=0, end=5, text="Hello")
    segment2 = Segment(start=5, end=10, text="World")
    transcription = Transcription(
        language="en", language_probability=0.99, segments=[segment1, segment2]
    )

    # verifica se full_text retorna o texto concatenado
    assert transcription.full_text == "Hello World"
