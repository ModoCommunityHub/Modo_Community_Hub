# Local setup:
___
This repository uses poetry to handle the dependencies.
The following steps will help you set up the project locally.
1. Clone the repository.
2. Create a virtual environment.
   - `python -m venv .venv`
3. Use poetry to install the dependencies.
   - `poetry install`
4. Activate the virtual environment.
   - `poetry shell`
5. Command to remove the .venv folder.
   - MAC: `rm -rf .venv`
   - Windows: `rmdir /s .venv`


# Python setup using pyenv:
___
It is preferred to use `pyenv` to manage python installations on your machine.

MacOS: 
- `brew install pyenv`
- `pyenv install 3.10.11`
- `pyenv global 3.10.11`

Windows:
- `choco install pyenv-win`
- `pyenv install 3.10.11`
- `pyenv global 3.10.11`
- Without choco:
- - Follow the instructions on the [pyenv-win github page](https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#powershell).

# Running the scripts
1. Install the kit locally.
   - `python -m scripts.install`
2. Build the .lpk file.
   - `python -m scripts.build`
3. Run the UI locally. (Not in modo)
   - `python -m scripts.run`


## TODO List:
- [ ] Clean up kit JSON data.
- [ ] Add more kits to the kits.json file.
- [ ] Create workflow for adding a new kit.
- [ ] Allow self update of the hub.
- [ ] Show installed kits.
