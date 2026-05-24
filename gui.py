# gui.py
# هاد ملف الواجهة الرسومية (GUI) للعبة باستخدام مكتبة PyQt6 الاحترافية.
# تم تصميمه بأسلوب عصري جداً (Dark Mode) وبشاشة عرض فورية لتحليل تفكير الذكاء الاصطناعي (Minimax Diagnostics).

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QComboBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# استيراد منطق اللعبة وخوارزمية الـ Minimax من الملف المنفصل
from game_logic import TicTacToeGame, find_best_move
import game_logic

class TicTacToeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = TicTacToeGame()
        self.ai_player = 'O'
        self.human_player = 'X'
        self.current_turn = 'X' # اللاعب الذي يبدأ اللعب أولاً
        self.is_game_over = False
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Tic-Tac-Toe AI (Minimax Algorithm)")
        self.setMinimumSize(850, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0e14; /* خلفية الفضاء الداكنة */
            }
            QLabel {
                color: #c9d1d9;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QComboBox {
                background-color: #1f293d;
                border: 2px solid #2d3d5a;
                border-radius: 8px;
                color: #ffffff;
                padding: 6px 12px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }
            QComboBox:hover {
                border: 2px solid #00f0ff;
            }
            QComboBox QAbstractItemView {
                background-color: #1f293d;
                color: #ffffff;
                selection-background-color: #00f0ff;
                selection-color: #0b0e14;
            }
            QPushButton#reset_btn {
                background-color: #ff5e62;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#reset_btn:hover {
                background-color: #ff7b7f;
            }
            QPushButton#reset_btn:pressed {
                background-color: #d14b4f;
            }
        """)

        # الودجت الرئيسي والتخطيط العام (أفقي لتقسيم الشاشة لعمودين)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # =====================================================================
        # العمود الأيسر: لوحة اللعب (Game Board Panel)
        # =====================================================================
        left_panel = QVBoxLayout()
        
        # عنوان علوي أنيق
        title_label = QLabel("TIC-TAC-TOE AI")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #00f0ff; margin-bottom: 5px;") # لون نيوني سماوي
        left_panel.addWidget(title_label)
        
        # مؤشر الدور الحالي
        self.status_label = QLabel("نو ريسك نو فان🤭")
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #8b949e; margin-bottom: 15px;")
        left_panel.addWidget(self.status_label)

        # شبكة أزرار اللعبة 3x3
        self.board_grid = QGridLayout()
        self.board_grid.setSpacing(10)
        self.buttons = []
        
        for i in range(9):
            btn = QPushButton("")
            btn.setObjectName(f"cell_{i}")
            btn.setFixedSize(120, 120)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
            
            # تنسيق أزرار الشبكة بـ QSS (توهج وحواف دائرية أنيقة)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #151b26;
                    border: 2px solid #2d3d5a;
                    border-radius: 15px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #1f2a3d;
                    border: 2px solid #00f0ff; /* توهج أزرق على الهوفر */
                }
                QPushButton:pressed {
                    background-color: #0b0e14;
                }
            """)
            
            # ربط الزر بحدث الضغط
            btn.clicked.connect(lambda checked, idx=i: self.cell_clicked(idx))
            self.buttons.append(btn)
            
            row, col = divmod(i, 3)
            self.board_grid.addWidget(btn, row, col)
            
        left_panel.addLayout(self.board_grid)
        left_panel.addStretch()
        
        # =====================================================================
        # العمود الأيمن: لوحة التحكم وتحليل الذكاء الاصطناعي (Control & Diagnostics Panel)
        # =====================================================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # --- مجموعة خيارات اللعب (Game Settings Group) ---
        settings_group = QGroupBox("إعدادات اللعبة (Settings)")
        settings_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        settings_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2d3d5a;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                color: #00f0ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(10)
        
        # مستوى الصعوبة
        diff_layout = QHBoxLayout()
        diff_label = QLabel("مستوى الصعوبة:")
        diff_label.setFont(QFont("Segoe UI", 11))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Hard (Unbeatable)", "Medium (Depth Limit=2)", "Easy (Random)"])
        diff_layout.addWidget(diff_label)
        diff_layout.addWidget(self.diff_combo)
        settings_layout.addLayout(diff_layout)
        
        # اختيار من يبدأ اللعب
        start_layout = QHBoxLayout()
        start_label = QLabel("من يبدأ باللعب؟")
        start_label.setFont(QFont("Segoe UI", 11))
        self.start_combo = QComboBox()
        self.start_combo.addItems(["المستخدم (X)", "الكمبيوتر (O)"])
        self.start_combo.currentIndexChanged.connect(self.starting_player_changed)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_combo)
        settings_layout.addLayout(start_layout)
        
        right_panel.addWidget(settings_group)
        
        # --- مجموعة تحليل تفكير الـ Minimax (Live Explainer Panel) ---
        diagnostics_group = QGroupBox("تحليل تفكير الذكاء الاصطناعي (Minimax Diagnostics)")
        diagnostics_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        diagnostics_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2d3d5a;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                color: #ff5e62; /* لون برتقالي/محمر نيوني */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        diag_layout = QVBoxLayout(diagnostics_group)
        diag_layout.setSpacing(12)
        
        # عدد الحالات المستكشفة (States Explored)
        states_title = QLabel("🔍 عدد الحالات المستكشفة (States Explored):")
        states_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.states_val = QLabel("0 حالة")
        self.states_val.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.states_val.setStyleSheet("color: #00f0ff; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #2d3d5a;")
        diag_layout.addWidget(states_title)
        diag_layout.addWidget(self.states_val)
        
        # التقييم الحالي للحركة (Score)
        score_title = QLabel("📊 تقييم الحركة المثالية (Evaluation Score):")
        score_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.score_val = QLabel("لم يلعب الكمبيوتر بعد")
        self.score_val.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.score_val.setStyleSheet("color: #ff5e62; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #2d3d5a;")
        diag_layout.addWidget(score_title)
        diag_layout.addWidget(self.score_val)
        
        # شرح الخطوة الحالية
        expl_title = QLabel("💡 تفسير الكمبيوتر لخطوته (AI Decision):")
        expl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.expl_val = QLabel("بانتظار حركتك الأولى للبدء في التحليل...")
        self.expl_val.setWordWrap(True)
        self.expl_val.setFont(QFont("Segoe UI", 10))
        self.expl_val.setStyleSheet("color: #8b949e; background-color: #151b26; padding: 10px; border-radius: 6px; border: 1px solid #2d3d5a;")
        self.expl_val.setMinimumHeight(80)
        diag_layout.addWidget(expl_title)
        diag_layout.addWidget(self.expl_val)
        
        right_panel.addWidget(diagnostics_group)
        
        # زر إعادة اللعب (Reset)
        self.reset_button = QPushButton("إعادة اللعب والبدء من جديد 🔄")
        self.reset_button.setObjectName("reset_btn")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_game)
        right_panel.addWidget(self.reset_button)
        
        # إضافة العمودين للتخطيط الرئيسي
        main_layout.addLayout(left_panel, stretch=3)
        main_layout.addLayout(right_panel, stretch=2)

    def starting_player_changed(self):
        """التعامل مع تغيير اللاعب البادئ"""
        self.reset_game()

    def cell_clicked(self, idx):
        """التعامل مع نقر المربع من قبل اللاعب البشري"""
        # إذا كانت اللعبة منتهية، أو لم يكن دور الإنسان، أو المربع غير فارغ -> تجاهل الضغط
        if self.is_game_over or self.current_turn != self.human_player or self.game.board[idx] != " ":
            return
            
        # 1. تنفيذ حركة الإنسان
        self.game.make_move(idx, self.human_player)
        self.update_board_ui()
        
        # التحقق من حالة الفوز/التعادل بعد حركة الإنسان
        winner = self.game.check_winner()
        if winner:
            self.handle_game_over(winner)
            return
            
        # 2. تحويل الدور للذكاء الاصطناعي
        self.current_turn = self.ai_player
        self.status_label.setText("الكمبيوتر يفكر الآن... 🧠")
        self.status_label.setStyleSheet("color: #ff5e62;")
        
        # تعطيل الواجهة مؤقتاً أثناء تفكير الكمبيوتر لإعطاء لمسة احترافية
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        # تشغيل حركة الكمبيوتر بعد تأخير بسيط (300 مللي ثانية) لتبدو طبيعية ويلاحظها المستخدم
        QTimer.singleShot(400, self.ai_turn)

    def ai_turn(self):
        """تنفيذ دور الذكاء الاصطناعي باستخدام Minimax"""
        QApplication.restoreOverrideCursor() # إعادة المؤشر لشكل الطبيعي
        
        if self.is_game_over:
            return
            
        # الحصول على الصعوبة المحددة
        difficulty_text = self.diff_combo.currentText()
        if "Hard" in difficulty_text:
            difficulty = "Hard"
        elif "Medium" in difficulty_text:
            difficulty = "Medium"
        else:
            difficulty = "Easy"
            
        # البحث عن الحركة الأفضل
        best_move, score = find_best_move(self.game, self.ai_player, self.human_player, difficulty)
        
        if best_move is not None:
            # تنفيذ الحركة للكمبيوتر
            self.game.make_move(best_move, self.ai_player)
            self.update_board_ui()
            
            # تحديث لوحة التحليل التشخيصية (Diagnostics)
            self.update_diagnostics_ui(best_move, score, difficulty)
            
            # التحقق من الفوز/التعادل بعد حركة الكمبيوتر
            winner = self.game.check_winner()
            if winner:
                self.handle_game_over(winner)
                return
                
            # إعادة الدور للمستخدم
            self.current_turn = self.human_player
            self.status_label.setText("دورك يا ريس! العب بـ X")
            self.status_label.setStyleSheet("color: #8b949e;")

    def update_board_ui(self):
        """تحديث اللوحة الرسومية بناءً على مصفوفة اللعبة في game_logic"""
        for i in range(9):
            val = self.game.board[i]
            self.buttons[i].setText(val)
            
            # تنسيق ملون مختلف لكل لاعب
            if val == 'X':
                self.buttons[i].setStyleSheet("""
                    QPushButton {
                        background-color: #151b26;
                        border: 2px solid #00f0ff; /* إطار أزرق نيوني */
                        border-radius: 15px;
                        color: #00f0ff; /* خط سماوي نيوني */
                    }
                """)
            elif val == 'O':
                self.buttons[i].setStyleSheet("""
                    QPushButton {
                        background-color: #151b26;
                        border: 2px solid #ff5e62; /* إطار أحمر/وردي نيوني */
                        border-radius: 15px;
                        color: #ff5e62; /* خط أحمر/وردي نيوني */
                    }
                """)
            else:
                # مربع فارغ
                self.buttons[i].setStyleSheet("""
                    QPushButton {
                        background-color: #151b26;
                        border: 2px solid #2d3d5a;
                        border-radius: 15px;
                        color: #ffffff;
                    }
                    QPushButton:hover {
                        background-color: #1f2a3d;
                        border: 2px solid #00f0ff;
                    }
                """)

    def update_diagnostics_ui(self, move, score, difficulty):
        """تحديث واجهة التشخيص والتحليل لعرض تفاصيل تفكير الخوارزمية للمعيد"""
        # 1. تحديث عدد الحالات المستكشفة (States Explored)
        self.states_val.setText(f"{game_logic.states_explored:,} حالة")
        
        # 2. تحديث التقييم الرياضي للحركة (Score Evaluation)
        if difficulty == "Easy":
            self.score_val.setText("غير مفعل (حركة عشوائية)")
            self.score_val.setStyleSheet("color: #8b949e; background-color: #151b26; padding: 6px; border-radius: 6px;")
            self.expl_val.setText("في المستوى السهل، لا تفكر الخوارزمية للمستقبل وإنما تختار مربعاً فارغاً بشكل عشوائي تماماً لتسهيل اللعبة على المستخدم.")
            return
            
        score_text = ""
        score_style = ""
        explanation_text = ""
        
        if score == 1:
            score_text = "+1 (فوز مؤكد للكمبيوتر MAX)"
            score_style = "color: #4ade80; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #4ade80;" # أخضر
        elif score == -1:
            score_text = "-1 (فوز مؤكد للمستخدم MIN)"
            score_style = "color: #f87171; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #f87171;" # أحمر
        else:
            score_text = "0 (تعادل مضمون بفرض اللعب المثالي)"
            score_style = "color: #fbbf24; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #fbbf24;" # أصفر/ذهبي
            
        self.score_val.setText(score_text)
        self.score_val.setStyleSheet(score_style)
        
        # 3. صياغة التفسير الذكي للخطوة الحالية لتسهيل شرحها للمعيد
        move_name = f"المربع رقم {move + 1}"
        
        if difficulty == "Medium":
            explanation_text = f"بما أن الصعوبة 'متوسطة' (Heuristic Mode)، قمت بالبحث لمستويين فقط (Depth Limit = 2) لتجنب الانفجار التجميعي (Combinatorial Explosion). قمت باختيار {move_name} كأفضل حركة تقديرية حالياً."
        else:
            # الصعوبة القصوى: فحص كامل
            if score == 0:
                explanation_text = f"قمت باستكشاف جميع السيناريوهات الممكنة ({game_logic.states_explored:,} احتمال). ووجدت أن اللعب في {move_name} هو الخيار الأمثل ليضمن لي التعادل على الأقل ويمنعك من تشكيل أي خطة فوز."
            elif score == 1:
                explanation_text = f"رائع! اكتشفت الخوارزمية ثغرة في طريقة لعبك وحللت {game_logic.states_explored:,} احتمال للوصول لخطوة الفوز المؤكد. تم اللعب في {move_name} لإتمام مسار الفوز بنجاح."
            else:
                explanation_text = f"الخوارزمية في ورطة! بفرض أنك ستلعب بذكاء مثالي، تتوقع الخوارزمية فوزك بالخسارة (-1)، وتم اللعب في {move_name} لمحاولة إطالة أمد المباراة قدر الإمكان."
                
        self.expl_val.setText(explanation_text)

    def handle_game_over(self, winner):
        """معالجة نهاية المباراة وتحديد الفائز"""
        self.is_game_over = True
        
        # تعطيل جميع أزرار اللوحة
        for btn in self.buttons:
            btn.setCursor(Qt.CursorShape.ArrowCursor)
            
        if winner == "Tie":
            self.status_label.setText("ايش استفدت🙉")
            self.status_label.setStyleSheet("color: #fbbf24; font-weight: bold; font-size: 18px;")
            self.expl_val.setText("انتهت المباراة بالتعادل المضمون. هذا ما يحدث دائماً عندما يلعب طرفان بذكاء مثالي كامل في لعبة Tic-Tac-Toe!")
        else:
            if winner == self.human_player:
                self.status_label.setText("برافوو علييك 😂")
                self.status_label.setStyleSheet("color: #4ade80; font-weight: bold; font-size: 18px;")
                self.expl_val.setText("رائع! لقد فزت! (ملاحظة: لا يمكنك الفوز على مستوى الصعب أبداً، جرب مستويات السهل والمتوسط لتلاحظ الفرق!)")
            else:
                self.status_label.setText("طيب يا سيدي شكرا كفاية🙄")
                self.status_label.setStyleSheet("color: #f87171; font-weight: bold; font-size: 18px;")
                self.expl_val.setText("الكمبيوتر هو الفائز! خوارزمية Minimax تفوقت من خلال استكشاف شجرة اللعبة والبحث عن مسار الفوز المؤكد بدون أي أخطاء.")

    def reset_game(self):
        """إعادة تهيئة اللعبة وبدء مباراة جديدة"""
        self.game.reset()
        self.is_game_over = False
        
        # تفريغ أزرار اللوحة وإعادة استعادة المؤشرات
        for btn in self.buttons:
            btn.setText("")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.update_board_ui()
        
        # استعادة قيم لوحة التشخيص والتحليل
        self.states_val.setText("0 حالة")
        self.score_val.setText("بانتظار بدء اللعب")
        self.score_val.setStyleSheet("color: #8b949e; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #2d3d5a;")
        self.expl_val.setText("بانتظار حركتك الأولى للبدء في التحليل...")
        
        # تحديد من يبدأ
        starting_option = self.start_combo.currentText()
        if "المستخدم" in starting_option:
            self.current_turn = self.human_player
            self.status_label.setText("دورك الآن! العب بـ X")
            self.status_label.setStyleSheet("color: #8b949e;")
        else:
            self.current_turn = self.ai_player
            self.status_label.setText("الكمبيوتر يفكر الآن... 🧠")
            self.status_label.setStyleSheet("color: #ff5e62;")
            # بدء دور الكمبيوتر بتأخير بسيط
            QTimer.singleShot(400, self.ai_turn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تحديد اتجاه التطبيق من اليمين إلى اليسار ليتناسب مع اللغة العربية والإنجليزية بشكل أنيق
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    gui = TicTacToeGUI()
    gui.show()
    sys.exit(app.exec())
