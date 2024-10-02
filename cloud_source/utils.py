#!/usr/bin/env python
# encoding: utf-8

# João Antunes <joao8tunes@gmail.com>
# https://github.com/joao8tunes

from pathlib import Path
from typing import List
import subprocess
import tempfile
import logging
import re


from cloud_source.system_settings import setup_logging

setup_logging(__name__)


def validate_rfc1123_label(label: str) -> bool:
    """
    Validate if a given string conforms to the RFC 1123 label format.

    Parameters
    ----------
    label : str
        The label string to be validated.

    Returns
    -------
    bool
        True if the string is a valid RFC 1123 label, False otherwise.

    Examples
    --------
    >>> validate_rfc1123_label("my-name")
    True
    >>> validate_rfc1123_label("123-abc")
    True
    >>> validate_rfc1123_label("-invalid-")
    False
    >>> validate_rfc1123_label("Invalid")
    False
    >>> validate_rfc1123_label("invalid-")
    False
    """
    # RFC 1123 label pattern
    rfc1123_label_pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'

    # Check if the label string matches the pattern
    return re.match(rfc1123_label_pattern, label) is not None


def list_files(directory: str) -> List[str]:
    """
    Recursively list all files in a directory and its subdirectories.

    Parameters
    ----------
    directory : str
        The path of the root directory to search for files.

    Returns
    -------
    List[str]
        A list of file paths as strings.

    Examples
    --------
    >>> list_files('/path/to/directory')
    ['/path/to/directory/file1.txt', '/path/to/directory/subdir/file2.txt', ...]

    """
    root_dir = Path(directory)

    return [str(f) for f in root_dir.rglob('*') if f.is_file()]


def copy_file(source_file: str, destination_file: str) -> None:
    """
    Read a text file and copy its content to another file.

    Parameters
    ----------
    source_file : str
        The path of the source text file to be read.
    destination_file : str
        The path of the destination file where the content will be copied.

    Examples
    --------
    >>> copy_file('source.txt', 'destination.txt')
    """
    with open(source_file, 'r') as src:
        content = src.read()

    with open(destination_file, 'w') as dst:
        dst.write(content)


def execute_command(command) -> str:
    """
    Execute a shell command and log its output and errors.

    Parameters
    ----------
    command : str
        The shell command to be executed.

    Returns
    -------
    str
        The combined output (stdout) of the command.
    """
    # Start the subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Capture stdout and stderr
    stdout, stderr = process.communicate()

    # Log stdout line by line
    for line in stdout.splitlines():
        line = line.strip()

        if line:
            logging.debug(line)

    # Log stderr line by line
    for line in stderr.splitlines():
        line = line.strip()

        if line:
            logging.error(line)

    # Return the combined stdout content
    return stdout.strip()


def create_temp_file(extension: str) -> str:
    """
    Create a temporary file with a specified extension.

    Parameters
    ----------
    extension : str
        The file extension (including the dot, e.g., '.txt').

    Returns
    -------
    str
        The path to the created temporary file.
    """
    # Create a temporary file with a unique name
    temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)

    # Get the file path
    temp_file_path = temp_file.name

    # Close the file as we don't need it open
    temp_file.close()

    return temp_file_path
