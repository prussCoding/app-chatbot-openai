import os
import venv
import subprocess


# Create a Python virtual environment
venv_dir = 'venv'
venv.create(venv_dir, with_pip=True)
venv_path = os.path.join(venv_dir, 'Scripts' if os.name == 'nt' else 'bin')


# Activate the virtual environment
activate_script = os.path.join(venv_path, 'activate')
subprocess.check_call(f'source {activate_script}', stdout=subprocess.PIPE, shell=True)
