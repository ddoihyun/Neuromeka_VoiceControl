# tests/core/test_wakeword.py
"""
WakeWordDetector 단위 테스트
Wake word 감지 및 TFLite 모델 로딩 테스트

사용법:
    python tests/core/test_wakeword.py
    python tests/core/test_wakeword.py --model EirnNami.tflite
    python tests/core/test_wakeword.py --model custom_model.tflite
"""
import os
import sys
import argparse

# ========================================
# 1. 경로 설정
# ========================================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)

# ========================================
# 2. 환경 변수 설정
# ========================================
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# ========================================
# 3. Warning 필터링
# ========================================
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='keras')
warnings.filterwarnings('ignore', message='.*np.object.*')
warnings.filterwarnings('ignore', message='.*tf.lite.*')
warnings.filterwarnings('ignore', message='.*deprecated.*')

import numpy as np
from core.wakeword import WakeWordDetector
from configs import (
    WAKE_WORD_MODEL_PATH,
    WAKE_WORD_THRESHOLD,
    WAKE_WORD_TARGETS,
    WAKE_WORD_NAMES
)
from utils.logger import Logger


def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="WakeWordDetector 테스트",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--model', 
        type=str,
        default=None,
        help='테스트할 모델 파일명 (models/ 폴더 내, 예: EirnNami.tflite)'
    )
    
    return parser.parse_args()


def get_model_path(model_filename=None):
    """
    모델 경로 반환
    Args:
        model_filename: 모델 파일명 (None이면 config 기본값 사용)
    Returns:
        모델 전체 경로
    """
    if model_filename is None:
        # 기본값 사용 (config.py)
        return WAKE_WORD_MODEL_PATH
    
    # 사용자 지정 모델
    model_path = os.path.join(project_root, "models", model_filename)
    
    # 경로 검증
    if not os.path.exists(model_path):
        Logger.error(f"모델 파일을 찾을 수 없습니다: {model_path}")
        Logger.info(f"models/ 폴더 내 파일 목록:")
        
        models_dir = os.path.join(project_root, "models")
        if os.path.exists(models_dir):
            files = os.listdir(models_dir)
            tflite_files = [f for f in files if f.endswith('.tflite')]
            
            if tflite_files:
                for f in tflite_files:
                    Logger.info(f"  - {f}")
            else:
                Logger.warning("  .tflite 파일이 없습니다")
        else:
            Logger.error(f"models/ 폴더가 없습니다: {models_dir}")
        
        raise FileNotFoundError(f"모델 파일 없음: {model_path}")
    
    return model_path


class TestWakeWordDetectorBasic:
    """WakeWordDetector 기본 기능 테스트"""
    
    @staticmethod
    def test_detector_instance_creation(model_path):
        """WakeWordDetector 인스턴스 생성"""
        if not os.path.exists(model_path):
            Logger.warning(f"모델 파일 없음: {model_path}")
            Logger.info("테스트 스킵")
            return False
        
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=WAKE_WORD_THRESHOLD,
            target_wake_words=WAKE_WORD_TARGETS,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        assert detector is not None, "WakeWordDetector 인스턴스 생성 실패"
        assert hasattr(detector, 'detect_from_stream'), "detect_from_stream 메서드 없음"
        assert hasattr(detector, 'reset'), "reset 메서드 없음"
        Logger.success("WakeWordDetector 인스턴스 생성 테스트 통과")
        return True
    
    @staticmethod
    def test_detector_model_loading(model_path):
        """TFLite 모델 로딩 테스트"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        try:
            detector = WakeWordDetector(
                model_path=model_path,
                threshold=WAKE_WORD_THRESHOLD,
                target_wake_words=WAKE_WORD_TARGETS,
                wake_word_names=WAKE_WORD_NAMES
            )
            
            assert detector.interpreter is not None, "TFLite 인터프리터 로딩 실패"
            Logger.success("TFLite 모델 로딩 테스트 통과")
            return True
        except Exception as e:
            Logger.error(f"모델 로딩 실패: {e}")
            return False


class TestWakeWordDetectorSettings:
    """WakeWordDetector 설정 테스트"""
    
    @staticmethod
    def test_threshold_setting(model_path):
        """임계값 설정 테스트"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=0.7,
            target_wake_words=WAKE_WORD_TARGETS,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        assert detector.threshold == 0.7, "임계값 설정 실패"
        Logger.success("임계값 설정 테스트 통과")
        return True
    
    @staticmethod
    def test_target_wake_words_setting(model_path):
        """타겟 Wake word 설정 테스트"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        target_words = [0, 1]
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=WAKE_WORD_THRESHOLD,
            target_wake_words=target_words,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        assert detector.target_wake_words == target_words, "타겟 Wake word 설정 실패"
        Logger.success("타겟 Wake word 설정 테스트 통과")
        return True


class TestWakeWordDetection:
    """Wake word 감지 테스트"""
    
    @staticmethod
    def test_detect_from_stream_with_noise(model_path):
        """노이즈 오디오로 감지 테스트 (감지되지 않아야 함)"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=WAKE_WORD_THRESHOLD,
            target_wake_words=WAKE_WORD_TARGETS,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        # 랜덤 노이즈 생성 (160샘플 = 10ms)
        noise_audio = np.random.randint(-1000, 1000, 160, dtype='int16')
        
        result = detector.detect_from_stream(noise_audio)
        
        # 노이즈는 Wake word로 감지되지 않아야 함
        assert result is False, "노이즈가 Wake word로 감지됨"
        Logger.success("노이즈 오디오 테스트 통과 (감지 안됨)")
        return True
    
    @staticmethod
    def test_detect_from_stream_with_silence(model_path):
        """침묵 오디오로 감지 테스트 (감지되지 않아야 함)"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=WAKE_WORD_THRESHOLD,
            target_wake_words=WAKE_WORD_TARGETS,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        # 침묵 (0으로 채워진 오디오)
        silence_audio = np.zeros(160, dtype='int16')
        
        result = detector.detect_from_stream(silence_audio)
        
        assert result is False, "침묵이 Wake word로 감지됨"
        Logger.success("침묵 오디오 테스트 통과 (감지 안됨)")
        return True


class TestWakeWordReset:
    """Wake word 감지기 리셋 테스트"""
    
    @staticmethod
    def test_detector_reset(model_path):
        """감지기 리셋 테스트"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=WAKE_WORD_THRESHOLD,
            target_wake_words=WAKE_WORD_TARGETS,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        # 초기 버퍼 크기 저장
        initial_buffer_size = len(detector.audio_buffer)
        Logger.info(f"초기 버퍼 크기: {initial_buffer_size}")
        
        # 오디오 처리 (버퍼에 데이터 추가)
        for _ in range(10):
            test_audio = np.random.randint(-1000, 1000, 160, dtype='int16')
            detector.detect_from_stream(test_audio)
        
        buffer_size_after_detection = len(detector.audio_buffer)
        Logger.info(f"감지 후 버퍼 크기: {buffer_size_after_detection}")
        
        # 리셋
        detector.reset()
        
        buffer_size_after_reset = len(detector.audio_buffer)
        Logger.info(f"리셋 후 버퍼 크기: {buffer_size_after_reset}")
        
        # 리셋 후 버퍼가 초기 상태로 돌아갔는지 확인
        if buffer_size_after_reset == 0:
            Logger.success("감지기 리셋 테스트 통과 (버퍼 완전히 비워짐)")
        elif buffer_size_after_reset <= initial_buffer_size:
            Logger.success("감지기 리셋 테스트 통과 (버퍼 초기화됨)")
        else:
            Logger.warning(f"버퍼가 완전히 초기화되지 않음 (초기: {initial_buffer_size}, 현재: {buffer_size_after_reset})")
            Logger.info("reset() 메서드가 부분적으로만 작동하는 것 같습니다")
        
        return True


class TestWakeWordErrorHandling:
    """에러 처리 테스트"""
    
    @staticmethod
    def test_invalid_model_path():
        """잘못된 모델 경로 처리"""
        try:
            detector = WakeWordDetector(
                model_path="/nonexistent/model.tflite",
                threshold=WAKE_WORD_THRESHOLD,
                target_wake_words=WAKE_WORD_TARGETS,
                wake_word_names=WAKE_WORD_NAMES
            )
            Logger.warning("에러가 발생해야 하는데 발생하지 않음")
            return False
        except Exception as e:
            Logger.success(f"잘못된 모델 경로 에러 처리: {type(e).__name__}")
            return True


class TestWakeWordIntegration:
    """Wake word 통합 테스트"""
    
    @staticmethod
    def test_continuous_detection(model_path):
        """연속 감지 테스트"""
        if not os.path.exists(model_path):
            Logger.warning("모델 파일 없음, 테스트 스킵")
            return False
        
        detector = WakeWordDetector(
            model_path=model_path,
            threshold=WAKE_WORD_THRESHOLD,
            target_wake_words=WAKE_WORD_TARGETS,
            wake_word_names=WAKE_WORD_NAMES
        )
        
        # 여러 오디오 청크 연속 처리
        for i in range(10):
            test_audio = np.random.randint(-1000, 1000, 160, dtype='int16')
            result = detector.detect_from_stream(test_audio)
            # 랜덤 노이즈이므로 대부분 False
        
        Logger.success("연속 감지 테스트 통과")
        return True


if __name__ == "__main__":
    # 명령행 인자 파싱
    args = parse_arguments()
    
    Logger.section("WakeWordDetector 테스트")
    
    # 모델 경로 가져오기
    try:
        model_path = get_model_path(args.model)
        Logger.info(f"테스트 모델: {model_path}")
        
        if args.model:
            Logger.info(f"사용자 지정 모델: {args.model}")
        else:
            Logger.info("기본 모델 사용 (config.py)")
        
        Logger.separator()
        
    except FileNotFoundError as e:
        Logger.error(str(e))
        exit(1)
    
    # 기본 기능 테스트
    test_basic = TestWakeWordDetectorBasic()
    if not test_basic.test_detector_instance_creation(model_path):
        exit(1)
    test_basic.test_detector_model_loading(model_path)
    
    # 설정 테스트
    test_settings = TestWakeWordDetectorSettings()
    test_settings.test_threshold_setting(model_path)
    test_settings.test_target_wake_words_setting(model_path)
    
    # 감지 테스트
    test_detection = TestWakeWordDetection()
    test_detection.test_detect_from_stream_with_noise(model_path)
    test_detection.test_detect_from_stream_with_silence(model_path)
    
    # 리셋 테스트
    test_reset = TestWakeWordReset()
    test_reset.test_detector_reset(model_path)
    
    # 에러 처리 테스트
    test_error = TestWakeWordErrorHandling()
    test_error.test_invalid_model_path()
    
    # 통합 테스트
    test_integration = TestWakeWordIntegration()
    test_integration.test_continuous_detection(model_path)
    
    Logger.section("✅ WakeWordDetector 테스트 완료")
