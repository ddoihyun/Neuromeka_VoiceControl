# tests/core/test_factory.py
"""
Factory 패턴 단위 테스트
지연 초기화 및 싱글톤 동작 검증

사용법:
    python tests/core/test_factory.py
"""
import sys
import os

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

import pytest
from core.factory import get_stt_fn, get_llm_fn, get_tts_fn
from utils.logger import Logger


class TestFactorySingleton:
    """싱글톤 패턴 테스트"""
    
    def test_stt_singleton(self):
        """STT 싱글톤 확인"""
        stt1 = get_stt_fn("whisper")
        stt2 = get_stt_fn("whisper")
        
        assert stt1 is stt2, "STT 싱글톤 실패: 다른 인스턴스 생성됨"
        Logger.success("STT 싱글톤 테스트 통과")
    
    def test_llm_singleton(self):
        """LLM 싱글톤 확인"""
        llm1 = get_llm_fn("gemini")
        llm2 = get_llm_fn("gemini")
        
        assert llm1 is llm2, "LLM 싱글톤 실패: 다른 인스턴스 생성됨"
        Logger.success("LLM 싱글톤 테스트 통과")
    
    def test_tts_singleton(self):
        """TTS 싱글톤 확인"""
        tts1 = get_tts_fn("google")
        tts2 = get_tts_fn("google")
        
        assert tts1 is tts2, "TTS 싱글톤 실패: 다른 인스턴스 생성됨"
        Logger.success("TTS 싱글톤 테스트 통과")


class TestFactoryEngineSelection:
    """엔진 선택 테스트"""
    
    def test_stt_engine_selection(self):
        """다양한 STT 엔진 선택"""
        whisper = get_stt_fn("whisper")
        google = get_stt_fn("google")
        clova = get_stt_fn("clova")
        
        assert whisper is not google, "STT 엔진이 구분되지 않음"
        assert google is not clova, "STT 엔진이 구분되지 않음"
        Logger.success("STT 엔진 선택 테스트 통과")
    
    def test_llm_engine_selection(self):
        """다양한 LLM 엔진 선택"""
        gemini = get_llm_fn("gemini")
        gpt = get_llm_fn("gpt")
        
        assert gemini is not gpt, "LLM 엔진이 구분되지 않음"
        Logger.success("LLM 엔진 선택 테스트 통과")
    
    def test_tts_engine_selection(self):
        """다양한 TTS 엔진 선택"""
        google = get_tts_fn("google")
        openai = get_tts_fn("openai")
        clova = get_tts_fn("clova")
        
        assert google is not openai, "TTS 엔진이 구분되지 않음"
        assert openai is not clova, "TTS 엔진이 구분되지 않음"
        Logger.success("TTS 엔진 선택 테스트 통과")


class TestFactoryLazyInit:
    """지연 초기화 테스트"""
    
    def test_lazy_initialization(self):
        """지연 초기화 확인: 인스턴스가 호출 전까지 생성되지 않음"""
        stt_fn = get_stt_fn("whisper")
        
        assert stt_fn._instance is None, "지연 초기화 실패: 즉시 생성됨"
        Logger.success("지연 초기화 테스트 통과 (인스턴스 미생성 확인)")


class TestFactoryDefaultEngine:
    """기본 엔진 폴백 테스트"""
    
    def test_unknown_stt_fallback(self):
        """알 수 없는 STT 엔진 → Whisper 기본값"""
        stt_fn = get_stt_fn("unknown")
        assert stt_fn is not None, "기본 STT 엔진 생성 실패"
        Logger.success("STT 기본 엔진 폴백 테스트 통과")
    
    def test_unknown_llm_fallback(self):
        """알 수 없는 LLM 엔진 → Gemini 기본값"""
        llm_fn = get_llm_fn("unknown")
        assert llm_fn is not None, "기본 LLM 엔진 생성 실패"
        Logger.success("LLM 기본 엔진 폴백 테스트 통과")
    
    def test_unknown_tts_fallback(self):
        """알 수 없는 TTS 엔진 → Google 기본값"""
        tts_fn = get_tts_fn("unknown")
        assert tts_fn is not None, "기본 TTS 엔진 생성 실패"
        Logger.success("TTS 기본 엔진 폴백 테스트 통과")


if __name__ == "__main__":
    Logger.section("Factory 패턴 테스트")
    
    # 싱글톤 테스트
    Logger.info("싱글톤 패턴 검증 중...")
    test_singleton = TestFactorySingleton()
    test_singleton.test_stt_singleton()
    test_singleton.test_llm_singleton()
    test_singleton.test_tts_singleton()
    
    Logger.separator()
    
    # 엔진 선택 테스트
    Logger.info("엔진 선택 기능 검증 중...")
    test_engine = TestFactoryEngineSelection()
    test_engine.test_stt_engine_selection()
    test_engine.test_llm_engine_selection()
    test_engine.test_tts_engine_selection()
    
    Logger.separator()
    
    # 지연 초기화 테스트
    Logger.info("지연 초기화 검증 중...")
    test_lazy = TestFactoryLazyInit()
    test_lazy.test_lazy_initialization()
    
    Logger.separator()
    
    # 기본 엔진 테스트
    Logger.info("기본 엔진 폴백 검증 중...")
    test_default = TestFactoryDefaultEngine()
    test_default.test_unknown_stt_fallback()
    test_default.test_unknown_llm_fallback()
    test_default.test_unknown_tts_fallback()
    
    Logger.section("✅ 모든 테스트 통과!")
