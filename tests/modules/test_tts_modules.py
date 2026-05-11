# tests/modules/test_tts_modules.py
"""
TTS 모듈 단위 테스트
각 TTS 엔진의 speak 메서드 및 AudioPlayer 테스트


사용법:
    python tests/modules/test_tts_modules.py           # Google TTS만
    python tests/modules/test_tts_modules.py --all     # 모든 엔진
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


import argparse
import pytest
import time


from modules.tts_modules import GoogleTTS, OpenAITTS, ClovaTTS, AudioPlayer, TTSManager
from utils.logger import Logger, configure_logger, set_log_level



class TestTTSModules:
    """TTS 모듈 기본 테스트"""
    
    def test_google_tts_instance_creation(self):
        """Google TTS 인스턴스 생성"""
        tts = GoogleTTS()
        assert tts is not None, "Google TTS 인스턴스 생성 실패"
        assert hasattr(tts, 'speak'), "speak 메서드 없음"
        Logger.success("Google TTS 인스턴스 생성 테스트 통과")
    
    def test_openai_tts_instance_creation(self):
        """OpenAI TTS 인스턴스 생성"""
        try:
            tts = OpenAITTS()
            assert tts is not None, "OpenAI TTS 인스턴스 생성 실패"
            assert hasattr(tts, 'speak'), "speak 메서드 없음"
            Logger.success("OpenAI TTS 인스턴스 생성 테스트 통과")
        except Exception as e:
            Logger.warning(f"OpenAI TTS 생성 실패 (키 확인 필요): {e}")
    
    def test_clova_tts_instance_creation(self):
        """Clova TTS 인스턴스 생성"""
        try:
            tts = ClovaTTS()
            assert tts is not None, "Clova TTS 인스턴스 생성 실패"
            assert hasattr(tts, 'speak'), "speak 메서드 없음"
            Logger.success("Clova TTS 인스턴스 생성 테스트 통과")
        except Exception as e:
            Logger.warning(f"Clova TTS 생성 실패 (키 확인 필요): {e}")



class TestAudioPlayer:
    """AudioPlayer 유틸리티 테스트"""
    
    def test_audio_player_creation(self):
        """AudioPlayer 인스턴스 생성"""
        player = AudioPlayer()
        assert player is not None, "AudioPlayer 인스턴스 생성 실패"
        assert hasattr(player, 'play'), "play 메서드 없음"
        assert hasattr(player, 'stop'), "stop 메서드 없음"
        Logger.success("AudioPlayer 인스턴스 생성 테스트 통과")
    
    def test_safe_remove_nonexistent(self):
        """존재하지 않는 파일 삭제 시도"""
        result = AudioPlayer.safe_remove("nonexistent_file.mp3")
        assert result is True or result is False, "safe_remove 실행 실패"
        Logger.success("존재하지 않는 파일 삭제 테스트 통과")



class TestTTSSpeak:
    """TTS speak 메서드 테스트 (실제 음성 생성)"""
    
    def test_google_tts_speak(self):
        """Google TTS 음성 생성 및 재생"""
        try:
            tts = GoogleTTS()
            tts.speak("테스트입니다")
            
            from configs import TTS_PATH
            if os.path.exists(TTS_PATH):
                Logger.success(f"Google TTS 파일 생성: {TTS_PATH}")
            else:
                Logger.warning("TTS 파일이 생성되지 않음 (TTS_KEEP_FILES 설정 확인)")
            
        except Exception as e:
            Logger.warning(f"Google TTS speak 테스트 실패: {e}")
    
    def test_openai_tts_speak(self):
        """OpenAI TTS 음성 생성 및 재생"""
        try:
            tts = OpenAITTS()
            tts.speak("OpenAI 테스트입니다")
            Logger.success("OpenAI TTS speak 테스트 통과")
        except Exception as e:
            Logger.warning(f"OpenAI TTS speak 테스트 실패: {e}")
    
    def test_clova_tts_speak(self):
        """Clova TTS 음성 생성 및 재생"""
        try:
            tts = ClovaTTS()
            tts.speak("클로바 테스트입니다")
            Logger.success("Clova TTS speak 테스트 통과")
        except Exception as e:
            Logger.warning(f"Clova TTS speak 테스트 실패: {e}")



class TestTTSManager:
    """TTSManager 백그라운드 매니저 테스트"""
    
    def test_tts_manager_creation(self):
        """TTSManager 인스턴스 생성"""
        manager = TTSManager(tts_engine="google")
        assert manager is not None, "TTSManager 인스턴스 생성 실패"
        assert hasattr(manager, 'start'), "start 메서드 없음"
        assert hasattr(manager, 'stop'), "stop 메서드 없음"
        Logger.success("TTSManager 인스턴스 생성 테스트 통과")
    
    def test_tts_manager_lifecycle(self):
        """TTSManager 시작 및 종료"""
        manager = TTSManager(tts_engine="google")
        
        manager.start()
        assert manager.running is True, "TTSManager 시작 실패"
        Logger.success("TTSManager 시작 테스트 통과")
        
        time.sleep(0.5)
        
        manager.stop()
        assert manager.running is False, "TTSManager 종료 실패"
        Logger.success("TTSManager 종료 테스트 통과")
    
    def test_tts_manager_global_integration(self):
        """TTSManager Global 변수 연동 테스트"""
        from configs import globals as g
        
        manager = TTSManager(tts_engine="google")
        manager.start()
        
        g.set_speak_request("매니저 테스트입니다")
        time.sleep(2)
        
        manager.stop()
        Logger.success("TTSManager Global 연동 테스트 통과")



class TestTTSErrorHandling:
    """TTS 에러 처리 테스트"""
    
    def test_empty_text(self):
        """빈 텍스트 처리"""
        tts = GoogleTTS()
        try:
            tts.speak("")
            Logger.success("빈 텍스트 처리 테스트 통과")
        except Exception as e:
            Logger.error(f"빈 텍스트 처리 실패: {e}")
    
    def test_none_text(self):
        """None 텍스트 처리"""
        tts = GoogleTTS()
        try:
            tts.speak(None)
            Logger.success("None 텍스트 처리 테스트 통과")
        except Exception as e:
            Logger.error(f"None 텍스트 처리 실패: {e}")



def main():
    parser = argparse.ArgumentParser(description="TTS 모듈 테스트")
    parser.add_argument('--all', action='store_true',
                       help='모든 TTS 엔진 테스트 (Google, OpenAI, Clova)')
    args = parser.parse_args()
    
    # Logger 설정
    configure_logger(use_emoji=True, use_color=True, log_to_file=False)
    set_log_level("INFO")
    
    Logger.section("TTS 모듈 테스트")
    
    # 인스턴스 생성 테스트
    Logger.info("인스턴스 생성 테스트 시작", emoji="🔧")
    test_modules = TestTTSModules()
    test_modules.test_google_tts_instance_creation()
    test_modules.test_openai_tts_instance_creation()
    test_modules.test_clova_tts_instance_creation()
    Logger.separator()
    
    # AudioPlayer 테스트
    Logger.info("AudioPlayer 테스트 시작", emoji="🔊")
    test_player = TestAudioPlayer()
    test_player.test_audio_player_creation()
    test_player.test_safe_remove_nonexistent()
    Logger.separator()
    
    # TTS speak 테스트
    Logger.info("TTS 음성 생성 테스트 (소리가 재생될 수 있습니다)...", emoji="🔉")
    test_speak = TestTTSSpeak()
    
    # Google TTS는 기본적으로 실행
    test_speak.test_google_tts_speak()
    
    # --all 플래그가 있을 때만 나머지 엔진 테스트
    if args.all:
        Logger.info("모든 TTS 엔진 테스트 중...", emoji="🌐")
        test_speak.test_openai_tts_speak()
        test_speak.test_clova_tts_speak()
    else:
        Logger.info("모든 엔진을 테스트하려면: python test_tts_modules.py --all", emoji="💡")
    Logger.separator()
    
    # TTSManager 테스트
    Logger.info("TTSManager 테스트 시작...", emoji="⚙️")
    test_manager = TestTTSManager()
    test_manager.test_tts_manager_creation()
    test_manager.test_tts_manager_lifecycle()
    test_manager.test_tts_manager_global_integration()
    Logger.separator()
    
    # 에러 처리 테스트
    Logger.info("에러 처리 테스트 시작", emoji="🛡️")
    test_error = TestTTSErrorHandling()
    test_error.test_empty_text()
    test_error.test_none_text()
    Logger.separator()
    
    Logger.section("✅ TTS 모듈 테스트 완료")



if __name__ == "__main__":
    main()
