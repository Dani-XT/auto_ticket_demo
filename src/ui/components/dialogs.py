from src.ui.components.error_dialog import ErrorDialog


def show_error(parent, title: str, message: str):
    ErrorDialog(parent, title=title, message=message, level="error")


def show_warning(parent, title: str, message: str):
    ErrorDialog(parent, title=title, message=message, level="warning")


def show_info(parent, title: str, message: str):
    ErrorDialog(parent, title=title, message=message, level="info")