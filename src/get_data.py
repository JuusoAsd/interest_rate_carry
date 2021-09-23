import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from dotenv import dotenv_values
from web3 import Web3
import requests
import json
from pprint import pprint


conf = dotenv_values(".env")
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{conf['infura']}"))

abi_implementation = {'address':'abi'}

def annualized_return(rate):
    per_day = 6500
    days = 365
    factor = 1*10**18
    return (((rate/factor*per_day + 1) ** days) - 1 ) * 100

def main():
    pool_address = '0x989273ec41274C4227bCB878C2c26fdd3afbE70d'
    folder = os.path.join(os.getcwd(), "abi","rari_abi.json")
    with open(folder) as f:
        abi = json.load(f)

    contract = web3.eth.contract(
            address=web3.toChecksumAddress(pool_address), abi=abi
        )

    lend = contract.functions.supplyRatePerBlock().call()
    borrow = contract.functions.borrowRatePerBlock().call()

    print(annualized_return(lend), annualized_return(borrow))

   
    
def get_rari_fuse():
    comptroller_address='0x835482FE0532f169024d5E9410199369aAD5C77E'
    comptroller_implementation='0xbC81C8fBB73B5825bA6CC7C4dE1fE92004Cc80c6'
    comptroller = get_abi_implementation_separate(
        comptroller_address,
        comptroller_implementation
        )
    important_pools = [6,18,8,9,7,24]
    pool_list = comptroller.functions.getAllPools().call()
    for nr in important_pools:
        print()
        get_fuse_pool(pool_list[nr])


def get_fuse_pool(pool_info):
    print(pool_info[0])
    pool_address = pool_info[2]
    pool_contract = get_pool_contract(pool_address)
    #print(*pool_contract.functions, '\n')
    all_markets = pool_contract.functions.getAllMarkets().call()
    for market in all_markets:
        market_contract = get_market_contract(market)
        #get_rari_rate(market_contract)
        print(market_contract.functions.interestRateModel().call())
        
def get_rari_rate(contract):
    symbol = contract.functions.symbol().call()
    lend = contract.functions.supplyRatePerBlock().call()
    borrow = contract.functions.borrowRatePerBlock().call()

    print(symbol, round(annualized_return(lend), 2), round(annualized_return(borrow),2))


def get_pool_contract(address):
    initial_contract = web3.eth.contract(
            address=address,
            abi=get_abi(address)
        )
    implementation_address = initial_contract.functions.comptrollerImplementation().call()
    return web3.eth.contract(
            address=address,
            abi=get_abi(implementation_address)
        )

def get_market_contract(address):
    initial_contract = web3.eth.contract(
            address=address,
            abi=get_abi(address)
        )
    implementation_address = initial_contract.functions.implementation().call()
    return web3.eth.contract(
            address=address,
            abi=get_abi(implementation_address)
        )

def get_abi_implementation_separate(address, implementation):

    return web3.eth.contract(
            address=address,
            abi=get_abi(implementation)
        )

def get_abi(address):
    if address in abi_implementation:
        return abi_implementation[address]
    else:
        r = requests.get(
                ("https://api.etherscan.io/api"
                    "?module=contract"
                    "&action=getabi"
                    f"&address={address}"
                    f"&apikey={conf['etherscan']}")
                    )
        
        abi_implementation[address] = r.json()['result']
        return r.json()['result']


if __name__ == '__main__':
    get_rari_fuse()