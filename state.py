WAITING_LEVEL = "WAITING_LEVEL"
WAITING_FEEDBACK_LANG ="WAITING_FEEDBACK_LANG"
WAITING_TASK = "WAITING_TASK"
WAITING_CV = "WAITING_CV"
WAITING_JD = "WAITING_JD"

user_states = {}

def create_user_state() -> dict:
    return {
        "phase": WAITING_LEVEL,
        "italian_level": None,
        "feedback_language": None,
        "task": None,
        "cv_file_path": None,
        "jd_file_path": None,
    }