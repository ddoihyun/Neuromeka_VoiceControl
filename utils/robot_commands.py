# utils/robot_commands.py
"""
로봇 명령 실행 함수
Global 변수 기반으로 단순화
"""
from configs import globals as g
from utils.logger import Logger


def execute_command(action: str) -> str:
    """
    로봇 모드 변경
    Args:
        mode: "stop" | "point" | "line" | "free" | "direct_teaching" | "simulation" | "tracking" | "calibration" | "navigation" | "exit"
    Returns:
        성공 메시지 또는 None
    """
    if action == "stop":
        g.set_robot_mode("stop")
        return "정지"
    
    elif action == "point":
        g.set_robot_mode("point")
        return "점 고정 모드로 전환"
    
    elif action == "line":
        g.set_robot_mode("line")
        return "선 고정 모드로 전환"
    
    elif action == "free":
        g.set_robot_mode("free")
        return "자유 이동 모드로 전환"
    
    elif action == "direct_teaching":
        g.set_robot_mode("direct_teaching")
        return "직접교시 모드로 전환"
    
    elif action == "simulation":
        g.set_robot_mode("simulation")
        return "시뮬레이션 모드로 전환"
    
    elif action == "tracking":
        g.set_robot_mode("tracking")
        return "타겟 추적 모드 시작"
    
    elif action == "calibration":
        g.set_robot_mode("calibration")
        return "캘리브레이션 시작"
    
    elif action == "navigation":
        g.set_robot_mode("navigation")
        return "내비게이션 모드 시작"
    
    elif action == "exit":
        g.set_robot_mode("exit")
        return "프로그램 종료"
    
    else:
        Logger.warning(f"알 수 없는 모드: {action}")
        return None


def get_current_mode() -> str:
    """현재 로봇 모드 반환"""
    return g.get_robot_mode()

# def move_robot(dx: float, dy: float) -> str:
#     """
#     로봇 이동 (향후 확장용)
#     Args:
#         dx: X축 이동 거리
#         dy: Y축 이동 거리
#     Returns:
#         결과 메시지
#     """
#     if g.get_robot_mode() != "free":
#         return "이동 모드가 아닙니다"
    
#     with g._lock:
#         g.robot_position[0] += dx
#         g.robot_position[1] += dy
#         position = g.robot_position.copy()
    
#     return f"이동 완료: {position}"

# def stop_robot() -> str:
#     """로봇 정지"""
#     g.set_robot_mode("stop")
#     return "로봇 정지"
