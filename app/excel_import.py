"""
Handles loading a member list from Excel. Since the real Discovery/Team
Vitality export's column headers aren't known in advance, the user maps
'ID number' and 'Name' columns the first time they load a new sheet.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox, QLabel
)


class ColumnMapDialog(QDialog):
    """Small dialog letting the user pick which spreadsheet columns hold
    the ID number, full name, and (optionally) membership tier."""

    def __init__(self, columns: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Match spreadsheet columns")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Tell the app which columns to use:"))

        form = QFormLayout()
        self.id_combo = QComboBox()
        self.name_combo = QComboBox()
        self.tier_combo = QComboBox()

        options = ["(none)"] + columns
        for combo in (self.id_combo, self.name_combo, self.tier_combo):
            combo.addItems(options)

        # Best-effort auto guess based on common header wording
        self._auto_select(self.id_combo, columns, ["id number", "id no", "idnumber", "id"])
        self._auto_select(self.name_combo, columns, ["full name", "name", "member name"])
        self._auto_select(self.tier_combo, columns, ["tier", "status", "membership"])

        form.addRow("ID number column:", self.id_combo)
        form.addRow("Name column:", self.name_combo)
        form.addRow("Tier / status column:", self.tier_combo)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _auto_select(combo: QComboBox, columns: list[str], guesses: list[str]) -> None:
        lowered = {c.lower(): c for c in columns}
        for guess in guesses:
            if guess in lowered:
                combo.setCurrentText(lowered[guess])
                return

    def mapping(self) -> dict:
        return {
            "id_number": None if self.id_combo.currentText() == "(none)" else self.id_combo.currentText(),
            "full_name": None if self.name_combo.currentText() == "(none)" else self.name_combo.currentText(),
            "tier": None if self.tier_combo.currentText() == "(none)" else self.tier_combo.currentText(),
        }


def read_excel_columns(path: str) -> list[str]:
    df = pd.read_excel(path, nrows=0)
    return list(df.columns)


def load_rows(path: str, mapping: dict) -> list[dict]:
    """Reads the full sheet and returns a list of plain dicts using the
    chosen column mapping, ready for db.replace_members()."""
    df = pd.read_excel(path)
    rows = []
    for _, r in df.iterrows():
        rows.append(
            {
                "id_number": str(r[mapping["id_number"]]).strip() if mapping["id_number"] else "",
                "full_name": str(r[mapping["full_name"]]).strip() if mapping["full_name"] else "",
                "tier": str(r[mapping["tier"]]).strip() if mapping["tier"] else "",
            }
        )
    return rows
