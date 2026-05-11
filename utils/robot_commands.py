# utils/robot_commands.py
"""
로봇 명령 실행 함수
Global 변수 기반으로 단순화
"""
from configs import globals as g
from utils.logger import Logger


def set_mode(mode: str) -> str:
    """
    로봇 모드 변경
    Args:
        mode: "fix" | "free" | "point" | "line"
    Returns:
        성공 메시지 또는 None
    """
    if mode == "fix":
        g.set_robot_mode("fix")
        return "고정 모드로 전환"
    
    elif mode == "free":
        g.set_robot_mode("free")
        return "이동 모드로 전환"
    
    elif mode == "point":
        g.set_robot_mode("point")
        return "점 고정 모드로 전환"
    
    elif mode == "line":
        g.set_robot_mode("line")
        return "선 고정 모드로 전환"
    
    else:
        Logger.warning(f"알 수 없는 모드: {mode}")
        return None


def get_current_mode() -> str:
    """현재 로봇 모드 반환"""
    return g.get_robot_mode()

def move_robot(dx: float, dy: float) -> str:
    """
    로봇 이동 (향후 확장용)
    Args:
        dx: X축 이동 거리
        dy: Y축 이동 거리
    Returns:
        결과 메시지
    """
    if g.get_robot_mode() != "free":
        return "이동 모드가 아닙니다"
    
    with g._lock:
        g.robot_position[0] += dx
        g.robot_position[1] += dy
        position = g.robot_position.copy()
    
    return f"이동 완료: {position}"

def stop_robot() -> str:
    """로봇 정지"""
    g.set_robot_mode("stop")
    return "로봇 정지"
