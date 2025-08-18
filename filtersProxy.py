from PyQt5.QtCore import QSortFilterProxyModel

class MultiColumnMultiValueFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.column_filters = {}  # {column_index: [values, ...]}

    def setColumnFilter(self, column, text):
        values = [v.strip().lower() for v in text.split(",") if v.strip()]
        if values:
            self.column_filters[column] = values
        else:
            self.column_filters.pop(column, None)
        self.invalidateFilter()

    def clearAllFilters(self):
        self.column_filters.clear()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        for col, values in self.column_filters.items():
            data = str(model.index(source_row, col, source_parent).data()).lower()
            if not any(val in data for val in values):
                return False
        return True