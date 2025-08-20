from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex
from typing import Dict, List, Any, Optional

class MultiColumnMultiValueFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: Optional[Any] = None):
        super().__init__(parent)
        self.column_filters: Dict[int, List[str]] = {}  # {column_index: [values, ...]}

    def setColumnFilter(self, column: int, text: str) -> None:
        values: List[str] = [v.strip().lower() for v in text.split(",") if v.strip()]
        if values:
            self.column_filters[column] = values
        else:
            self.column_filters.pop(column, None)
        self.invalidateFilter()

    def clearAllFilters(self) -> None:
        self.column_filters.clear()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        for col, values in self.column_filters.items():
            data: str = str(model.index(source_row, col, source_parent).data()).lower()
            if not any(val in data for val in values):
                return False
        return True
