# DeFi interest rate arbitrage

## Functionality
Goal of this project is to find optimal allocations between different stablecoin lendingpools.


## Setup
1. Clone project repository to relevant location locally:
```sh
git clone https://github.com/-------------.git
cd *repo name*
```

2. Install requirements for and initialize new venv for python3 in project directory.
Then install dependencies with pip:
```sh
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

3. When adding new dependencies, add them to the requiremements file by freezing the pip:
```sh
pip freeze > requirements.txt
```

4. Create .env -file and add relevant api keys there:
```sh
echo -e "infura=infura_api\netherscan=etherscan\n" >> .env
```

