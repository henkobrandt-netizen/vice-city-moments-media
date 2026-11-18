# Build Bill narrator "Adam" (chosen 18 Nov 2026)
Synthetic designed voice (no real person). Recipe:
1. Kokoro v1.0 style = 0.5*am_adam + 0.5*am_onyx, speed 0.9, lang en-us (make_base.py → base_adam.wav)
2. ffmpeg -af "rubberband=pitch=0.95:formant=shifted,highpass=f=70" -ar 24000 → adam_ref.wav
3. Chatterbox TTS (MIT) generate(text, audio_prompt_path="adam_ref.wav", exaggeration=0.7, cfg_weight=0.55, temperature=0.8)
4. Final pace: atempo=0.97 (user: "a tiny bit slower" than the 1.06 test). 0.25 s between lines inside a sentence group.
