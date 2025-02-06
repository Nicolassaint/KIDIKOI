import streamlit as st
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
from collections import defaultdict, Counter
from css import TIMESTAMP_STYLE
from utils import (
    call_llm_API,
    analize_text,
    get_prompt,
    get_file_type,
    save_uploaded_file,
    transcribe_audio,
    transcribe_video,
    create_accessible_timestamps,
    create_word_document,
    process_transcript_with_rag,
)
from prompts import generate_meeting_analysis_prompts
import requests
import pandas as pd
import json
from json import JSONDecodeError


def format_for_llm(segments):
    # Input validation
    if not segments or not isinstance(segments, list):
        return {"error": "Invalid segments input"}

    # Create XML structure for better parsing
    xml_output = "<conversation>\n"

    # Group utterances by speaker
    for segment in segments:
        if (
            not isinstance(segment, dict)
            or "speaker" not in segment
            or "text" not in segment
        ):
            continue

        speaker_id = segment["speaker"]
        text = segment["text"].strip()
        timestamp = segment.get("timestamp", {})
        start_time = timestamp.get("start", "")
        end_time = timestamp.get("end", "")

        xml_output += f"""  <utterance>
    <speaker id="{speaker_id}">
      <text>{text}</text>
      <time start="{start_time}" end="{end_time}"/>
    </speaker>
  </utterance>\n"""

    xml_output += "</conversation>"
    return xml_output


def extract_speaker_names(segments):
    formatted_data = format_for_llm(segments)

    prompt = f"""TÂCHE: Extraire les identités des intervenants à partir de la transcription XML.

FORMAT DE LA TRANSCRIPTION:
{formatted_data}

INSTRUCTIONS:
1. Analyser les dialogues pour identifier les noms des intervenants
2. Chercher les formules d'introduction comme:
   - "Je m'appelle..."
   - "Je suis..."
   - "Moi c'est..."
   - Les mentions directes de noms
3. Vérifier les références croisées entre intervenants

RÉPONSE ATTENDUE:
Un objet JSON avec:
- Clés: IDs des speakers (format SPEAKER_XX avec deux chiffres)
- Valeurs: Noms identifiés ou "Inconnu"

Exemple:
{{
    "SPEAKER_01": "Vincent",
    "SPEAKER_02": "Elena",
    "SPEAKER_03": "Shogu",
    "SPEAKER_04": "Inconnu"
}}

RÈGLES STRICTES:
- Format JSON uniquement
- Pas de commentaires ou analyses
- Utiliser des guillemets doubles
- IDs au format SPEAKER_XX"""

    try:
        response = call_llm_API(prompt).strip()

        # Clean and validate JSON
        start_idx = response.find("{")
        end_idx = response.rfind("}")

        if start_idx == -1 or end_idx == -1:
            return {"error": "Format JSON invalide"}

        json_str = response[start_idx : end_idx + 1]
        parsed = json.loads(json_str)

        # Validate structure
        if not isinstance(parsed, dict):
            return {"error": "Format invalide: doit être un objet"}

        # Validate values
        for key, value in parsed.items():
            if not isinstance(value, str):
                return {"error": "Les valeurs doivent être des chaînes"}

        return parsed

    except json.JSONDecodeError:
        return {"error": "Erreur de parsing JSON"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}


class MediaProcessor:
    def __init__(self, media_type):
        self.media_type = media_type
        self.supported_types = {
            "audio": ["mp3", "wav", "ogg", "m4a", "flac"],
            "video": ["mp4", "avi", "mov", "mkv"],
        }
        self.transcription_key = f"transcription_{media_type}"

    def render_interface(self):
        st.header(f"Charger votre fichier {self.media_type.capitalize()}")

        uploaded_file = st.file_uploader(
            "Choisir un fichier",
            type=self.supported_types[self.media_type],
            help=f"Formats supportés: {', '.join(self.supported_types[self.media_type])}",
        )

        if uploaded_file:
            self._handle_file_preview(uploaded_file)
            if st.button("Transcription AUDIO"):
                self._process_json_file(uploaded_file)

        if st.session_state.get("transcription_json"):
            self._render_json_analysis()

    def _handle_file_preview(self, uploaded_file):
        file_type = get_file_type(uploaded_file.name)
        if not file_type:
            st.error("Format de fichier non supporté")
            return

        st.info(f"Format détecté : {file_type}")
        if self.media_type == "audio":
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

    def _process_json_file(self, uploaded_file):
        with st.spinner("Transcription AUDIO en cours..."):
            temp_file_path = save_uploaded_file(uploaded_file)
            files = {"file": open(temp_file_path, "rb")}
            response = requests.post(
                "https://dev.bhub.cloud/api/v1/transcribe/", files=files
            )

            if response.status_code == 200:
                st.session_state["transcription_json"] = response.json()
                st.session_state.current_transcription = " ".join(
                    [
                        segment["text"]
                        for segment in st.session_state["transcription_json"][
                            "segments"
                        ]
                    ]
                )
                st.success("Transcription JSON terminée!")
            else:
                st.error("Erreur lors de la transcription AUDIO")

    def _render_json_analysis(self):
        if (
            not st.session_state.get("transcription_json")
            or "segments" not in st.session_state["transcription_json"]
        ):
            st.warning("Aucune transcription disponible")
            return

        segments_data = [
            {
                "Début": segment["timestamp"]["start"],
                "Fin": segment["timestamp"]["end"],
                "Intervenant": segment["speaker"],
                "Texte": segment["text"],
            }
            for segment in st.session_state["transcription_json"]["segments"]
        ]

        with st.expander("📝 Transcription Détaillée", expanded=True):
            df = pd.DataFrame(segments_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "👥 Identifier les Intervenants",
                key=f"identify_speakers_{self.media_type}",
            ):
                with st.spinner("Identification des intervenants en cours..."):
                    speaker_map = extract_speaker_names(
                        st.session_state["transcription_json"]["segments"]
                    )
                    if "error" not in speaker_map:
                        st.session_state["speaker_map"] = speaker_map
                        st.success("Identification terminée!")
                    else:
                        st.error(speaker_map["error"])

        if st.session_state.get("speaker_map"):
            with st.expander("👤 Identités des Intervenants", expanded=True):
                st.markdown("### Participants Identifiés")
                for speaker_id, name in st.session_state["speaker_map"].items():
                    st.markdown(f"**{speaker_id}**: {name}")

        st.divider()

        base_prompts = generate_meeting_analysis_prompts(
            st.session_state.current_transcription
        )
        analysis_options = {
            "compte_rendu": "Compte-rendu détaillé",
            "qui_dit_quoi": "Attribution des propos",
            "questions_reponses": "Questions et réponses",
            "emotions": "Analyse émotionnelle",
            "statistiques": "Données statistiques",
            "mindmap": "Carte mentale",
            "points_focus": "Points d'attention majeurs",
        }

        st.markdown("### 📊 Analyses Disponibles")
        selected_analyses = st.multiselect(
            "Sélectionner les types d'analyses",
            options=list(analysis_options.keys()),
            default=st.session_state.get(f"selected_{self.media_type}", []),
            format_func=lambda x: analysis_options[x],
            key=f"analysis_json_{self.media_type}",
        )

        if st.button(
            "🚀 Lancer les analyses",
            disabled=len(selected_analyses) == 0,
            key=f"analyze_json_{self.media_type}",
        ):

            all_results = {}
            for analysis_type in selected_analyses:
                with st.spinner(f"Analyse en cours: {analysis_options[analysis_type]}"):
                    with st.expander(
                        f"📈 {analysis_options[analysis_type]}", expanded=True
                    ):
                        try:
                            if len(st.session_state.current_transcription) > 38000:
                                result, _ = process_transcript_with_rag(
                                    st.session_state.current_transcription,
                                    analysis_type,
                                )
                            else:
                                prompt = get_prompt(
                                    st.session_state.current_transcription,
                                    analysis_type,
                                )
                                result = call_llm_API(prompt) if prompt else None

                            if result:
                                all_results[analysis_options[analysis_type]] = result
                                st.markdown("---")
                                st.markdown(
                                    f"### Résultats: {analysis_options[analysis_type]}"
                                )
                                st.markdown(result)
                                st.success("✅ Analyse terminée")
                            else:
                                st.error("❌ Erreur: Analyse non générée")
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                        finally:
                            st.divider()

            if all_results:
                st.markdown("### 📑 Téléchargement du Rapport")
                word_doc = create_word_document(
                    st.session_state.current_transcription, all_results
                )
                st.download_button(
                    label="📁 Télécharger le Rapport Complet",
                    data=word_doc,
                    file_name="rapport_analyse.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

    def _process_analyses(self, selected_analyses, base_prompts, analysis_options):
        all_analysis = {}
        transcript = st.session_state.current_transcription

        for analysis_type in selected_analyses:
            with st.spinner(f"Analyse {analysis_options[analysis_type]}..."):
                with st.expander(f"📊 {analysis_options[analysis_type]}", expanded=True):
                    try:
                        if len(transcript) > 38000:
                            final_analysis, _ = process_transcript_with_rag(
                                transcript, analysis_type
                            )
                            if final_analysis:
                                all_analysis[
                                    base_prompts[analysis_type]["description"]
                                ] = final_analysis
                                st.success("Analyse RAG terminée")
                                st.markdown(final_analysis)
                        else:
                            prompt = get_prompt(transcript, analysis_type)
                            if prompt:
                                st.info("Prompt généré avec succès")
                                analysis = call_llm_API(prompt)
                                if analysis:
                                    all_analysis[
                                        base_prompts[analysis_type]["description"]
                                    ] = analysis
                                    st.success("Analyse terminée")
                                    st.markdown(analysis)
                                else:
                                    st.error(
                                        "Erreur: L'analyse n'a pas généré de résultat"
                                    )
                            else:
                                st.error(
                                    "Erreur: Impossible de générer le prompt pour ce type d'analyse"
                                )
                    except Exception as e:
                        st.error(f"Erreur lors de l'analyse: {str(e)}")
                    finally:
                        st.divider()

        if all_analysis:
            word_doc = create_word_document(transcript, all_analysis)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.download_button(
                    label="📁 Télécharger le Rapport",
                    data=word_doc,
                    file_name="rapport_analyse.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    on_click=lambda: [
                        st.session_state.messages.clear(),
                        st.session_state.pop("current_transcription", None),
                        st.session_state.pop(self.transcription_key, None),
                    ],
                    use_container_width=True,
                )


def record_audio():
    st.write("Enregistrement audio en direct")
    audio_bytes = audio_recorder(pause_threshold=3600)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        temp_audio_file = "temp_recording.wav"
        with open(temp_audio_file, "wb") as f:
            f.write(audio_bytes)

        if st.button("Transcrire l'enregistrement"):
            with st.spinner("Analyse..."):
                try:
                    result = transcribe_audio(temp_audio_file)
                    if "error" in result:
                        st.error(result["error"])
                        return None, None
                    else:
                        st.session_state.messages = []
                        st.session_state.current_transcription = result["transcription"]
                        return (
                            result["transcription"],
                            {"summary": analize_text(result["transcription"])},
                        )
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
                    return None, None
    return None, None


def main():
    st.set_page_config(page_title="Transcription Media")

    st.markdown(
        """
    <style>
    .fixed-chat {
        position: fixed;
        bottom: 0;
        left: 2%;
        right: 2%;
        background: white;
        z-index: 999;
        padding: 1rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        border-radius: 10px;
    }
    .chat-messages {
        max-height: 40vh;
        overflow-y: auto;
        margin-bottom: 1rem;
    }
    .main .block-container {
        padding-bottom: 200px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    session_keys = [
        "messages",
        "current_transcription",
        "transcription_audio",
        "transcription_video",
        "speaker_map",
    ]
    for key in session_keys:
        if key not in st.session_state:
            st.session_state[key] = [] if key == "messages" else None

    st.markdown(
        "<h1 style='text-align: center'>🗣️ KIDIKOI 👥</h1>", unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["🎧 Audio", "🎥 Vidéo", "🎤 Enregistrement"])

    with tab1:
        MediaProcessor("audio").render_interface()

    with tab2:
        MediaProcessor("video").render_interface()

    with tab3:
        st.header("Enregistrement Direct")
        transcrib, summary = record_audio()
        if transcrib is not None:
            word_doc = create_word_document(transcrib, summary)
            st.download_button(
                label="📁 Télécharger Rapport",
                data=word_doc,
                file_name="rapport_enregistrement.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                on_click=lambda: [
                    st.session_state.messages.clear(),
                    st.session_state.pop("current_transcription", None),
                ],
            )

    if st.session_state.current_transcription:
        with st.container():
            st.markdown('<div class="fixed-chat">', unsafe_allow_html=True)

            st.subheader("💬 Chat avec la Transcription")

            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            st.markdown("</div>", unsafe_allow_html=True)

            if prompt := st.chat_input("Poser une question..."):
                st.session_state.messages.append({"role": "user", "content": prompt})

                with st.chat_message("assistant"):
                    with st.spinner("Analyse..."):
                        response = call_llm_API(
                            f"""
                        Transcription: {st.session_state.current_transcription}
                        Question: {prompt}
                        Répondre en français de manière concise.
                        """
                        )
                        st.markdown(response)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 200px'></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
