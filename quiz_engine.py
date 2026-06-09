import random
import sqlite3
import difflib
from dataclasses import dataclass, field
from fsm import QuizFSM, State


@dataclass
class Message:
    role: str        
    text: str
    choices: list[str] = field(default_factory=list)
    emoji: str = ""
    tag: str = ""     

@dataclass
class Question:
    id: int
    category: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

# ─────────────────────────────────────────────────────────────────
#  DATABASE SOAL — 3 Level × 3 Soal = 9 Soal Total (180 XP Max)
# ─────────────────────────────────────────────────────────────────

LEVELS = {
    1: {
        "name": "Recruit",
        "title": "🟢 LEVEL 1 — Jaringan & Dasar",
        "questions": [
            Question(1, "Networking", "Protokol apa yang digunakan untuk mengirim halaman web secara aman?",
                     ["HTTP", "HTTPS", "FTP", "SSH"], "HTTPS",
                     "HTTPS menggunakan enkripsi SSL/TLS untuk mengamankan pertukaran data."),
            Question(2, "Coding/Python", "Manakah tipe data di Python yang bersifat 'immutable' (tidak bisa diubah nilainya setelah dibuat)?",
                     ["List", "Dictionary", "Tuple", "Set"], "Tuple",
                     "Tuple di Python bersifat immutable dan ditulis menggunakan tanda kurung biasa ( )."),
            Question(3, "Struktur Data", "Struktur data yang menggunakan prinsip FIFO (First In First Out) adalah...",
                     ["Stack", "Queue", "Tree", "Graph"], "Queue",
                     "Queue (Antrean) memproses data yang pertama kali masuk untuk dikeluarkan pertama kali juga.")
        ]
    },
    2: {
        "name": "Hacker",
        "title": "🔵 LEVEL 2 — Algoritma & Pemrograman",
        "questions": [
            Question(4, "Algoritma", "Notasi Big-O yang menggambarkan kompleksitas waktu terbaik untuk Binary Search adalah...",
                     ["O(n)", "O(log n)", "O(n²)", "O(1)"], "O(log n)",
                     "Binary Search membagi ruang pencarian setengah setiap iterasi, sehingga O(log n)."),
            Question(5, "Database", "Perintah SQL untuk mengambil data yang unik (tidak duplikat) dari sebuah kolom adalah...",
                     ["SELECT ALL", "SELECT UNIQUE", "SELECT DISTINCT", "SELECT TOP"], "SELECT DISTINCT",
                     "SELECT DISTINCT menyaring baris duplikat sehingga setiap nilai hanya muncul satu kali."),
            Question(6, "Jaringan", "Model referensi jaringan yang terdiri dari 7 lapisan (layer) disebut...",
                     ["TCP/IP Model", "OSI Model", "HTTP Model", "DNS Model"], "OSI Model",
                     "OSI (Open Systems Interconnection) Model memiliki 7 layer: Physical, Data Link, Network, Transport, Session, Presentation, Application."),
        ]
    },
    3: {
        "name": "Elite Coder",
        "title": "🔴 LEVEL 3 — Sistem & Keamanan Lanjut",
        "questions": [
            Question(7, "Sistem Operasi", "Kondisi di mana dua proses saling menunggu sumber daya yang dikuasai satu sama lain disebut...",
                     ["Race Condition", "Deadlock", "Starvation", "Context Switch"], "Deadlock",
                     "Deadlock terjadi saat proses A menunggu resource milik B, sementara B menunggu resource milik A."),
            Question(8, "CyberSecurity", "Serangan yang menyisipkan skrip berbahaya ke dalam halaman web yang dilihat pengguna lain disebut...",
                     ["CSRF", "XSS", "SQL Injection", "Man-in-the-Middle"], "XSS",
                     "Cross-Site Scripting (XSS) menyisipkan script client-side berbahaya ke halaman web untuk mencuri data pengguna."),
            Question(9, "Algoritma", "Algoritma sorting yang memiliki kompleksitas waktu rata-rata O(n log n) dan bersifat divide & conquer adalah...",
                     ["Bubble Sort", "Insertion Sort", "Merge Sort", "Selection Sort"], "Merge Sort",
                     "Merge Sort membagi array menjadi dua bagian secara rekursif lalu menggabungkannya dalam urutan terurut — O(n log n)."),
        ]
    }
}

PLAYER_TITLES = {
    1: "🟢 Cyber Recruit",
    2: "🔵 Network Hacker",
    3: "🔴 Elite Coder",
}

FUN_FACTS = [
    "Bug komputer pertama ditemukan berupa sebuah 'ngengat' asli yang terjebak di dalam mesin komputer Harvard Mark II pada tahun 1947.",
    "Bahasa pemrograman Python bukan dinamai dari jenis ular, melainkan dari acara komedi TV Inggris 'Monty Python's Flying Circus'.",
    "Lebih dari 90% mata uang di dunia saat ini hanya eksis dalam bentuk kode digital di dalam server perbankan.",
    "Linus Torvalds menciptakan kernel Linux pada usia 21 tahun sebagai proyek hobi mahasiswa di Helsinki, Finlandia.",
    "Ada lebih dari 700 bahasa pemrograman yang pernah dibuat, meskipun hanya sekitar 20 yang digunakan secara luas di industri.",
]

MAX_LEVELS = len(LEVELS)
XP_PER_CORRECT = 20
MAX_XP = MAX_LEVELS * 3 * XP_PER_CORRECT


class QuizEngine:
    def __init__(self):
        self.fsm = QuizFSM()
        self.session_data: dict = {}
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect("quiz_data.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                score INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def _save_score(self, name, score):
        conn = sqlite3.connect("quiz_data.db")
        conn.execute(
            "INSERT INTO leaderboard(name, score) VALUES (?, ?)",
            (name, score)
        )
        conn.commit()
        conn.close()

    def _get_leaderboard(self):
            conn = sqlite3.connect("quiz_data.db")
            rows = conn.execute("""
                SELECT name, score
                FROM leaderboard
                ORDER BY score DESC
                LIMIT 10
            """).fetchall()
            conn.close()
            return rows

    def start(self) -> list[Message]:
        self.fsm.reset()
        self.session_data = {
            "score": 0,
            "accumulated_xp": 0,
            "streak": 0,
            "current_level": 1,          
            "level_idx": 0,              
            "total_match": 0,            
            "player_name": "Anonymous",
            "player_title": PLAYER_TITLES[1],
            "last_answer": "",
            "lives": 3,            
            "hints_left": 2,       
            "game_over": False,  
        }
        self.fsm.transition("boot")
        return self._handle_state()

    def process_input(self, user_input: str) -> list[Message]:
        if self.fsm.current_state == State.PLAYING and user_input.lower().strip() in ["bantuan", "hint"]:
            if self.session_data.get("hints_left", 0) > 0:

                self.session_data["hints_left"] -= 1
                
                idx = self.session_data.get("level_idx", 0)
                q = self._current_questions()[idx]
  
                penalty = 5
                self.session_data["score"] = max(0, self.session_data.get("score", 0) - penalty)
                
                ans = q.correct_answer
                clue = ans[:max(1, len(ans)//2)] + ("_" * (len(ans) - max(1, len(ans)//2)))
                sisa_hint = self.session_data["hints_left"]
                
                return [
                    Message("bot",
                            f"💡 BANTUAN DIAKTIFKAN (-{penalty} XP)\n\n"
                            f"Petunjuk huruf depan jawaban: {clue}\n\n"
                            f"Sisa bantuan Anda: {sisa_hint}x\n\n"
                            f"Silakan ketik tebakan Anda di bawah:",
                            emoji="🔑", tag="warning")
                ]
            else:
                return [
                    Message("bot",
                            "⚠️ BANTUAN HABIS!\n\n"
                            "Anda sudah menggunakan semua jatah bantuan (2/2). Percayalah pada insting Anda!",
                            emoji="🚫", tag="danger")
                ]

        intent, data = self._parse_intent(user_input)
        if data:
            self.session_data.update(data)

        if self.fsm.current_state == State.CHECKING_ANSWER and self.session_data.get("game_over"):
            if intent in ["next_question", "trigger_lvlup", "quiz_done", "menu"] or "lanjut" in user_input.lower():
                self.session_data.update({
                    "score": 0,
                    "current_level": 1,
                    "level_idx": 0,
                    "lives": 3,
                    "hints_left": 2,
                    "game_over": False,
                    "streak": 0,
                    "total_match": 0
                })
                for k in list(self.session_data.keys()):
                    if k.startswith("shuffled_questions"):
                        del self.session_data[k]
                intent = "next_question"

        success, _ = self.fsm.transition(intent)
        if not success:
            return [Message("bot", "🚨 Perintah tidak dikenali.", emoji="🤖", tag="warning")]

        return self._handle_state()

    def get_state(self) -> str:
        if hasattr(self.fsm, "current_state") and hasattr(self.fsm.current_state, "name"):
            return self.fsm.current_state.name.upper()
        return str(self.fsm.current_state).upper()

    def _current_questions(self) -> list[Question]:
        lvl = self.session_data.get("current_level", 1)
        if lvl > MAX_LEVELS:
            lvl = MAX_LEVELS
            
        order_key = f"shuffled_questions_lvl_{lvl}"
        if order_key not in self.session_data:
            questions_copy = list(LEVELS[lvl]["questions"])
            random.shuffle(questions_copy)
            self.session_data[order_key] = questions_copy
            
        return self.session_data[order_key]

    def _is_level_done(self) -> bool:
        return self.session_data.get("level_idx", 0) >= len(self._current_questions())

    def _is_all_done(self) -> bool:
        lvl = self.session_data.get("current_level", 1)
        idx = self.session_data.get("level_idx", 0)
        return lvl >= MAX_LEVELS and idx >= len(self._current_questions())

    def _handle_state(self) -> list[Message]:
        s = self.fsm.current_state

        if s == State.GREETING:
            return [
                Message("bot",
                        "⚡ SYSTEM BOOT SUCCESSFUL ⚡\n\n"
                        "Selamat datang di GUESS IT v2.0. "
                        "Saya adalah Core AI yang akan menguji pengetahuan Informatika Anda.\n\n"
                        "Tersedia 3 Level dengan 3 soal masing-masing (Total 9 soal / 180 XP).",
                        emoji="🛡️", tag="hero"),
                Message("bot", "Ketik MULAI untuk memasuki sistem terminal kuis.", emoji="⌨️", tag="action")
            ]

        elif s == State.MAIN_MENU:
            lvl = self.session_data.get("current_level", 1)
            lvl_name = LEVELS.get(lvl, LEVELS[1])["title"]
            return [
                Message("bot",
                        f"🖥️ MAINFRAME TERMINAL — {lvl_name}\n\n"
                        "Silakan ketik salah satu perintah operasi berikut:\n"
                        "• Ketik KUIS — Mulai menjawab soal kuis\n"
                        "• Ketik RANKING — Papan peringkat skor\n"
                        "• Ketik FACT — Info unik seputar dunia IT\n"
                        "• Ketik SHUTDOWN — Keluar dari terminal",
                        emoji="⚙️", tag="menu")
            ]

        elif s == State.PLAYING:
            lvl = self.session_data["current_level"]
            idx = self.session_data["level_idx"]
            questions = self._current_questions()
            
            if idx >= len(questions):
                idx = len(questions) - 1
                
            q = questions[idx]
            total_done = (lvl - 1) * 3 + idx + 1
            
            shuffled_options = list(q.options)
            random.shuffle(shuffled_options)
            options_text = "\n".join([f"🔸 {opt}" for opt in shuffled_options])
            nyawa = self.session_data.get("lives", 3)
            hearts = ("❤️" * nyawa) + ("🖤" * (3 - nyawa))
            return [

                Message("bot",
                        f"🛡️ NYAWA: {hearts}\n"
                        f"📁 Kategori: {q.category} "
                        f"(Level {lvl} — Soal {idx + 1}/3 | Total {total_done}/9)\n\n"
                        f"{q.question}\n\nPilihan Jawaban:\n{options_text}\n\n"
                        "👉 Ketik jawaban Anda di bawah. (Ketik BANTUAN jika kesulitan)",
                        emoji="❓", tag="step")
            ]

        elif s == State.CHECKING_ANSWER:
            lvl = self.session_data["current_level"]
            idx = self.session_data["level_idx"]
            questions = self._current_questions()
            
            if idx >= len(questions):
                idx = len(questions) - 1
                
            q = questions[idx]
            ans = self.session_data.get("last_answer", "")

            is_correct = (ans.strip().lower() == q.correct_answer.lower())
            
            if is_correct:
                self.session_data["score"] += XP_PER_CORRECT
                self.session_data["accumulated_xp"] += XP_PER_CORRECT
                self.session_data["streak"] += 1
                msg = f"🟢 ACCESS GRANTED! JAWABAN BENAR.\n\n{q.explanation}"
                tag, emoji = "success", "✅"
            else:
                self.session_data["streak"] = 0
                self.session_data["lives"] -= 1  
                sisa_nyawa = self.session_data["lives"]
                
                if sisa_nyawa > 0:
                    hearts = ("❤️" * sisa_nyawa) + ("🖤" * (3 - sisa_nyawa))
                    msg = (f"🔴 ACCESS DENIED! JAWABAN SALAH.\n"
                           f"Sisa Nyawa: {hearts}\n\n"
                           f"Jawaban benar: {q.correct_answer}\n\n{q.explanation}")
                    tag, emoji = "danger", "❌"
                else:
                    self.session_data["game_over"] = True
                    msg = (f"💀 FATAL ERROR! NYAWA HABIS.\n\n"
                           f"Jawaban benar: {q.correct_answer}\n\n"
                           f"Sistem terminal terkena virus karena terlalu banyak kesalahan. "
                           f"Anda telah dikeluarkan dari jaringan.")
                    tag, emoji = "danger", "💀"

            self.session_data["total_match"] += 1
            new_idx = idx + 1
            self.session_data["level_idx"] = new_idx  

            all_done = self._is_all_done()
            level_done = self._is_level_done()

            if self.session_data.get("game_over"):
                next_hint = "LANJUT untuk me-reboot koneksi dari Level 1"
            elif all_done:
                next_hint = "LANJUT untuk melihat hasil skor akhir"
            elif level_done:
                next_hint = "LANJUT untuk naik ke level berikutnya"
            else:
                next_hint = "LANJUT untuk memuat soal berikutnya"

            return [
                Message("bot", msg, emoji=emoji, tag=tag),
                Message("bot", f"⌨️ Sesi dijeda. Ketik {next_hint}.", tag="action")
            ]

        elif s == State.LEVEL_UP:
            old_lvl = self.session_data["current_level"]
            next_lvl = old_lvl + 1
            
            if next_lvl > MAX_LEVELS:
                next_lvl = MAX_LEVELS
                
            self.session_data["current_level"] = next_lvl
            self.session_data["level_idx"] = 0
            self.session_data["player_title"] = PLAYER_TITLES.get(next_lvl, PLAYER_TITLES[MAX_LEVELS])
            
            lvl_info = LEVELS[next_lvl]
            return [
                Message("bot",
                        f"🎖️ LEVEL UP! Selamat, Anda naik ke {lvl_info['title']}!\n\n"
                        f"Ketik LANJUT untuk memuat soal Level {next_lvl}.",
                        emoji="⬆️", tag="hero")
            ]

        elif s == State.SHOW_LEADERBOARD:
                    rows = self._get_leaderboard()
                    board = "🏆 GUESS RANKINGS (TOP HACKERS)\n\n"
                    if rows:
                        for i, (name, score) in enumerate(rows, start=1):
                            board += f"{i}. `{name}` — {score} PTS\n"
                    else:
                        board += "Belum ada data ranking.\n"
                    
                    return [
                        Message("bot", board, emoji="🏆", tag="hero"),
                        Message("bot", "Ketik MENU untuk kembali ke mainframe.", tag="action")
                    ]

        elif s == State.SHOW_TIPS:
            return [
                Message("bot", f"💡 DID YOU KNOW?\n\n{random.choice(FUN_FACTS)}", emoji="⚡", tag="tutorial"),
                Message("bot", "Ketik MENU untuk kembali ke mainframe.", tag="action")
            ]

        elif s == State.FEEDBACK:
            final_score = self.session_data.get("score", 0)
            correct = final_score // XP_PER_CORRECT
            total = self.session_data.get("total_match", 9)
            best_streak = self.session_data.get("streak", 0)

            player_name = self.session_data.get("player_name", "Anonymous")

            # Simpan ke database
            self._save_score(player_name, final_score)

            return [
                Message(
                    "bot",
                    f"🎉 SEMUA LEVEL SELESAI! 🎉\n\n"
                    f"📊 Total XP: {final_score} / {MAX_XP} PTS\n"
                    f"✅ Benar: {correct} / {total} soal\n"
                    f"🔥 Streak Terbaik: {best_streak}x\n\n"
                    "Ketik RANKING untuk melihat peringkat atau DONE untuk keluar.",
                    emoji="📊",
                    tag="feedback"
                )
            ]

        elif s == State.END:
            return [
                Message(
                    "bot",
                    "🔌 SYSTEM SHUTDOWN SUCCESSFULLY\n\n"
                    "Koneksi terminal aman terputus. Ketik REBOOT untuk menyalakan ulang.",
                    emoji="💤",
                    tag="end"
                )
            ]

    def _parse_intent(self, text: str) -> tuple[str, dict | None]:
        t = text.lower().strip()
        s = self.fsm.current_state

        if s == State.GREETING:
            if "mulai" in t:
                return "continue", None

        elif s == State.MAIN_MENU:
            if "kuis" in t:
                return "start_quiz", {"level_idx": 0}
            if "ranking" in t or "leaderboard" in t:
                return "leaderboard", None
            if "fact" in t or "tips" in t:
                return "fun_tips", None
            if "shutdown" in t:
                return "shutdown", None
            
        elif s == State.SHOW_TIPS:
            if "menu" in t:
                return "menu", None

        elif s == State.PLAYING:
            return "submit_answer", {"last_answer": text}

        elif s == State.CHECKING_ANSWER:
            if "lanjut" in t or "next" in t:
                if self._is_all_done():
                    return "quiz_done", None
                if self._is_level_done():
                    return "trigger_lvlup", None
                return "next_question", None
            
            if "menu" in t:
                return "menu", None

        elif s == State.LEVEL_UP:
            if "lanjut" in t or "next" in t:
                return "continue_level", {"level_idx": 0}

        elif s == State.SHOW_LEADERBOARD:
            if "menu" in t:
                return "menu", None
            if "kembali" in t:
                return "feedback", None

        elif s == State.FEEDBACK:
            if "ranking" in t:
                return "leaderboard", None
            if "done" in t:
                return "feedback_done", None

        elif s == State.END:
            if "reboot" in t or "restart" in t:
                return "reboot", None

        return "__unknown__", None
    