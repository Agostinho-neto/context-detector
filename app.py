import streamlit as st
from pathlib import Path
import tempfile
import shutil

from src.extractor import extract_audio
from src.transcriber import transcribe_audio
from src.processor import save_transcription

VIDEO_EXTENSIONS = ["mp4", "mkv", "avi", "mov", "webm", "flv", "wmv"]

st.set_page_config(page_title="Context Detector", page_icon="🎬", layout="centered")

st.title("🎬 Context Detector")
st.markdown("Extraia áudio de vídeos e transcreva automaticamente.")
st.divider()

# Sidebar — configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    model_size = st.selectbox(
        "Modelo Whisper",
        options=["tiny", "base", "small", "medium", "large-v3"],
        index=1,
        help="Modelos maiores são mais precisos, mas mais lentos.",
    )
    st.markdown("""
    | Modelo | Qualidade | Velocidade |
    |---|---|---|
    | tiny | Básica | Muito rápido |
    | base | Boa | Rápido |
    | small | Muito boa | Médio |
    | medium | Ótima | Lento |
    | large-v3 | Máxima | Muito lento |
    """)

# Upload de vídeo
uploaded_file = st.file_uploader(
    "Envie seu vídeo",
    type=VIDEO_EXTENSIONS,
    help="Formatos suportados: MP4, MKV, AVI, MOV, WEBM, FLV, WMV",
)

if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("🚀 Transcrever", type="primary", use_container_width=True):
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Salvar vídeo temporário
            video_path = tmp_path / uploaded_file.name
            video_path.write_bytes(uploaded_file.getbuffer())

            # Pipeline
            with st.status("Processando...", expanded=True) as status:
                # 1. Extrair áudio
                st.write("🔊 Extraindo áudio do vídeo...")
                audio_path = extract_audio(video_path, tmp_path)

                # 2. Transcrever
                st.write(f"🧠 Transcrevendo com modelo **{model_size}**...")
                transcription = transcribe_audio(audio_path, model_size=model_size)

                # 3. Salvar
                st.write("💾 Salvando transcrições...")
                save_transcription(transcription, video_path.stem, output_dir)

                # Limpar áudio temp
                audio_path.unlink(missing_ok=True)

                status.update(label="Concluído!", state="complete", expanded=True)

            # Resultados
            st.divider()
            st.subheader("📝 Resultado")

            st.markdown(f"**Idioma detectado:** {transcription.language} ({transcription.language_probability:.0%})")
            st.markdown(f"**Segmentos:** {len(transcription.segments)}")

            # Texto completo
            st.text_area("Transcrição", transcription.full_text, height=300)

            # Downloads
            st.subheader("📥 Downloads")
            col1, col2, col3 = st.columns(3)

            txt_file = output_dir / f"{video_path.stem}.txt"
            srt_file = output_dir / f"{video_path.stem}.srt"
            json_file = output_dir / f"{video_path.stem}.json"

            with col1:
                if txt_file.exists():
                    st.download_button(
                        "📄 TXT",
                        txt_file.read_text(encoding="utf-8"),
                        file_name=txt_file.name,
                        mime="text/plain",
                        use_container_width=True,
                    )
            with col2:
                if srt_file.exists():
                    st.download_button(
                        "🎬 SRT",
                        srt_file.read_text(encoding="utf-8"),
                        file_name=srt_file.name,
                        mime="text/plain",
                        use_container_width=True,
                    )
            with col3:
                if json_file.exists():
                    st.download_button(
                        "📊 JSON",
                        json_file.read_text(encoding="utf-8"),
                        file_name=json_file.name,
                        mime="application/json",
                        use_container_width=True,
                    )
