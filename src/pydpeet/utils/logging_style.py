import logging


def set_logging_style(level="WARNING", formatting_string="%(levelname)s | %(pathname)s:%(lineno)d | %(message)s"):
    """
    Sets up on import the logging configuration to use the specified level and a custom format.

    The logging configuration is set to use the specified level. The format of the
    messages is set to '<levelname> | <pathname>:<lineno> | <message>'.

    Parameters
    ----------
    level : int, optional
        The logging level to use. Defaults to logging.WARNING.
    formatting_string : str, optional
        The formatting string to use for the log messages. Defaults to
        '%(levelname)s | %(pathname)s:%(lineno)d | %(message)s'.

    Returns
    -------
    None
    """
    if isinstance(level, str):
        level = getattr(logging, level)
    logging.basicConfig(
        level=level,
        format=formatting_string,
        force=True
    )