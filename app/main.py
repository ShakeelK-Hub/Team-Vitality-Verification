"""
Vitality Check-in — offline-first member verification for hospitality suite access.

Run with:  python main.py

Kiosk-style flow:
  1. One box: type or scan an ID / passport number, press Enter or click Verify.
  2. Screen fills green (granted) or red (denied) for 3 seconds, then resets.
  3. Everything else (loading the Excel sheet, exporting the log, setting a
     background image) lives behind the small "Menu" button in the corner,
     so the main screen stays down to just the input and the result.

No internet connection is required for verifying or logging — see db.py.
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QKeyEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QGridLayout, QMenu, QDialog, QTableWidget, QTableWidgetItem
)

import db
import excel_import

DEFAULT_BG_COLOR = "#D4537E"   # Team Vitality pink placeholder
GRANTED_COLOR = "#1F9E5C"
DENIED_COLOR = "#C0392B"
FLASH_MS = 3000


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vitality Check-in")
        self.resize(1000, 650)
        db.init_db()

        central = QWidget()
        self.setCentralWidget(central)
        self.grid = QGridLayout(central)
        self.grid.setContentsMargins(0, 0, 0, 0)

        # --- Background layer ---
        self.bg_label = QLabel()
        self.bg_label.setScaledContents(True)
        self.grid.addWidget(self.bg_label, 0, 0)
        self._bg_pixmap = None

        # --- Foreground content (transparent, sits above background) ---
        self.content = QWidget()
        self.content.setAttribute(Qt.WA_StyledBackground, True)
        self.content.setStyleSheet("background: transparent;")
        self.grid.addWidget(self.content, 0, 0)
        self._build_content()

        # --- Result overlay (green / red flash, sits above everything) ---
        self.overlay = QWidget()
        self.overlay.hide()
        self.grid.addWidget(self.overlay, 0, 0)
        self._build_overlay()

        self.bg_label.lower()
        self.content.raise_()
        self.overlay.raise_()

        self._load_saved_background()

    # ---------- Layout ----------

    def _build_content(self):
        outer = QVBoxLayout(self.content)

        top_row = QHBoxLayout()
        top_row.addStretch(1)
        self.menu_btn = QPushButton("Menu")
        self.menu_btn.setStyleSheet(
            "background: rgba(255,255,255,0.75); border-radius: 6px; padding: 6px 14px;"
        )
        self.menu_btn.clicked.connect(self.show_menu)
        top_row.addWidget(self.menu_btn)
        outer.addLayout(top_row)

        outer.addStretch(1)

        center_box = QVBoxLayout()
        center_box.setSpacing(16)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter ID or passport number")
        self.id_input.setAlignment(Qt.AlignCenter)
        self.id_input.setFixedWidth(480)
        self.id_input.setFixedHeight(56)
        input_font = QFont()
        input_font.setPointSize(18)
        self.id_input.setFont(input_font)
        self.id_input.setStyleSheet(
            "background: white; border-radius: 8px; padding: 0 12px;"
        )
        self.id_input.returnPressed.connect(self.on_verify)
        center_box.addWidget(self.id_input, 0, Qt.AlignHCenter)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setFixedWidth(200)
        self.verify_btn.setFixedHeight(52)
        btn_font = QFont()
        btn_font.setPointSize(14)
        btn_font.setBold(True)
        self.verify_btn.setFont(btn_font)
        self.verify_btn.setStyleSheet(
            "background: #0B0B0B; color: white; border-radius: 8px;"
        )
        self.verify_btn.clicked.connect(self.on_verify)
        center_box.addWidget(self.verify_btn, 0, Qt.AlignHCenter)

        outer.addLayout(center_box)
        outer.addStretch(1)

        self.id_input.setFocus()

    def _build_overlay(self):
        layout = QVBoxLayout(self.overlay)
        self.overlay_label = QLabel("")
        self.overlay_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.overlay_label.setFont(font)
        self.overlay_label.setStyleSheet("color: white;")
        layout.addWidget(self.overlay_label)

    # ---------- Background ----------

    def _apply_color_background(self, hex_color: str):
        self._bg_pixmap = None
        self.bg_label.setPixmap(QPixmap())
        self.bg_label.setStyleSheet(f"background-color: {hex_color};")
        db.set_meta("bg_type", "color")
        db.set_meta("bg_value", hex_color)

    def _apply_image_background(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Could not load image", f"'{path}' isn't a valid image.")
            return
        self._bg_pixmap = pixmap
        self.bg_label.setStyleSheet("")
        self.bg_label.setPixmap(pixmap)
        db.set_meta("bg_type", "image")
        db.set_meta("bg_value", path)

    def _load_saved_background(self):
        bg_type = db.get_meta("bg_type")
        bg_value = db.get_meta("bg_value")
        if bg_type == "image" and bg_value:
            self._apply_image_background(bg_value)
        else:
            self._apply_color_background(bg_value or DEFAULT_BG_COLOR)

    # ---------- Menu (Load Excel / background / export) ----------

    def show_menu(self):
        menu = QMenu(self)
        menu.addAction("Load member list (Excel)...", self.on_load_excel)
        menu.addSeparator()
        menu.addAction("Set background image...", self.on_set_bg_image)
        menu.addAction("Reset background to pink", lambda: self._apply_color_background(DEFAULT_BG_COLOR))
        menu.addSeparator()
        menu.addAction("View recent check-ins...", self.on_view_log)
        menu.addAction("Export check-in log...", self.on_export_log)
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def on_load_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select member list", "", "Excel files (*.xlsx *.xls)"
        )
        if not path:
            return
        try:
            columns = excel_import.read_excel_columns(path)
        except Exception as e:
            QMessageBox.critical(self, "Could not read file", str(e))
            return

        dialog = excel_import.ColumnMapDialog(columns, self)
        if dialog.exec() != dialog.Accepted:
            return
        mapping = dialog.mapping()
        if not mapping["id_number"]:
            QMessageBox.warning(self, "Missing column", "You must select an ID number column.")
            return

        try:
            rows = excel_import.load_rows(path, mapping)
            count = db.replace_members(rows)
        except Exception as e:
            QMessageBox.critical(self, "Import failed", str(e))
            return

        QMessageBox.information(self, "Import complete", f"Loaded {count} members.")

    def on_set_bg_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select background image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self._apply_image_background(path)

    def on_view_log(self):
        rows = db.recent_checkins(100)
        dlg = QDialog(self)
        dlg.setWindowTitle("Recent check-ins")
        dlg.resize(600, 400)
        layout = QVBoxLayout(dlg)
        table = QTableWidget(len(rows), 4)
        table.setHorizontalHeaderLabels(["Time", "ID number", "Name", "Result"])
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i, row in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(row["timestamp"]))
            table.setItem(i, 1, QTableWidgetItem(row["id_number"]))
            table.setItem(i, 2, QTableWidgetItem(row["full_name"]))
            table.setItem(i, 3, QTableWidgetItem(row["result"]))
        layout.addWidget(table)
        dlg.exec()

    def on_export_log(self):
        import pandas as pd

        rows = db.all_checkins()
        if not rows:
            QMessageBox.information(self, "Nothing to export", "No check-ins logged yet.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save check-in log", "checkin_log.xlsx", "Excel files (*.xlsx)"
        )
        if not path:
            return
        df = pd.DataFrame(
            [dict(id_number=r["id_number"], full_name=r["full_name"],
                  result=r["result"], timestamp=r["timestamp"]) for r in rows]
        )
        df.to_excel(path, index=False)
        QMessageBox.information(self, "Exported", f"Saved {len(df)} rows to {path}")

    # ---------- Verification ----------

    def on_verify(self):
        raw_id = self.id_input.text().strip()
        if not raw_id:
            return
        self.id_input.setEnabled(False)
        self.verify_btn.setEnabled(False)

        member = db.lookup_member(raw_id)
        if member:
            db.log_checkin(raw_id, member["full_name"], "granted")
            self._flash(GRANTED_COLOR, "ACCESS GRANTED")
        else:
            db.log_checkin(raw_id, "", "denied")
            self._flash(DENIED_COLOR, "ACCESS DENIED")

    def _flash(self, hex_color: str, text: str):
        self.overlay.setStyleSheet(f"background-color: {hex_color};")
        self.overlay_label.setText(text)
        self.overlay.show()
        self.overlay.raise_()
        QTimer.singleShot(FLASH_MS, self._reset_after_flash)

    def _reset_after_flash(self):
        self.overlay.hide()
        self.id_input.clear()
        self.id_input.setEnabled(True)
        self.verify_btn.setEnabled(True)
        self.id_input.setFocus()

    # ---------- Kiosk fullscreen toggle ----------

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()
        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep the background label filling the window on resize
        self.bg_label.resize(self.centralWidget().size())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()