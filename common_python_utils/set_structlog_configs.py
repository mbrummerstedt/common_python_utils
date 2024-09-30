
import os
import inspect
from google.cloud import logging as cloud_logging
import structlog
import logging
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger
import structlog_gcp



# Custom processor to append the calling function's name to the log entry for structlog
def append_calling_function_name_to_log(logger, log_method, event_dict):
    frame = inspect.currentframe().f_back.f_back  # Adjust according to the call stack depth
    while frame and (
        "structlog" in frame.f_code.co_filename or
        frame.f_code.co_name in ["<module>", "append_calling_function_name_to_log"]
    ):
        frame = frame.f_back
    event_dict["function"] = frame.f_code.co_name if frame else "unknown"
    return event_dict

def append_script_name_to_log(logger, log_method, event_dict):
    """
    Adds the script name to the log entry in structlog.

    This function examines the call stack and finds the name of the script
    where the logger is being called. It then adds this script name to the
    event_dict under the key 'script'.

    Args:
        logger: The logger instance.
        log_method: The log method used.
        event_dict (dict): The event dictionary to which the script name will be added.

    Returns:
        dict: The updated event dictionary with the script name added.
    """
    frame = inspect.currentframe()

    # Traverse back to find the first frame outside of structlog and this function
    while frame is not None and (
        frame.f_code.co_name == "append_script_name_to_log"
        or "structlog" in frame.f_code.co_filename
    ):
        frame = frame.f_back

    if frame is not None:
        script_name = os.path.basename(frame.f_code.co_filename)
        event_dict["script"] = script_name
    else:
        event_dict["script"] = "unknown"

    return event_dict

def google_cloud_logging_formatter(logger, log_method, event_dict):
    # Ensure 'msg' is directly set as 'message' at the top level
    if 'msg' in event_dict:
        event_dict['message'] = event_dict.pop('msg')
    return event_dict


def configure_structlog_for_dev(name):
    processors = [
        append_script_name_to_log,
        append_calling_function_name_to_log,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S"),
        structlog.dev.ConsoleRenderer()
    ]
    # Configure standard logging to INFO level
    logging.basicConfig(level=logging.INFO)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )
    return structlog.get_logger(name)


def configure_structlog_for_prod(name):
    processors = [
        append_script_name_to_log,
        append_calling_function_name_to_log,
    ]
    gcp_processors = structlog_gcp.build_processors()
    processors.extend(gcp_processors)
    # Configure standard logging to INFO level
    logging.basicConfig(level=logging.INFO)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )
    return structlog.get_logger(name)



# Environment-based logger factory
def get_logger(name, env=None):
    # Load environment variables from .env file
    load_dotenv()
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not GOOGLE_CLOUD_PROJECT:
        print("Warning: GOOGLE_CLOUD_PROJECT environment variable is not set.")
    if env == 'prod':
        client = cloud_logging.Client(project=GOOGLE_CLOUD_PROJECT)
        client.setup_logging()
        handler = cloud_logging.handlers.CloudLoggingHandler(client)
        handler.setFormatter(jsonlogger.JsonFormatter())
        # Add handler to the root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        return configure_structlog_for_prod(name)
    else:
        # Ensure structlog is configured for non-prod environments
        return configure_structlog_for_dev(name)
