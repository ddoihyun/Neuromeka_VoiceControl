# tests/utils/test_robot_commands.py
"""
Robot Commands 유틸리티 단위 테스트
로봇 제어 함수 및 Global 변수 연동 테스트
"""
import sys
import os


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


from utils.robot_commands import set_mode, get_current_mode, move_robot, stop_robot
from configs import globals as g
from utils.logger import Logger, configure_logger, set_log_level



class TestRobotModeControl:
    """로봇 모드 제어 테스트"""
    
    def test_set_mode_fix(self):
        """고정 모드 설정"""
        result = set_mode("fix")
        assert result is not None, "고정 모드 설정 실패"
        assert g.get_robot_mode() == "fix", "Global 변수 업데이트 실패"
        Logger.success("고정 모드 설정 테스트 통과")
    
    def test_set_mode_free(self):
        """이동 모드 설정"""
        result = set_mode("free")
        assert result is not None, "이동 모드 설정 실패"
        assert g.get_robot_mode() == "free", "Global 변수 업데이트 실패"
        Logger.success("이동 모드 설정 테스트 통과")
    
    def test_set_mode_point(self):
        """점 고정 모드 설정"""
        result = set_mode("point")
        assert result is not None, "점 고정 모드 설정 실패"
        assert g.get_robot_mode() == "point", "Global 변수 업데이트 실패"
        Logger.success("점 고정 모드 설정 테스트 통과")
    
    def test_set_mode_line(self):
        """선 고정 모드 설정"""
        result = set_mode("line")
        assert result is not None, "선 고정 모드 설정 실패"
        assert g.get_robot_mode() == "line", "Global 변수 업데이트 실패"
        Logger.success("선 고정 모드 설정 테스트 통과")
    
    def test_set_mode_invalid(self):
        """잘못된 모드 처리"""
        result = set_mode("invalid_mode")
        assert result is None, "잘못된 모드가 수락됨"
        Logger.success("잘못된 모드 처리 테스트 통과")



class TestRobotModeQuery:
    """로봇 모드 조회 테스트"""
    
    def test_get_current_mode(self):
        """현재 모드 조회"""
        set_mode("fix")
        mode = get_current_mode()
        assert mode == "fix", "현재 모드 조회 실패"
        
        set_mode("free")
        mode = get_current_mode()
        assert mode == "free", "현재 모드 조회 실패"
        
        Logger.success("현재 모드 조회 테스트 통과")



class TestRobotMovement:
    """로봇 이동 제어 테스트"""
    
    def test_move_robot_in_free_mode(self):
        """이동 모드에서 로봇 이동"""
        set_mode("free")
        
        # 초기 위치 저장
        initial_position = g.robot_position.copy()
        
        # 이동
        result = move_robot(10, 20)
        assert "이동 완료" in result, "이동 실패"
        
        # 위치 변경 확인
        new_position = g.robot_position
        assert new_position[0] == initial_position[0] + 10, "X축 이동 실패"
        assert new_position[1] == initial_position[1] + 20, "Y축 이동 실패"
        
        Logger.success("이동 모드 로봇 이동 테스트 통과")
    
    def test_move_robot_in_fixed_mode(self):
        """고정 모드에서 이동 시도"""
        set_mode("fix")
        
        result = move_robot(10, 20)
        assert "이동 모드가 아닙니다" in result, "고정 모드 이동 제한 실패"
        
        Logger.success("고정 모드 이동 제한 테스트 통과")



class TestRobotStop:
    """로봇 정지 제어 테스트"""
    
    def test_stop_robot(self):
        """로봇 정지"""
        result = stop_robot()
        assert "정지" in result, "로봇 정지 실패"
        assert g.get_robot_mode() == "stop", "정지 모드 설정 실패"
        Logger.success("로봇 정지 테스트 통과")



class TestGlobalIntegration:
    """Global 변수 연동 테스트"""
    
    def test_robot_mode_persistence(self):
        """로봇 모드 지속성"""
        set_mode("point")
        mode1 = get_current_mode()
        
        # 다른 함수 호출 후에도 모드 유지
        mode2 = get_current_mode()
        
        assert mode1 == mode2 == "point", "모드 지속성 실패"
        Logger.success("로봇 모드 지속성 테스트 통과")
    
    def test_robot_position_tracking(self):
        """로봇 위치 추적"""
        set_mode("free")
        
        # 위치 초기화
        g.robot_position = [0, 0]
        
        # 여러 번 이동
        move_robot(5, 10)
        move_robot(3, -2)
        
        position = g.robot_position
        assert position[0] == 8, "X축 누적 이동 실패"
        assert position[1] == 8, "Y축 누적 이동 실패"
        
        Logger.success("로봇 위치 추적 테스트 통과")



if __name__ == "__main__":
    # Logger 설정
    configure_logger(use_emoji=True, use_color=True, log_to_file=False)
    set_log_level("INFO")
    
    Logger.section("Robot Commands 유틸리티 테스트")
    
    # 모드 제어 테스트
    Logger.info("로봇 모드 제어 테스트 시작", emoji="🤖")
    test_mode = TestRobotModeControl()
    test_mode.test_set_mode_fix()
    test_mode.test_set_mode_free()
    test_mode.test_set_mode_point()
    test_mode.test_set_mode_line()
    test_mode.test_set_mode_invalid()
    Logger.separator()
    
    # 모드 조회 테스트
    Logger.info("로봇 모드 조회 테스트 시작", emoji="🔍")
    test_query = TestRobotModeQuery()
    test_query.test_get_current_mode()
    Logger.separator()
    
    # 이동 제어 테스트
    Logger.info("로봇 이동 제어 테스트 시작", emoji="🚀")
    test_move = TestRobotMovement()
    test_move.test_move_robot_in_free_mode()
    test_move.test_move_robot_in_fixed_mode()
    Logger.separator()
    
    # 정지 제어 테스트
    Logger.info("로봇 정지 제어 테스트 시작", emoji="🛑")
    test_stop = TestRobotStop()
    test_stop.test_stop_robot()
    Logger.separator()
    
    # Global 연동 테스트
    Logger.info("Global 변수 연동 테스트 시작", emoji="🔗")
    test_global = TestGlobalIntegration()
    test_global.test_robot_mode_persistence()
    test_global.test_robot_position_tracking()
    Logger.separator()
    
    Logger.section("✅ Robot Commands 유틸리티 테스트 완료")
