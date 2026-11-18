import soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro("/home/claude/tts/kokoro-v1.0.onnx", "/home/claude/tts/voices-v1.0.bin")
ref = "The Romans moved a quarter of a million tonnes of stone without a single truck. Every block was cut by hand, hauled by oxen, and locked in place with iron. Nobody knows exactly how many people it took. But we can work out the bill."
V = {"onyx": 0.6*k.get_voice_style("am_onyx")+0.4*k.get_voice_style("am_michael"),
     "lewis": 0.6*k.get_voice_style("bm_lewis")+0.4*k.get_voice_style("bm_george"),
     "adam": 0.5*k.get_voice_style("am_adam")+0.5*k.get_voice_style("am_onyx")}
for n,s in V.items():
    a,sr = k.create(ref, voice=s, speed=0.9, lang="en-gb" if n=="lewis" else "en-us"); sf.write(f"base_{n}.wav", a, sr)
