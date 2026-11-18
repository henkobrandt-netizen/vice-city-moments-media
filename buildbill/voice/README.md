# Build Bill narrator "Adam" (chosen 18 Nov 2026)
Synthetic designed voice (no real person). Recipe:
1. Kokoro v1.0 style = 0.5*am_adam + 0.5*am_onyx, speed 0.9, lang en-us (make_base.py → base_adam.wav)
2. ffmpeg -af "rubberband=pitch=0.95:formant=shifted,highpass=f=70" -ar 24000 → adam_ref.wav
3. Chatterbox TTS (MIT) generate(text, audio_prompt_path="adam_ref.wav", exaggeration=0.7, cfg_weight=0.55, temperature=0.8)
4. Post-process every line (FINAL, "Adam B", user: "PERFECT", 18 Nov 2026):
   ffmpeg -af "rubberband=pitch=1.05:formant=preserved,afftdn=nf=-30,equalizer=f=3500:t=q:w=1.2:g=-3,atempo=0.97"
   Median pitch about 115 Hz. Sample: adam_B_sample.mp3
