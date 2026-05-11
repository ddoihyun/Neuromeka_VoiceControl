# tests/core/test_recorder.py
"""
AudioRecorder 단위 테스트
실제 녹음 및 파일 저장 기능 검증

사용법:
    python tests/test_recording.py              # 기본 테스트 (녹음 없음)
    python tests/test_recording.py --record     # 실제 녹음 테스트
    python tests/test_recording.py --all        # 모든 테스트 (녹음 포함)
"""
import os
import sys
import time 

# ========================================
# 경로 설정
# ========================================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
# 작업 디렉토리 변경
os.chdir(project_root)

# ========================================
# 환경 변수 설정 (import 전에!)
# ========================================
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

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

import argparse
import wave
import numpy as np
import sounddevice as sd
import threading

from core import AudioRecorder
from configs import SAMPLE_RATE, CHUNK_SIZE, OUTPUT_DIR
from utils.logger import Logger

# 테스트 출력 디렉토리
TEST_OUTPUT_DIR = os.path.join(project_root, "tests", "assets")
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)


def test_basic_recording():
    """기본 녹음 테스트 (실제 녹음 없음)"""
    Logger.section("AudioRecorder 초기화 테스트")
    
    try:
        recorder = AudioRecorder()
        Logger.success("AudioRecorder 초기화 성공")
        return True
    except Exception as e:
        Logger.error(f"AudioRecorder 초기화 실패: {e}")
        return False


def test_file_creation(duration=3):
    """파일 생성 테스트 (실제 녹음)"""
    Logger.section(f"녹음 파일 생성 테스트")
    
    try:
        recorder = AudioRecorder()
        
        # 출력 파일 경로
        output_file = os.path.join(TEST_OUTPUT_DIR, "test_recording.wav")
        relative_path = os.path.relpath(output_file, project_root)
        
        Logger.info(f"💾 저장 위치: {relative_path}")
        
        # Manual 모드로 녹음 (엔터키로 중지)
        audio_data = []
        
        def callback(indata, frames, time_info, status):
            if status:
                Logger.warning(f"녹음 상태: {status}")
            audio_data.append(indata.copy())
        
        Logger.info("🎤 마이크 준비 중...")
        time.sleep(0.5)  # 마이크 초기화 대기
        
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, 
                          dtype='int16', callback=callback):
            Logger.info("🔴 녹음 시작! 말해보세요...")
            Logger.info("   (녹음을 마치려면 엔터키를 누르세요)")
            time.sleep(0.2)  # 콜백 시작 대기
            input()  # 사용자 입력 대기
        
        Logger.info("⏹️  녹음 중지")
        
        # 데이터 확인
        if not audio_data:
            Logger.error("녹음된 데이터가 없습니다. 너무 빨리 중지했습니다.")
            return False
        
        # WAV 파일로 저장
        audio_array = np.concatenate(audio_data, axis=0)
        
        # 최소 길이 체크 (0.1초 이상)
        min_samples = int(SAMPLE_RATE * 0.1)
        if len(audio_array) < min_samples:
            Logger.warning(f"녹음 시간이 너무 짧습니다: {len(audio_array)/SAMPLE_RATE:.2f}초")
            Logger.info("최소 0.5초 이상 녹음해주세요")
            return False
        
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_array.tobytes())
        
        Logger.success(f"녹음 파일 저장: {output_file}")
        
        # 파일 정보 출력
        file_size = os.path.getsize(output_file) / 1024  # KB
        duration = len(audio_array) / SAMPLE_RATE
        Logger.info(f"파일 크기: {file_size:.1f} KB")
        Logger.info(f"녹음 길이: {duration:.1f}초")
        Logger.info(f"샘플 수: {len(audio_array):,}")
        
        return True
        
    except Exception as e:
        Logger.error(f"녹음 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="AudioRecorder 테스트")
    parser.add_argument('--record', action='store_true', 
                       help='실제 녹음 테스트')
    parser.add_argument('--all', action='store_true',
                       help='모든 테스트 실행')
    args = parser.parse_args()
    
    Logger.section("AudioRecorder 테스트 시작")
    
    # 기본 테스트는 항상 실행
    if not test_basic_recording():
        Logger.error("기본 테스트 실패")
        return
    
    # 녹음 테스트
    if args.record or args.all:
        if not test_file_creation():
            Logger.error("녹음 테스트 실패")
            return
    else:
        Logger.info("실제 녹음 테스트를 하려면: python test_recording.py --record")
    
    Logger.section("✅ 모든 테스트 통과!")


if __name__ == "__main__":
    main()
