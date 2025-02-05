import torch
import torchaudio
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline
from ..core.config import settings

class AudioProcessor:
    def __init__(self):
        self.asr_pipe = None
        self.diarization_pipe = None
        self.initialize_models()

    def initialize_models(self):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        processor = AutoProcessor.from_pretrained(settings.MODEL_NAME)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            settings.MODEL_NAME,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
        ).to(device)

        self.asr_pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            chunk_length_s=15,
            stride_length_s=2,
            return_timestamps=True,
            generate_kwargs={"task": "transcribe", "language": "fr"}
        )

        self.diarization_pipe = Pipeline.from_pretrained(
            settings.DIARIZATION_MODEL,
            use_auth_token=settings.HF_TOKEN
        ).to(device)

    def diarize_audio(self, audio_file_path: str, asr_pipe, diarization_pipe):
        # Load and preprocess audio
        waveform, sample_rate = torchaudio.load(audio_file_path)
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Resample if necessary
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
        
        # Get ASR results
        asr_result = self.asr_pipe(audio_file_path)
        asr_segments = asr_result.get("chunks", [])
        
        # Pass waveform directly to diarization pipeline
        diarization = self.diarization_pipe({
            "waveform": waveform,
            "sample_rate": 16000
        })
        
        # Convert diarization to dictionary format
        diar_dict = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start_time = turn.start
            end_time = turn.end
            for t in np.arange(start_time, end_time, 0.1):
                diar_dict[round(t, 1)] = speaker

        # Combine ASR and diarization
        diarized_segments = []
        for segment in asr_segments:
            if "timestamp" not in segment or None in segment["timestamp"]:
                continue

            start_time, end_time = segment["timestamp"]
            text = segment.get("text", "").strip()
            
            times = np.arange(start_time, end_time, 0.1)
            speakers = [diar_dict.get(round(t, 1)) for t in times if round(t, 1) in diar_dict]
            if speakers:
                speaker = max(set(speakers), key=speakers.count)
            else:
                speaker = "UNKNOWN"

            diarized_segments.append({
                "speaker": speaker,
                "start": start_time,
                "end": end_time,
                "text": text
            })

        # Merge consecutive segments from the same speaker
        return self.merge_segments(diarized_segments)

    def process_audio_segment(self, waveform, start_time, end_time, sample_rate=16000):
        if start_time is None or end_time is None:
            return None
        
        try:
            start_frame = int(float(start_time) * sample_rate)
            end_frame = int(float(end_time) * sample_rate)
            target_length = 160000  # Fixed length for all segments
            
            segment = waveform[:, start_frame:end_frame]
            
            # Pad or trim to target length
            if segment.shape[1] < target_length:
                padding = torch.zeros((1, target_length - segment.shape[1]))
                segment = torch.cat([segment, padding], dim=1)
            elif segment.shape[1] > target_length:
                segment = segment[:, :target_length]
                
            segment = segment / (torch.max(torch.abs(segment)) + 1e-6)
            return segment
        except (ValueError, TypeError):
            return None

    def merge_segments(self, segments, time_threshold=0.2):
        if not segments:
            return []
            
        merged = []
        current = segments[0].copy()
        
        for next_seg in segments[1:]:
            if (current["speaker"] == next_seg["speaker"] 
                and next_seg["start"] - current["end"] <= time_threshold
                and len(current["text"].split()) < 35):
                
                current["end"] = next_seg["end"]
                current["text"] += " " + next_seg["text"]
            else:
                merged.append(current)
                current = next_seg.copy()
        
        merged.append(current)
        return merged

    async def process_audio_file(self, audio_file_path: str):
        segments = self.diarize_audio(audio_file_path, self.asr_pipe, self.diarization_pipe)
        
        return {
            "segments": [
                {
                    "timestamp": {
                        "start": round(seg["start"], 2),
                        "end": round(seg["end"], 2)
                    },
                    "speaker": seg["speaker"],
                    "text": seg["text"]
                }
                for seg in segments
            ]
        } 