"""
Logging configuration for the workflow system.
"""
import logging
import os
from pathlib import Path
from datetime import datetime
import colorlog


def setup_logging(log_level: str = None, log_file: str = None):
    """Configure logging with color output and file handler."""
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    if log_file is None:
        log_file = os.getenv("LOG_FILE", "./logs/workflow.log")
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


class WorkflowLogger:
    """Specialized logger for workflow execution tracking."""
    
    def __init__(self, workflow_name: str):
        self.logger = get_logger(f"workflow.{workflow_name}")
        self.start_time = datetime.now()
        self.step_times = {}
    
    def log_step_start(self, step_id: str, step_name: str):
        """Log the start of a workflow step."""
        self.step_times[step_id] = datetime.now()
        self.logger.info(f"[START] Starting step: {step_name} ({step_id})")
    
    def log_step_complete(self, step_id: str, step_name: str, output: dict = None):
        """Log the completion of a workflow step."""
        if step_id in self.step_times:
            duration = (datetime.now() - self.step_times[step_id]).total_seconds()
            self.logger.info(f"[DONE] Completed step: {step_name} ({step_id}) in {duration:.2f}s")
        else:
            self.logger.info(f"[DONE] Completed step: {step_name} ({step_id})")
        
        if output:
            self.logger.debug(f"Step output: {output}")
    
    def log_step_error(self, step_id: str, step_name: str, error: Exception):
        """Log an error during a workflow step."""
        self.logger.error(f"[ERROR] Error in step: {step_name} ({step_id}): {str(error)}")
    
    def log_workflow_complete(self):
        """Log workflow completion."""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"🎉 Workflow completed in {total_duration:.2f}s")
    
    def log_api_call(self, tool_name: str, endpoint: str, status: str):
        """Log API call information."""
        self.logger.debug(f"API Call - {tool_name} | {endpoint} | Status: {status}")
    
    def log_reasoning(self, agent_name: str, reasoning: str):
        """Log agent reasoning."""
        self.logger.info(f"🤔 {agent_name} reasoning: {reasoning}")
