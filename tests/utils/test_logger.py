# tests/utils/test_logger.py
"""
Logger 유틸리티 단위 테스트
로그 레벨, 포맷, 색상 등 테스트
"""
import sys
import os
import io
from contextlib import redirect_stdout

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from utils.logger import Logger, LogLevel, set_log_level, configure_logger


class TestLoggerBasic:
    """Logger 기본 기능 테스트"""
    
    def test_logger_debug(self):
        """디버그 로그 출력"""
        set_log_level("DEBUG")
        
        # 출력 캡처
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.debug("디버그 메시지")
        
        output = f.getvalue()
        assert "DEBUG" in output, "DEBUG 로그 출력 실패"
        assert "디버그 메시지" in output, "로그 내용 출력 실패"
        print("✓ Logger.debug() 테스트 통과")
    
    def test_logger_info(self):
        """정보 로그 출력"""
        set_log_level("INFO")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.info("정보 메시지")
        
        output = f.getvalue()
        assert "INFO" in output, "INFO 로그 출력 실패"
        assert "정보 메시지" in output, "로그 내용 출력 실패"
        print("✓ Logger.info() 테스트 통과")
    
    def test_logger_warning(self):
        """경고 로그 출력"""
        set_log_level("WARNING")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.warning("경고 메시지")
        
        output = f.getvalue()
        assert "WARNING" in output, "WARNING 로그 출력 실패"
        assert "경고 메시지" in output, "로그 내용 출력 실패"
        print("✓ Logger.warning() 테스트 통과")
    
    def test_logger_error(self):
        """에러 로그 출력"""
        set_log_level("ERROR")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.error("에러 메시지")
        
        output = f.getvalue()
        assert "ERROR" in output, "ERROR 로그 출력 실패"
        assert "에러 메시지" in output, "로그 내용 출력 실패"
        print("✓ Logger.error() 테스트 통과")
    
    def test_logger_success(self):
        """성공 로그 출력"""
        set_log_level("INFO")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.success("성공 메시지")
        
        output = f.getvalue()
        assert "성공 메시지" in output, "로그 내용 출력 실패"
        print("✓ Logger.success() 테스트 통과")


class TestLoggerLevel:
    """Logger 레벨 필터링 테스트"""
    
    def test_log_level_filtering(self):
        """로그 레벨 필터링"""
        set_log_level("WARNING")
        
        # DEBUG와 INFO는 출력되지 않아야 함
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.debug("디버그")
            Logger.info("정보")
            Logger.warning("경고")
            Logger.error("에러")
        
        output = f.getvalue()
        assert "디버그" not in output, "DEBUG 로그가 출력됨 (필터링 실패)"
        assert "정보" not in output, "INFO 로그가 출력됨 (필터링 실패)"
        assert "경고" in output, "WARNING 로그 출력 실패"
        assert "에러" in output, "ERROR 로그 출력 실패"
        print("✓ 로그 레벨 필터링 테스트 통과")


class TestLoggerFormatting:
    """Logger 포맷팅 테스트"""
    
    def test_emoji_display(self):
        """이모지 표시"""
        configure_logger(use_emoji=True)
        set_log_level("INFO")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.info("메시지", emoji="🔍")
        
        output = f.getvalue()
        assert "🔍" in output, "이모지 출력 실패"
        print("✓ 이모지 표시 테스트 통과")
    
    def test_emoji_disabled(self):
        """이모지 비활성화"""
        configure_logger(use_emoji=False)
        set_log_level("INFO")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.info("메시지", emoji="🔍")
        
        output = f.getvalue()
        assert "🔍" not in output, "이모지가 출력됨 (비활성화 실패)"
        print("✓ 이모지 비활성화 테스트 통과")
    
    def test_separator(self):
        """구분선 출력"""
        set_log_level("INFO")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.separator(char="─", length=20)
        
        output = f.getvalue()
        assert "─" * 20 in output, "구분선 출력 실패"
        print("✓ 구분선 출력 테스트 통과")
    
    def test_section(self):
        """섹션 헤더 출력"""
        set_log_level("INFO")
        
        f = io.StringIO()
        with redirect_stdout(f):
            Logger.section("테스트 섹션")
        
        output = f.getvalue()
        assert "테스트 섹션" in output, "섹션 헤더 출력 실패"
        assert "─" in output, "섹션 구분선 출력 실패"
        print("✓ 섹션 헤더 출력 테스트 통과")


class TestLoggerConfiguration:
    """Logger 설정 테스트"""
    
    def test_set_log_level(self):
        """로그 레벨 설정"""
        set_log_level("ERROR")
        assert Logger.CURRENT_LEVEL == LogLevel.ERROR, "로그 레벨 설정 실패"
        
        set_log_level("DEBUG")
        assert Logger.CURRENT_LEVEL == LogLevel.DEBUG, "로그 레벨 설정 실패"
        
        print("✓ 로그 레벨 설정 테스트 통과")
    
    def test_configure_logger(self):
        """Logger 설정 변경"""
        configure_logger(use_emoji=True, use_color=True)
        assert Logger.USE_EMOJI is True, "이모지 설정 실패"
        assert Logger.USE_COLOR is True, "색상 설정 실패"
        
        configure_logger(use_emoji=False, use_color=False)
        assert Logger.USE_EMOJI is False, "이모지 비활성화 실패"
        assert Logger.USE_COLOR is False, "색상 비활성화 실패"
        
        print("✓ Logger 설정 변경 테스트 통과")


if __name__ == "__main__":
    print("="*60)
    print("  Logger 유틸리티 테스트")
    print("="*60)
    
    # 기본 기능 테스트
    test_basic = TestLoggerBasic()
    test_basic.test_logger_debug()
    test_basic.test_logger_info()
    test_basic.test_logger_warning()
    test_basic.test_logger_error()
    test_basic.test_logger_success()
    
    # 레벨 필터링 테스트
    test_level = TestLoggerLevel()
    test_level.test_log_level_filtering()
    
    # 포맷팅 테스트
    test_format = TestLoggerFormatting()
    test_format.test_emoji_display()
    test_format.test_emoji_disabled()
    test_format.test_separator()
    test_format.test_section()
    
    # 설정 테스트
    test_config = TestLoggerConfiguration()
    test_config.test_set_log_level()
    test_config.test_configure_logger()
    
    print("="*60)
    print("  ✅ Logger 유틸리티 테스트 완료")
    print("="*60)
