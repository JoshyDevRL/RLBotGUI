import fileinput
import os
import random
import re
import string
import sys
import tempfile
from pathlib import Path
from shutil import move

from rlbot_gui.bot_management.downloader import download_and_extract_zip


def convert_to_filename(text):
    """
    Normalizes string, converts to lowercase, removes non-alphanumeric characters,
    and converts spaces to underscores.
    """
    import unicodedata
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    valid_chars = f'-_.() {string.ascii_letters}{string.digits}'
    filename = ''.join(c for c in normalized if c in valid_chars)
    filename = filename.replace(' ', '_')  # Replace spaces with underscores
    return filename


def safe_move(src, dst):
    """ https://bugs.python.org/issue32689 """
    move(str(src), str(dst))


def replace_all(file, regex, replacement):
    for line in fileinput.input(file, inplace=1):
        updated = re.sub(regex, replacement, line)
        sys.stdout.write(updated)


def bootstrap_python_bot(bot_name, directory):
    sanitized_name = convert_to_filename(bot_name)
    bot_directory = Path(directory or '.')
    top_dir = bot_directory / sanitized_name
    if os.path.exists(top_dir):
        raise FileExistsError(f'There is already a bot named {sanitized_name}, please choose a different name!')

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        print('created temporary directory', tmpdir)

        download_and_extract_zip(
            download_url='https://github.com/RLBot/RLBotPythonExample/archive/master.zip',
            local_folder_path=tmpdir)

        safe_move(tmpdir / 'RLBotPythonExample-master', top_dir)

    # Choose appropriate file names based on the bot name
    code_dir = top_dir / sanitized_name
    python_filename = f'{sanitized_name}.py'
    python_file = code_dir / python_filename
    config_filename = f'{sanitized_name}.cfg'
    config_file = code_dir / config_filename

    replace_all(top_dir / 'rlbot.cfg', r'(participant_config_\d = ).*$',
                r'\1' + os.path.join(sanitized_name, config_filename).replace('\\', '\\\\'))

    # We're making some big assumptions here that the file structure / names in RLBotPythonExample will not change.
    safe_move(top_dir / 'python_example', code_dir)
    safe_move(code_dir / 'python_example.py', python_file)
    safe_move(code_dir / 'python_example.cfg', config_file)

    replace_all(config_file, r'name = .*$', 'name = ' + bot_name)
    replace_all(config_file, r'python_file = .*$', 'python_file = ' + python_filename)

    # This is intended to open the example python file in the default system editor for .py files.
    # Hopefully this will be VS Code or notepad++ or something. If it gets executed as a python script, no harm done.
    os.startfile(python_file)

    return config_file


def bootstrap_scratch_bot(bot_name, directory):
    sanitized_name = convert_to_filename(bot_name)
    bot_directory = Path(directory or '.')
    top_dir = bot_directory / sanitized_name
    if os.path.exists(top_dir):
        raise FileExistsError(f'There is already a bot named {sanitized_name}, please choose a different name!')

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        print('created temporary directory', tmpdir)

        download_and_extract_zip(
            download_url='https://github.com/RLBot/RLBotScratchInterface/archive/gui-friendly.zip',
            local_folder_path=tmpdir)

        safe_move(tmpdir / 'RLBotScratchInterface-gui-friendly', top_dir)

    # Choose appropriate file names based on the bot name
    code_dir = top_dir / sanitized_name
    sb3_filename = f'{sanitized_name}.sb3'
    sb3_file = code_dir / sb3_filename
    config_filename = f'{sanitized_name}.cfg'
    config_file = code_dir / config_filename

    replace_all(top_dir / 'rlbot.cfg', r'(participant_config_\d = ).*$',
                r'\1' + os.path.join(sanitized_name, config_filename).replace('\\', '\\\\'))

    # We're assuming that the file structure / names in RLBotScratchInterface will not change.
    # Semi-safe assumption because we're looking at a gui-specific git branch which ought to be stable.
    safe_move(top_dir / 'scratch_bot', code_dir)
    safe_move(code_dir / 'my_scratch_bot.sb3', sb3_file)
    safe_move(code_dir / 'my_scratch_bot.cfg', config_file)

    replace_all(config_file, r'name = .*$', 'name = ' + bot_name)
    replace_all(config_file, r'sb3file = .*$', 'sb3file = ' + sb3_filename)
    replace_all(config_file, r'port = .*$', 'port = ' + str(random.randint(20000, 65000)))

    return config_file
