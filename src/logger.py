import logging
import os
import sys

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = os.path.join(os.getcwd(), "logfile.log")


class Logger:
    """
    Class for logging behaviour of data exporting - ExportingTool class object
    """

    def __init__(self,
                 show: bool,
                 filename: str = LOG_FILE,
                 level: int = logging.DEBUG) -> None:
        """
        Arguments:
        ----------
        show : bool
            If True logs will be shown in terminal.
            Logs will be saved in logfile.log anyway.
        """
        self.show = show
        self.filename = filename
        self.level = level

    def get_console_handler(self) -> logging.StreamHandler:
        """
        Gets a console handler to show logs on terminal

        Returns:
        --------
        logging.StreamHandler:
            Handler object for streaming output through terminal
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        return console_handler

    def get_file_handler(self) -> logging.FileHandler:
        """
        Gets a file handler to write logs in file LOG_FILE

        Returns:
            logging.FileHandler: handler object for streaming output
                through std::filestream
        """
        file_handler = logging.FileHandler(self.filename, mode='w')
        file_handler.setFormatter(FORMATTER)
        return file_handler

    def get_logger(self, logger_name: str) -> logging.Logger:
        """
        Class method which creates logger with certain name

        Args:
        -----
        logger_name : str
            Name for logger

        Returns:
        --------
        logger:
            Object of Logger class
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.level)
        if self.show:
            logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())
        logger.propagate = False
        return logger