from loguru import logger
import sys
from pathlib import Path

logs_dir_parent = Path(__file__).parent.parent

logs_dir = logs_dir_parent / "logs"


def setup_logging(
    logs_dir=logs_dir, level="INFO", enable_console=True, enable_json=False
):
    Path(logs_dir).mkdir(exist_ok=True)

    logger.remove()

    if enable_console:
        logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
                "| <level>{level: <8}</level> "
                "| <cyan>{name}:{function}:{line}</cyan> "
                "- <level>{message}</level>"
            ),
            colorize=True,
        )

    if enable_json:
        logger.add(
            f"{logs_dir}/app.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
        )
    else:
        logger.add(
            f"{logs_dir}/app.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="5 MB",
            retention="90 days",
            backtrace=True,
            diagnose=True,
        )

    logger.add(
        f"{logs_dir}/errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="5 MB",
        retention="90 days",
        backtrace=True,
        diagnose=True,
    )

    logger.info(f"Logging initialized at level {level}")


if __name__ == "__main__":
    setup_logging(level="DEBUG")
