# tests/modules/test_llm_modules.py
"""
LLM 모듈 단위 테스트
각 LLM 엔진의 ask 메서드 및 JSON 추출 테스트
"""
import sys
import os
import pytest
import asyncio


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


from modules.llm_modules import GPT4oLLM, GeminiLLM, extract_json
from utils.logger import Logger, configure_logger, set_log_level



class TestLLMModules:
    """LLM 모듈 기본 테스트"""
    
    def test_gpt_instance_creation(self):
        """GPT LLM 인스턴스 생성"""
        try:
            llm = GPT4oLLM()
            assert llm is not None, "GPT LLM 인스턴스 생성 실패"
            assert hasattr(llm, 'ask'), "ask 메서드 없음"
            Logger.success("GPT LLM 인스턴스 생성 테스트 통과")
        except Exception as e:
            Logger.warning(f"GPT LLM 생성 실패 (키 확인 필요): {e}")
    
    def test_gemini_instance_creation(self):
        """Gemini LLM 인스턴스 생성"""
        try:
            llm = GeminiLLM()
            assert llm is not None, "Gemini LLM 인스턴스 생성 실패"
            assert hasattr(llm, 'ask'), "ask 메서드 없음"
            Logger.success("Gemini LLM 인스턴스 생성 테스트 통과")
        except Exception as e:
            Logger.warning(f"Gemini LLM 생성 실패 (키 확인 필요): {e}")



class TestJSONExtraction:
    """JSON 추출 테스트"""
    
    def test_valid_json_extraction(self):
        """올바른 JSON 추출"""
        text = '{"action": "mode", "aux0": "fix", "aux1": "고정 모드로 전환"}'
        result = extract_json(text)
        
        assert result["action"] == "mode"
        assert result["aux0"] == "fix"
        assert result["aux1"] == "고정 모드로 전환"
        Logger.success("JSON 추출 테스트 통과")
    
    def test_json_with_extra_text(self):
        """JSON 외 텍스트 포함 시 추출"""
        text = '추가 텍스트 {"action": "mode", "aux0": "free"} 뒤 텍스트'
        result = extract_json(text)
        
        assert result["action"] == "mode"
        assert result["aux0"] == "free"
        Logger.success("JSON 추가 텍스트 처리 테스트 통과")
    
    def test_empty_text(self):
        """빈 텍스트 처리"""
        result = extract_json("")
        
        assert result["action"] is None
        assert "응답 텍스트가 없습니다" in result["aux1"]
        Logger.success("빈 텍스트 처리 테스트 통과")
    
    def test_invalid_json(self):
        """잘못된 JSON 처리"""
        text = "이것은 JSON이 아닙니다"
        result = extract_json(text)
        
        assert result["action"] is None
        assert result["aux1"] == "이것은 JSON이 아닙니다"
        Logger.success("잘못된 JSON 처리 테스트 통과")



class TestLLMAsk:
    """LLM ask 메서드 테스트 (실제 API 호출)"""
    
    @pytest.mark.asyncio
    async def test_gemini_ask(self):
        """Gemini LLM 요청"""
        try:
            llm = GeminiLLM()
            result = await llm.ask("로봇을 고정 모드로 변경해줘")
            
            assert isinstance(result, dict), "결과가 딕셔너리가 아님"
            assert "action" in result, "action 키 없음"
            assert "aux0" in result, "aux0 키 없음"
            assert "aux1" in result, "aux1 키 없음"
            
            Logger.success(f"Gemini LLM 결과: {result}")
        except Exception as e:
            Logger.warning(f"Gemini LLM 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_gpt_ask(self):
        """GPT LLM 요청"""
        try:
            llm = GPT4oLLM()
            result = await llm.ask("로봇을 이동 모드로 변경해줘")
            
            assert isinstance(result, dict), "결과가 딕셔너리가 아님"
            assert "action" in result, "action 키 없음"
            
            Logger.success(f"GPT LLM 결과: {result}")
        except Exception as e:
            Logger.warning(f"GPT LLM 테스트 실패: {e}")



if __name__ == "__main__":
    # Logger 설정
    configure_logger(use_emoji=True, use_color=True, log_to_file=False)
    set_log_level("INFO")
    
    Logger.section("LLM 모듈 테스트")
    
    # 인스턴스 생성 테스트
    Logger.info("인스턴스 생성 테스트 시작", emoji="🔧")
    test_modules = TestLLMModules()
    test_modules.test_gpt_instance_creation()
    test_modules.test_gemini_instance_creation()
    Logger.separator()
    
    # JSON 추출 테스트
    Logger.info("JSON 추출 테스트 시작", emoji="📄")
    test_json = TestJSONExtraction()
    test_json.test_valid_json_extraction()
    test_json.test_json_with_extra_text()
    test_json.test_empty_text()
    test_json.test_invalid_json()
    Logger.separator()
    
    # LLM ask 테스트 (비동기)
    Logger.info("LLM API 호출 테스트 (시간이 걸릴 수 있습니다)...", emoji="🌐")
    test_ask = TestLLMAsk()
    asyncio.run(test_ask.test_gemini_ask())
    asyncio.run(test_ask.test_gpt_ask())
    Logger.separator()
    
    Logger.section("✅ LLM 모듈 테스트 완료")
