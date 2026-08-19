"""
Vitality Check-in — offline-first member verification for hospitality suite access.

Run with:
    python main.py

Premium minimalist kiosk interface:
  - Responsive layout for laptops and tablets.
  - ID/passport verification with Enter or Verify.
  - Granted screen shows member name and tier.
  - Denied screen shows a clear failure state.
  - Excel import, member count, recent check-ins, export and sync stub retained.
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QDialog,
    QMenu,
)

import db
import excel_import


# ---------------------------------------------------------------------------
# Premium minimalist theme
# ---------------------------------------------------------------------------

BG = "#F7F6F2"
SURFACE = "#FFFFFF"
TEXT = "#1C1B1A"
SECONDARY = "#6E6A64"
MUTED = "#A39E96"
BORDER = "#E2DED6"

# Vitality pink — closest match to Discovery's brand pink. Not sourced from
# an official brand guideline PDF, so eyedropper the real app/site if this
# needs to be pixel-exact.
ACCENT = "#E6007E"
ACCENT_HOVER = "#C40069"
ACCENT_PRESSED = "#A3005A"
ACCENT_TINT = "#FDEAF3"

BUTTON = ACCENT
BUTTON_HOVER = ACCENT_HOVER
BUTTON_PRESSED = ACCENT_PRESSED

GRANTED = "#1E6B4E"
DENIED = "#B84A4A"

FLASH_MS = 3000


class VitalityCheckinWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vitality Hospitality Verification")
        self.resize(1000, 680)
        self.setMinimumSize(620, 520)

        db.init_db()

        self._build_ui()
        self.refresh_status()
        self.refresh_table()
        self.id_input.setFocus()

    # -----------------------------------------------------------------------
    # Main UI
    # -----------------------------------------------------------------------

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        root.setStyleSheet(f"""
            QWidget#root {{
                background: {BG};
            }}
        """)
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(42, 30, 42, 30)
        outer.setSpacing(0)

        # Top navigation
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        brand = QLabel(
            f'<span style="color:{ACCENT};">V</span>ITALITY'
        )
        brand.setTextFormat(Qt.RichText)
        brand_font = QFont("Segoe UI")
        brand_font.setPointSize(11)
        brand_font.setBold(True)
        brand.setFont(brand_font)
        brand.setStyleSheet(
            f"color: {TEXT}; letter-spacing: 3px; background: transparent;"
        )

        top.addWidget(brand)
        top.addStretch(1)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_label.setStyleSheet(
            f"color: {MUTED}; font-size: 9px; background: transparent;"
        )
        top.addWidget(self.status_label)
        top.addSpacing(18)

        self.menu_btn = QPushButton("Menu")
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setFixedHeight(38)
        self.menu_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.92);
                color: {TEXT};
                border: 1px solid rgba(23, 23, 23, 0.10);
                border-radius: 19px;
                padding: 0 17px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #FFFFFF;
                border: 1px solid rgba(23, 23, 23, 0.18);
            }}
            QPushButton:pressed {{
                background: #ECEAE6;
            }}
        """)
        self.menu_btn.clicked.connect(self.show_menu)
        top.addWidget(self.menu_btn)

        outer.addLayout(top)

        # Centre verification area
        outer.addStretch(1)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignHCenter)
        center.setSpacing(0)

        eyebrow = QLabel("MEMBER ACCESS")
        eyebrow.setAlignment(Qt.AlignCenter)
        eyebrow_font = QFont("Segoe UI")
        eyebrow_font.setPointSize(10)
        eyebrow_font.setBold(True)
        eyebrow.setFont(eyebrow_font)
        eyebrow.setStyleSheet(
            f"color: {SECONDARY}; letter-spacing: 2.5px; background: transparent;"
        )
        center.addWidget(eyebrow)

        center.addSpacing(8)

        eyebrow_line = QFrame()
        eyebrow_line.setFixedSize(28, 2)
        eyebrow_line.setStyleSheet(
            f"background: {ACCENT}; border-radius: 1px;"
        )
        center.addWidget(eyebrow_line, 0, Qt.AlignHCenter)

        center.addSpacing(11)

        title = QLabel("Welcome")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI")
        title_font.setPointSize(34)
        title_font.setWeight(QFont.Weight.Normal)
        title.setFont(title_font)
        title.setStyleSheet(
            f"color: {TEXT}; background: transparent;"
        )
        center.addWidget(title)

        center.addSpacing(9)

        subtitle = QLabel(
            "Enter your ID or passport number to verify access."
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {SECONDARY}; font-size: 12px; background: transparent;"
        )
        center.addWidget(subtitle)

        center.addSpacing(28)

        self.id_input = QLineEdit()
        self.id_input.setObjectName("idInput")
        self.id_input.setPlaceholderText("ID or passport number")
        self.id_input.setAlignment(Qt.AlignCenter)
        self.id_input.setMinimumHeight(60)
        self.id_input.setMaximumWidth(520)
        self.id_input.setFont(QFont("Segoe UI", 16))
        self.id_input.setStyleSheet(f"""
            QLineEdit#idInput {{
                background: {SURFACE};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 13px;
                padding: 0 18px;
                selection-background-color: #DAD7D1;
                selection-color: {TEXT};
            }}
            QLineEdit#idInput:focus {{
                border: 1.5px solid {ACCENT};
                background: #FFFFFF;
            }}
            QLineEdit#idInput::placeholder {{
                color: {MUTED};
            }}
        """)
        self.id_input.returnPressed.connect(self.on_verify)
        center.addWidget(self.id_input, 0, Qt.AlignHCenter)

        center.addSpacing(14)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setCursor(Qt.PointingHandCursor)
        self.verify_btn.setMinimumHeight(50)
        self.verify_btn.setMaximumWidth(190)
        verify_font = QFont("Segoe UI")
        verify_font.setPointSize(12)
        verify_font.setBold(True)
        self.verify_btn.setFont(verify_font)
        self.verify_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BUTTON};
                color: #FFFFFF;
                border: none;
                border-radius: 25px;
                padding: 0 28px;
            }}
            QPushButton:hover {{
                background: {BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background: {BUTTON_PRESSED};
            }}
            QPushButton:disabled {{
                background: #8A8884;
                color: #E8E6E2;
            }}
        """)
        self.verify_btn.clicked.connect(self.on_verify)
        center.addWidget(self.verify_btn, 0, Qt.AlignHCenter)

        center.addSpacing(19)

        instruction = QLabel("Press Enter to verify")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet(
            f"color: {MUTED}; font-size: 9px; background: transparent;"
        )
        center.addWidget(instruction)

        center.addSpacing(22)

        tagline = QLabel("Every healthy step counts.")
        tagline.setAlignment(Qt.AlignCenter)
        tagline_font = QFont("Segoe UI")
        tagline_font.setItalic(True)
        tagline_font.setPointSize(9)
        tagline.setFont(tagline_font)
        tagline.setStyleSheet(
            f"color: {MUTED}; background: transparent;"
        )
        center.addWidget(tagline)

        outer.addLayout(center)
        outer.addStretch(1)

        footer = QHBoxLayout()
        footer_label = QLabel("VITALITY  •  MEMBER SERVICES")
        footer_label.setStyleSheet(
            f"color: {MUTED}; font-size: 8px; font-weight: 600; "
            f"letter-spacing: 1.5px; background: transparent;"
        )
        footer.addWidget(footer_label)
        footer.addStretch(1)

        self.members_footer = QLabel()
        self.members_footer.setAlignment(Qt.AlignRight)
        self.members_footer.setStyleSheet(
            f"color: {MUTED}; font-size: 8px; background: transparent;"
        )
        footer.addWidget(self.members_footer)

        outer.addLayout(footer)

        # Result overlay is kept as a separate full-window layer.
        self.overlay = QWidget(root)
        self.overlay.hide()

        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(40, 40, 40, 40)
        overlay_layout.addStretch(1)

        self.result_icon = QLabel("\u2713")
        self.result_icon.setAlignment(Qt.AlignCenter)
        self.result_icon.setFixedSize(56, 56)
        icon_font = QFont("Segoe UI")
        icon_font.setPointSize(22)
        self.result_icon.setFont(icon_font)
        self.result_icon.setStyleSheet("""
            color: white;
            background: transparent;
            border: 1.5px solid rgba(255,255,255,0.85);
            border-radius: 28px;
        """)
        overlay_layout.addWidget(self.result_icon, 0, Qt.AlignHCenter)
        overlay_layout.addSpacing(14)
        self.result_icon.hide()

        self.result_title = QLabel()
        self.result_title.setAlignment(Qt.AlignCenter)
        result_font = QFont("Segoe UI")
        result_font.setPointSize(34)
        result_font.setWeight(QFont.Weight.Normal)
        self.result_title.setFont(result_font)
        self.result_title.setStyleSheet(
            "color: white; background: transparent;"
        )
        overlay_layout.addWidget(self.result_title)

        self.result_name = QLabel()
        self.result_name.setAlignment(Qt.AlignCenter)
        name_font = QFont("Segoe UI")
        name_font.setPointSize(22)
        name_font.setWeight(QFont.Weight.DemiBold)
        self.result_name.setFont(name_font)
        self.result_name.setStyleSheet(
            "color: white; background: transparent;"
        )
        overlay_layout.addWidget(self.result_name)

        self.result_detail = QLabel()
        self.result_detail.setAlignment(Qt.AlignCenter)
        detail_font = QFont("Segoe UI")
        detail_font.setPointSize(12)
        self.result_detail.setFont(detail_font)
        self.result_detail.setStyleSheet(
            "color: rgba(255,255,255,0.85); background: transparent;"
        )
        overlay_layout.addWidget(self.result_detail, 0, Qt.AlignHCenter)

        overlay_layout.addStretch(1)

        # Give the overlay priority when visible.
        self.overlay.raise_()

    # -----------------------------------------------------------------------
    # Menu
    # -----------------------------------------------------------------------

    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: #FFFFFF;
                border: 1px solid {BORDER};
                padding: 7px;
            }}
            QMenu::item {{
                color: {TEXT};
                padding: 9px 18px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background: #F1EFEB;
                color: {TEXT};
            }}
            QMenu::separator {{
                height: 1px;
                background: #ECE9E4;
                margin: 6px 8px;
            }}
        """)

        menu.addAction("Load member list (Excel)...", self.on_load_excel)
        menu.addSeparator()
        menu.addAction("View recent check-ins...", self.on_view_log)
        menu.addAction("Export check-in log...", self.on_export_log)
        menu.addSeparator()
        menu.addAction("Sync now", self.on_sync_stub)

        menu.exec(
            self.menu_btn.mapToGlobal(
                self.menu_btn.rect().bottomLeft()
            )
        )

    # -----------------------------------------------------------------------
    # Excel import
    # -----------------------------------------------------------------------

    def on_load_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select member list",
            "",
            "Excel files (*.xlsx *.xls)"
        )

        if not path:
            return

        try:
            columns = excel_import.read_excel_columns(path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Could not read file",
                str(e)
            )
            return

        dialog = excel_import.ColumnMapDialog(columns, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        mapping = dialog.mapping()

        if not mapping["id_number"]:
            QMessageBox.warning(
                self,
                "Missing column",
                "You must select an ID number column."
            )
            return

        try:
            rows = excel_import.load_rows(path, mapping)
            count = db.replace_members(rows)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import failed",
                str(e)
            )
            return

        self.refresh_status()

        QMessageBox.information(
            self,
            "Import complete",
            f"Loaded {count:,} members."
        )

    def refresh_status(self):
        count = db.member_count()
        last = db.last_import_time() or "never"

        self.status_label.setText(
            f"{count:,} members  •  Last import: {last}"
        )

        self.members_footer.setText(
            f"{count:,} members loaded"
        )

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    def on_verify(self):
        raw_id = self.id_input.text().strip()

        if not raw_id:
            return

        self.id_input.setEnabled(False)
        self.verify_btn.setEnabled(False)

        member = db.lookup_member(raw_id)

        if member:
            name = (member["full_name"] or "Member").strip()

            db.log_checkin(
                raw_id,
                name,
                "granted"
            )

            self.show_granted(name)

        else:
            db.log_checkin(
                raw_id,
                "",
                "denied"
            )

            self.show_denied()

        self.refresh_table()

    def show_granted(self, name: str):
        self.overlay.setStyleSheet(
            f"background-color: {GRANTED};"
        )

        self.result_title.setText("ACCESS GRANTED")
        self.result_name.setText(name)

        self.result_detail.setText("Membership verified")
        self.result_detail.setStyleSheet(
            "color: rgba(255,255,255,0.85); background: transparent;"
        )

        self.result_icon.show()
        self.result_name.show()
        self.result_detail.show()

        self.overlay.show()
        self.overlay.raise_()

        QTimer.singleShot(
            FLASH_MS,
            self._reset_after_result
        )

    def show_denied(self):
        self.overlay.setStyleSheet(
            f"background-color: {DENIED};"
        )

        self.result_title.setText("ACCESS DENIED")
        self.result_name.setText("")

        self.result_icon.hide()
        self.result_detail.setStyleSheet(
            "color: rgba(255,255,255,0.85); background: transparent;"
        )
        self.result_detail.setText(
            "ID or passport number not found"
        )

        self.result_name.hide()
        self.result_detail.show()

        self.overlay.show()
        self.overlay.raise_()

        QTimer.singleShot(
            FLASH_MS,
            self._reset_after_result
        )

    def _reset_after_result(self):
        self.overlay.hide()

        self.id_input.clear()
        self.id_input.setEnabled(True)
        self.verify_btn.setEnabled(True)
        self.id_input.setFocus()

    # -----------------------------------------------------------------------
    # Recent check-ins / export
    # -----------------------------------------------------------------------

    def refresh_table(self):
        rows = db.recent_checkins(50)

        # Table is used by the menu dialog rather than the main screen.
        self._recent_rows = rows

    def on_view_log(self):
        rows = db.recent_checkins(100)

        dlg = QDialog(self)
        dlg.setWindowTitle("Recent check-ins")
        dlg.resize(720, 460)

        dlg.setStyleSheet(f"""
            QDialog {{
                background: {BG};
            }}
            QTableWidget {{
                background: #FFFFFF;
                color: {TEXT};
                border: 1px solid {BORDER};
                gridline-color: #ECE9E4;
                selection-background-color: #ECE9E4;
                selection-color: {TEXT};
            }}
            QHeaderView::section {{
                background: #F1EFEB;
                color: {TEXT};
                border: none;
                padding: 8px;
                font-weight: 600;
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 24)

        heading = QLabel("Recent check-ins")
        heading.setStyleSheet(
            f"color: {TEXT}; font-size: 20px; background: transparent;"
        )
        layout.addWidget(heading)
        layout.addSpacing(10)

        table = QTableWidget(len(rows), 4)
        table.setHorizontalHeaderLabels(
            ["Time", "ID number", "Name", "Result"]
        )
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for i, row in enumerate(rows):
            table.setItem(
                i, 0, QTableWidgetItem(row["timestamp"])
            )
            table.setItem(
                i, 1, QTableWidgetItem(row["id_number"])
            )
            table.setItem(
                i, 2, QTableWidgetItem(row["full_name"])
            )
            table.setItem(
                i, 3, QTableWidgetItem(row["result"])
            )

        layout.addWidget(table)

        dlg.exec()

    def on_export_log(self):
        import pandas as pd

        rows = db.all_checkins()

        if not rows:
            QMessageBox.information(
                self,
                "Nothing to export",
                "No check-ins logged yet."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save check-in log",
            "checkin_log.xlsx",
            "Excel files (*.xlsx)"
        )

        if not path:
            return

        df = pd.DataFrame(
            [
                dict(
                    id_number=r["id_number"],
                    full_name=r["full_name"],
                    result=r["result"],
                    timestamp=r["timestamp"]
                )
                for r in rows
            ]
        )

        df.to_excel(path, index=False)

        QMessageBox.information(
            self,
            "Exported",
            f"Saved {len(df):,} rows to {path}"
        )

    # -----------------------------------------------------------------------
    # Sync stub
    # -----------------------------------------------------------------------

    def on_sync_stub(self):
        QMessageBox.information(
            self,
            "Sync",
            "No sync endpoint configured yet.\n\n"
            "This button is a placeholder for pulling a fresh member list "
            "and pushing the check-in log once an approved connection is set up."
        )

    # -----------------------------------------------------------------------
    # Keyboard / responsive behaviour
    # -----------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            return

        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
            return

        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Keep the result overlay exactly over the full central widget.
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(
                self.centralWidget().rect()
            )


def main():
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = VitalityCheckinWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()