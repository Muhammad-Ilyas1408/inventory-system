"""Reusable menu helpers for the command-line interface."""

from collections.abc import Callable


def display_menu(title: str, options: list[tuple[str, str]]) -> None:
    """Display a formatted menu.

    Args:
        title: Heading displayed above the menu options.
        options: Menu option identifiers and descriptions.
    """
    print("\n" + "=" * 41)
    print(title)
    print("=" * 41)
    for option, description in options:
        print(f"{option}. {description}")


def get_selection(
    valid_options: set[str],
    prompt: str = "Select an option: ",
) -> str | None:
    """Read and validate a menu selection.

    Args:
        valid_options: Permitted selection values.
        prompt: Text displayed when requesting the selection.

    Returns:
        The validated selection, or None when the input is invalid.
    """
    selection = input(prompt).strip()
    if selection not in valid_options:
        print("Invalid selection. Please choose a listed option.")
        return None
    return selection


def run_action(action: Callable[[], None]) -> None:
    """Run a CLI action and display user-friendly errors.

    Args:
        action: User-initiated operation to execute.
    """
    try:
        action()
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")
    except Exception:
        print("An unexpected error occurred. Please try again.")
