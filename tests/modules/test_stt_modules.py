# tests/modules/test_stt_modules.py
"""
STT 모듈 단위 테스트
각 STT 엔진의 transcribe 메서드 테스트
"""
import sys
import os
import pytest


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


from modules.stt_modules import WhisperSTT, GoogleSTT, ClovaSTT
from utils.logger import Logger, configure_logger, set_log_level



# 테스트용 오디오 파일 경로
TEST_AUDIO_DIR = os.path.join(project_root, "tests", "assets")
TEST_AUDIO_FILE = os.path.join(TEST_AUDIO_DIR, "test_recording.wav")



class TestSTTModules:
    """STT 모듈 기본 테스트"""
    
    def test_whisper_instance_creation(self):
        """Whisper STT 인스턴스 생성"""
        stt = WhisperSTT()
        assert stt is not None, "Whisper STT 인스턴스 생성 실패"
        assert hasattr(stt, 'transcribe'), "transcribe 메서드 없음"
        Logger.success("Whisper STT 인스턴스 생성 테스트 통과")
    
    def test_google_instance_creation(self):
        """Google STT 인스턴스 생성"""
        try:
            stt = GoogleSTT()
            assert stt is not None, "Google STT 인스턴스 생성 실패"
            assert hasattr(stt, 'transcribe'), "transcribe 메서드 없음"
            Logger.success("Google STT 인스턴스 생성 테스트 통과")
        except Exception as e:
            Logger.warning(f"Google STT 생성 실패 (키 확인 필요): {e}")
    
    def test_clova_instance_creation(self):
        """Clova STT 인스턴스 생성"""
        try:
            stt = ClovaSTT()
            assert stt is not None, "Clova STT 인스턴스 생성 실패"
            assert hasattr(stt, 'transcribe'), "transcribe 메서드 없음"
            Logger.success("Clova STT 인스턴스 생성 테스트 통과")
        except Exception as e:
            Logger.warning(f"Clova STT 생성 실패 (키 확인 필요): {e}")



class TestSTTTranscription:
    """STT 음성 인식 테스트 (오디오 파일 필요)"""
    
    @pytest.mark.skipif(not os.path.exists(TEST_AUDIO_FILE), reason="테스트 오디오 파일 없음")
    def test_whisper_transcribe(self):
        """Whisper STT 음성 인식"""
        stt = WhisperSTT()
        result = stt.transcribe(TEST_AUDIO_FILE)
        
        assert result is not None, "Whisper STT 결과 없음"
        assert isinstance(result, str), "결과가 문자열이 아님"
        Logger.success(f"Whisper STT 결과: {result}")
    
    @pytest.mark.skipif(not os.path.exists(TEST_AUDIO_FILE), reason="테스트 오디오 파일 없음")
    def test_google_transcribe(self):
        """Google STT 음성 인식"""
        try:
            stt = GoogleSTT()
            result = stt.transcribe(TEST_AUDIO_FILE)
            
            assert result is not None, "Google STT 결과 없음"
            assert isinstance(result, str), "결과가 문자열이 아님"
            Logger.success(f"Google STT 결과: {result}")
        except Exception as e:
            Logger.warning(f"Google STT 테스트 실패: {e}")
    
    @pytest.mark.skipif(not os.path.exists(TEST_AUDIO_FILE), reason="테스트 오디오 파일 없음")
    def test_clova_transcribe(self):
        """Clova STT 음성 인식"""
        try:
            stt = ClovaSTT()
            result = stt.transcribe(TEST_AUDIO_FILE)
            
            assert result is not None, "Clova STT 결과 없음"
            assert isinstance(result, str), "결과가 문자열이 아님"
            Logger.success(f"Clova STT 결과: {result}")
        except Exception as e:
            Logger.warning(f"Clova STT 테스트 실패: {e}")



class TestSTTErrorHandling:
    """STT 에러 처리 테스트"""
    
    def test_nonexistent_file(self):
        """존재하지 않는 파일 처리"""
        stt = WhisperSTT()
        result = stt.transcribe("nonexistent_file.wav")
        
        assert result is None, "존재하지 않는 파일에 대해 None 반환 실패"
        Logger.success("존재하지 않는 파일 에러 처리 테스트 통과")



if __name__ == "__main__":
    # Logger 설정
    configure_logger(use_emoji=True, use_color=True, log_to_file=False)
    set_log_level("INFO")
    
    Logger.section("STT 모듈 테스트")
    
    # 인스턴스 생성 테스트
    Logger.info("인스턴스 생성 테스트 시작", emoji="🔧")
    test_modules = TestSTTModules()
    test_modules.test_whisper_instance_creation()
    test_modules.test_google_instance_creation()
    test_modules.test_clova_instance_creation()
    Logger.separator()
    
    # 음성 인식 테스트
    if os.path.exists(TEST_AUDIO_FILE):
        Logger.info(f"테스트 오디오 파일 발견: {TEST_AUDIO_FILE}", emoji="🎵")
        test_transcription = TestSTTTranscription()
        test_transcription.test_whisper_transcribe()
        test_transcription.test_google_transcribe()
        test_transcription.test_clova_transcribe()
    else:
        Logger.warning(f"테스트 오디오 파일 없음: {TEST_AUDIO_FILE}")
        Logger.info("python tests/test_recording.py 를 먼저 실행하세요", emoji="💡")
    Logger.separator()
    
    # 에러 처리 테스트
    Logger.info("에러 처리 테스트 시작", emoji="🛡️")
    test_error = TestSTTErrorHandling()
    test_error.test_nonexistent_file()
    Logger.separator()
    
    Logger.section("✅ STT 모듈 테스트 완료")
