# tests/test_integration.py
"""
전체 시스템 통합 테스트
STT → LLM → Global 변수 → 로봇 제어 → TTS 전체 파이프라인

오디오 파일이 없으면 자동으로 녹음합니다.

사용법:
    python test_integration.py
    python test_integration.py --stt google --llm gpt --tts clova
    python test_integration.py --text "로봇을 점 고정 모드로 변경해줘"
"""
import sys
import os

# 환경 변수 설정
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

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

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)  # 작업 디렉토리를 프로젝트 루트로 변경

import asyncio
import argparse
import threading
import time
import numpy as np
import sounddevice as sd
import wave
from core import get_stt_fn, get_llm_fn, get_tts_fn
from configs import globals as g
from utils.robot_commands import set_mode
from utils import Logger
from configs import SAMPLE_RATE, CHUNK_SIZE, OUTPUT_DIR

TEST_OUTPUT_DIR = os.path.join(project_root, "tests", "assets")
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def record_audio():
    """
    오디오 파일이 없으면 즉시 녹음
    
    Returns:
        str: 녹음된 파일 경로 또는 None
    """
    stop_event = threading.Event()
    frames = []
    audio_path = os.path.join(TEST_OUTPUT_DIR, "integration_test.wav")
    
    def record_loop():
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
            while not stop_event.is_set():
                data, _ = stream.read(CHUNK_SIZE)
                frames.append(data.copy())
    
    # 녹음 스레드 시작
    thread = threading.Thread(target=record_loop, daemon=True)
    thread.start()
    
    # 사용자 안내
    print("\n" + "="*60)
    print("🔴 [통합 테스트 녹음]")
    print("="*60)
    print("말을 하세요... (예: '로봇을 점 고정 모드로 변경해줘')")
    print("종료하려면 엔터(Enter)를 누르세요.\n")
    
    # 엔터 대기
    input()
    
    print("⏹️  [녹음 종료] 저장 중...")
    stop_event.set()
    thread.join(timeout=2)
    
    # 저장
    if frames and len(frames) > 0:
        audio_data = np.concatenate(frames, axis=0)
        
        # 최소 길이 체크 (0.5초)
        if len(audio_data) < SAMPLE_RATE * 0.5:
            Logger.warning(f"녹음이 너무 짧습니다 ({len(audio_data)/SAMPLE_RATE:.2f}초)")
            Logger.info("최소 0.5초 이상 녹음해주세요.")
            return None
        
        with wave.open(audio_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        
        duration = len(audio_data) / SAMPLE_RATE
        Logger.success(f"파일 저장: {audio_path} ({duration:.2f}초)")
        return audio_path
    else:
        Logger.error("녹음된 데이터 없음")
        Logger.info("마이크 연결을 확인하세요.")
        return None

def find_audio_file():
    """
    사용 가능한 오디오 파일 찾기
    우선순위: integration_test.wav → test_recording.wav → user_voice.wav
    
    Returns:
        str: 오디오 파일 경로 또는 None
    """
    candidates = [
        os.path.join(TEST_OUTPUT_DIR, "integration_test.wav"),
        os.path.join(TEST_OUTPUT_DIR, "test_recording.wav"),
        os.path.join(OUTPUT_DIR, "user_voice.wav")  # 메인 assets도 확인
    ]
    
    for path in candidates:
        if os.path.exists(path):
            Logger.info(f"오디오 파일 사용: {path}")
            return path
    
    return None

async def test_full_pipeline(args):
    """전체 음성 제어 파이프라인 테스트"""
    Logger.section("통합 테스트 시작")
    
    # 설정 정보 출력
    Logger.info(f"STT 엔진: {args.stt}")
    Logger.info(f"LLM 엔진: {args.llm}")
    Logger.info(f"TTS 엔진: {args.tts}")
    Logger.info(f"입력 모드: {'텍스트' if args.text else '음성'}")
    Logger.separator()
    
    # 엔진 초기화
    stt_fn = get_stt_fn(args.stt)
    llm_fn = get_llm_fn(args.llm)
    tts_fn = get_tts_fn(args.tts)
    
    # 1. 입력 처리 (텍스트 또는 음성)
    if args.text:
        # 텍스트 입력
        Logger.info("1단계: 텍스트 입력", emoji="⌨️")
        user_text = args.text
        Logger.success(f"입력 텍스트: {user_text}")
    else:
        # 음성 입력 (STT)
        Logger.info("1단계: 음성 인식 (STT)", emoji="🎤")
        
        # 오디오 파일 찾기 또는 녹음
        audio_path = find_audio_file()
        
        if not audio_path:
            Logger.warning("사용 가능한 오디오 파일이 없습니다.")
            Logger.info("지금 녹음을 시작합니다.")
            audio_path = record_audio()
            
            if not audio_path:
                Logger.error("녹음 실패, 테스트 중단")
                return
        
        user_text = stt_fn(audio_path)
        
        if not user_text:
            Logger.error("STT 실패")
            return
        
        Logger.success(f"STT 결과: {user_text}")
    
    # 2. LLM
    Logger.info("2단계: 명령 해석 (LLM)", emoji="🤖")
    command = await llm_fn(user_text)
    Logger.success(f"LLM 결과: {command}")
    
    # 3. Global 변수에 저장 (이미 llm_fn 내부에서 저장됨)
    Logger.info("3단계: Global 변수 저장", emoji="📋")
    Logger.success("Global 변수 저장 완료 (자동)")
    
    # 4. 로봇 명령 실행
    Logger.info("4단계: 로봇 제어", emoji="🤖")
    if command.get("action") == "mode":
        result = set_mode(command.get("aux0"))
        if result:
            Logger.success(f"로봇 응답: {result}")
            Logger.info(f"현재 모드: {g.get_robot_mode()}")
    else:
        Logger.warning("실행 가능한 명령이 없습니다")
    
    # 5. TTS
    Logger.info("5단계: 음성 피드백 (TTS)", emoji="🔊")
    feedback = command.get("aux1", "명령을 수행합니다")
    tts_fn(feedback)
    Logger.success("TTS 완료")
    
    # 6. 검증
    Logger.info("6단계: 상태 검증", emoji="✅")
    stored_command = g.get_voice_command()
    stored_raw = g.get_voice_command_raw()
    current_mode = g.get_robot_mode()
    Logger.success(f"저장된 명령 (dict): {stored_command}")
    Logger.success(f"저장된 명령 (raw): {stored_raw}")
    Logger.success(f"현재 로봇 모드: {current_mode}")
    
    Logger.section("통합 테스트 완료")


def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="통합 테스트 - STT → LLM → 로봇 제어 → TTS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
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
        help="텍스트 입력 모드 (음성 녹음 대신 텍스트 사용)"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(test_full_pipeline(args))
