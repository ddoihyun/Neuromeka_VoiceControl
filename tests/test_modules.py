# tests/test_modules.py
"""
개별 모듈 단위 테스트
- STT: Whisper, Google, Clova
- LLM: GPT, Gemini
- TTS: Google, OpenAI, Clova

사용법:
    python test_modules.py
    python test_modules.py --stt google --llm gpt --tts clova
    python test_modules.py --text "로봇을 점 고정 모드로 변경해줘"
    python test_modules.py --module stt
    python test_modules.py --module llm --llm gpt
"""
import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)

# ========================================
# Warning 필터링
# ========================================
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='keras')
warnings.filterwarnings('ignore', message='.*np.object.*')
warnings.filterwarnings('ignore', message='.*tf.lite.*')
warnings.filterwarnings('ignore', message='.*deprecated.*')

import asyncio
import argparse
from core import get_stt_fn, get_llm_fn, get_tts_fn
from utils import Logger
from configs import OUTPUT_DIR

TEST_OUTPUT_DIR = os.path.join(project_root, "tests", "assets")

def test_stt(stt_engine="whisper", audio_path=None):
    """
    STT 모듈 테스트
    Args:
        stt_engine: "whisper" | "google" | "clova"
        audio_path: 오디오 파일 경로 (None이면 자동 검색)
    Returns:
        인식된 텍스트 또는 None
    """
    Logger.section(f"STT 테스트 - {stt_engine.upper()}")
    
    # 오디오 파일 찾기
    if not audio_path:
        test_audio = os.path.join(TEST_OUTPUT_DIR, "test_recording.wav")
        integration_audio = os.path.join(TEST_OUTPUT_DIR, "integration_test.wav")
        user_audio = os.path.join(OUTPUT_DIR, "user_voice.wav")
        
        # 우선순위: test_recording → integration_test → user_voice
        for path in [test_audio, integration_audio, user_audio]:
            if os.path.exists(path):
                audio_path = path
                Logger.info(f"오디오 파일 사용: {path}")
                break
    
    if not audio_path or not os.path.exists(audio_path):
        Logger.error("오디오 파일 없음")
        Logger.info("다음 중 하나를 먼저 실행하세요:")
        Logger.info("  1. python tests/test_recording.py  (새로 녹음)")
        Logger.info("  2. python main.py --input mic  (main에서 녹음)")
        return None
    
    # STT 실행
    stt_fn = get_stt_fn(stt_engine)
    Logger.info(f"{stt_engine.upper()} STT 처리 중...", emoji="🎤")
    result = stt_fn(audio_path)
    
    if result:
        Logger.success(f"STT 결과: {result}")
    else:
        Logger.error("STT 실패")
    
    return result

async def test_llm(llm_engine="gemini", text=None):
    """
    LLM 모듈 테스트
    Args:
        llm_engine: "gemini" | "gpt"
        text: 입력 텍스트 (None이면 기본 문장 사용)
    Returns:
        LLM 응답 JSON
    """
    Logger.section(f"LLM 테스트 - {llm_engine.upper()}")
    
    # 기본 테스트 문장
    test_text = text or "로봇을 선 고정 모드로 변경해줘"
    Logger.info(f"입력 텍스트: {test_text}")
    
    # 빈 문자열 체크 추가
    if not test_text or test_text.strip() == "":
        test_text = "로봇을 선 고정 모드로 변경해줘"
        Logger.warning("입력 텍스트가 비어있어서 기본 문장 사용")
    
    Logger.info(f"입력 텍스트: {test_text}")

    # LLM 실행
    llm_fn = get_llm_fn(llm_engine)
    Logger.info(f"{llm_engine.upper()} LLM 처리 중...", emoji="🤖")
    result = await llm_fn(test_text)
    
    Logger.success(f"LLM 결과: {result}")
    
    return result

def test_tts(tts_engine="google", text=None, llm_result=None):
    """
    TTS 모듈 테스트
    Args:
        tts_engine: "google" | "openai" | "clova"
        text: 직접 입력 텍스트
        llm_result: LLM 결과 (aux1 추출)
    """
    Logger.section(f"TTS 테스트 - {tts_engine.upper()}")
    
    # 텍스트 결정 우선순위: text > llm_result["aux1"] > 기본 문장
    if text:
        tts_text = text
    elif llm_result and isinstance(llm_result, dict):
        tts_text = llm_result.get("aux1", "음성 합성 테스트입니다.")
    else:
        tts_text = "음성 합성 테스트입니다."
    
    Logger.info(f"TTS 텍스트: {tts_text}")
    
    # TTS 실행
    tts_fn = get_tts_fn(tts_engine)
    Logger.info(f"{tts_engine.upper()} TTS 재생 중...", emoji="🔊")
    tts_fn(tts_text)
    
    Logger.success("TTS 재생 완료")

async def run_selected_tests(args):
    """선택된 모듈 테스트 실행"""
    
    if args.module == "stt":
        # STT만 테스트
        test_stt(stt_engine=args.stt, audio_path=args.audio)
    
    elif args.module == "llm":
        # LLM만 테스트
        test_text = args.text or "로봇을 선 고정 모드로 변경해줘"
        await test_llm(llm_engine=args.llm, text=args.text)
    
    elif args.module == "tts":
        # TTS만 테스트
        test_tts(tts_engine=args.tts, text=args.text)
    
    else:
        # 전체 테스트 (STT → LLM → TTS)
        Logger.section("🧪 VoiceModular 모듈 전체 테스트")
        
        # 1. STT
        if args.text:
            Logger.info("텍스트 입력 모드: STT 건너뛰기")
            stt_result = args.text
        else:
            stt_result = test_stt(stt_engine=args.stt, audio_path=args.audio)
            if not stt_result or stt_result.strip() == "":
                Logger.error("STT 실패로 테스트 중단")
                return
        
        # 2. LLM
        llm_result = await test_llm(llm_engine=args.llm, text=stt_result)
        
        # 3. TTS
        test_tts(tts_engine=args.tts, llm_result=llm_result)
        
        Logger.section("✅ 모든 테스트 완료")

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="개별 모듈 단위 테스트",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--module",
        choices=["stt", "llm", "tts", "all"],
        default="all",
        help="테스트할 모듈 선택"
    )
    
    parser.add_argument(
        "--stt",
        choices=["whisper", "google", "clova"],
        default="whisper",
        help="STT 엔진 선택"
    )
    
    parser.add_argument(
        "--llm",
        choices=["gemini", "gpt"],
        default="gemini",
        help="LLM 엔진 선택"
    )
    
    parser.add_argument(
        "--tts",
        choices=["google", "openai", "clova"],
        default="google",
        help="TTS 엔진 선택"
    )
    
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="텍스트 입력 (STT 건너뛰기)"
    )
    
    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="오디오 파일 경로 지정"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(run_selected_tests(args))
