# modules/ - STT/LLM/TTS 엔진 구현체

각 엔진의 클래스 기반 구현 + 편의 함수 제공

---

## 📄 stt_modules.py - Speech-to-Text

### WhisperSTT.transcribe(audio_path) → str | None
: OpenAI Whisper API로 음성 → 텍스트
```python
from modules.stt_modules import WhisperSTT

stt = WhisperSTT()
text = stt.transcribe("assets/user_voice.wav")
```
### GoogleSTT.transcribe(audio_path) → str | None
: Google Cloud STT API로 음성 → 텍스트
```python
from modules.stt_modules import GoogleSTT

stt = GoogleSTT()
text = stt.transcribe("assets/user_voice.wav")
```
### ClovaSTT.transcribe(audio_path) → str | None
: Naver Clova STT API로 음성 → 텍스트
```python
from modules.stt_modules import ClovaSTT

stt = ClovaSTT()
text = stt.transcribe("assets/user_voice.wav")
```

---

## 📄 llm_modules.py - Large Language Model

### GPT4oLLM.ask(text) → dict (async)
: GPT-4o API로 사용자 입력 → 로봇 명령 JSON 변환
```python
from modules.llm_modules import GPT4oLLM

llm = GPT4oLLM()
result = await llm.ask("점 고정 모드로 변경")
# {"action": "mode", "aux0": "point", "aux1": "점 고정 모드로 전환할게요."}
```

### GeminiLLM.ask(text) → dict (async)
: Gemini 2.0 API로 사용자 입력 → 로봇 명령 JSON 변환
```python
from modules.llm_modules import GeminiLLM

llm = GeminiLLM()
result = await llm.ask("로봇 정지")
```
=> 출력 구조 :
```python
{
    "action": "mode" | None,
    "aux0": "free" | "fix" | "point" | "line" | None,
    "aux1": "피드백 텍스트"
}
```

---

## 📄 tts_modules.py - Text-to-Speech

### GoogleTTS.speak(text) → None
: gTTS로 텍스트 → 음성 재생
```python
from modules.tts_modules import GoogleTTS

tts = GoogleTTS()
tts.speak("안녕하세요")
```
### OpenAITTS.speak(text) → None
: OpenAI TTS API로 텍스트 → 음성 재생
```python
from modules.tts_modules import OpenAITTS

tts = OpenAITTS(voice="nova")
tts.speak("명령 수행")
```
### ClovaTTS.speak(text) → None
: Clova TTS API로 텍스트 → 음성 재생
```python
from modules.tts_modules import ClovaTTS

tts = ClovaTTS(speaker="jinho", speed=0)
tts.speak("점 고정 모드")
```