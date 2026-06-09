from enum import Enum, auto

class State(Enum):
    START            = auto()
    GREETING         = auto()
    MAIN_MENU        = auto()
    PLAYING          = auto()
    CHECKING_ANSWER  = auto()
    LEVEL_UP         = auto()
    SHOW_LEADERBOARD = auto()
    SHOW_TIPS        = auto()
    FEEDBACK         = auto()
    END              = auto()

# SATUKAN SEMUA ATURAN DI SINI
TRANSITIONS = {
    (State.START,             "boot"):           State.GREETING,
    (State.GREETING,          "continue"):       State.MAIN_MENU,
    
    (State.MAIN_MENU,         "start_quiz"):     State.PLAYING,
    (State.MAIN_MENU,         "leaderboard"):    State.SHOW_LEADERBOARD,
    (State.MAIN_MENU,         "fun_tips"):       State.SHOW_TIPS,
    (State.MAIN_MENU,         "shutdown"):       State.END,
    
    (State.PLAYING,           "submit_answer"):  State.CHECKING_ANSWER,
    (State.CHECKING_ANSWER,   "next_question"):  State.PLAYING,
    (State.CHECKING_ANSWER,   "trigger_lvlup"):  State.LEVEL_UP,
    (State.CHECKING_ANSWER,   "quiz_done"):      State.FEEDBACK,
    
    (State.LEVEL_UP,          "continue_level"): State.PLAYING,
    
    # Transisi yang Anda inginkan
    (State.SHOW_LEADERBOARD,  "menu"):           State.MAIN_MENU,
    (State.SHOW_LEADERBOARD,  "feedback"):       State.FEEDBACK,
    (State.SHOW_TIPS,         "menu"):           State.MAIN_MENU,
    (State.FEEDBACK,          "leaderboard"):    State.SHOW_LEADERBOARD,
    (State.FEEDBACK,          "feedback_done"):  State.END,
    (State.FEEDBACK,          "menu"):           State.MAIN_MENU, # Tambahan agar dari feedback bisa ke menu
    
    (State.END,               "reboot"):         State.START,
}

class QuizFSM:
    def __init__(self):
        self.current_state: State = State.START

    def transition(self, intent: str) -> tuple[bool, State]:
        key = (self.current_state, intent)
        if key in TRANSITIONS:
            self.current_state = TRANSITIONS[key]
            return True, self.current_state
        return False, self.current_state

    def reset(self):
        self.current_state = State.START