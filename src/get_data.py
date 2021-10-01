import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from dotenv import dotenv_values
from web3 import Web3
import requests
import json
from pprint import pprint


conf = dotenv_values(".env")

# initialize the web3 object using infura endpoint
# endpoint can also be for example your own ethereum node
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{conf['infura']}"))

# saving abi's in dictionary for addresses so they do not have to be re-read
abi_implementation = {'address':'abi'}

# replicating rari interest rate calculation - https://docs.rari.capital/fuse/#calculating-the-apy-using-rate-per-block
def annualized_return(rate):
    per_day = 6500
    days = 365
    factor = 1*10**18
    return (((rate/factor*per_day + 1) ** days) - 1 ) * 100
    
def get_rari_fuse():
    # https://docs.rari.capital/contracts/#rari-governance FusePoolDirectory
    comptroller_address='0x835482FE0532f169024d5E9410199369aAD5C77E'
    
    # Some contracts have "proxy implementation", where implementation and contract are in different address
    # The "implementation address" can be usually found by querying the address
    # In this case, not for some reason
    # as workaround, going to etherscan for the address: https://etherscan.io/address/0x835482FE0532f169024d5E9410199369aAD5C77E
    # going to contract > read as proxy
    # https://etherscan.io/address/0x835482FE0532f169024d5E9410199369aAD5C77E#readProxyContract
    # there you can find "abi for the implementation contract" -address
    comptroller_implementation='0xbC81C8fBB73B5825bA6CC7C4dE1fE92004Cc80c6'
    
    # gets the comptroller contract object
    comptroller = get_abi_implementation_separate(
        comptroller_address,
        comptroller_implementation
        )

    # integers for the largest pools
    important_pools = [6,18,8,9,7,24]
    
    # contracts have functions which are defined in ABI
    # all functions can be checked by, for example, print(*contract.functions, sep='\n')
    # this function gets all pools from comptroller
    pool_list = comptroller.functions.getAllPools().call()
    for nr in important_pools:
        print()
        get_fuse_pool(pool_list[nr])


def get_fuse_pool(pool_info):
    print(pool_info[0])
    pool_address = pool_info[2]
    pool_contract = get_pool_contract(pool_address)
    
    # pool contact has multiple markets like ETH, DAI, USDC...
    # looping through these "markets" and getting the interest rates for those
    all_markets = pool_contract.functions.getAllMarkets().call()
    for market in all_markets:
        market_contract = get_market_contract(market)
        get_rari_rate(market_contract)
        
def get_rari_rate(contract):
    # symbol for the token (ETH, DAI, USDC)
    symbol = contract.functions.symbol().call()
    
    # information required for computing the interest rates
    lend = contract.functions.supplyRatePerBlock().call()
    borrow = contract.functions.borrowRatePerBlock().call()
    print(symbol, round(annualized_return(lend), 2), round(annualized_return(borrow),2))

# create contract object for the pool
def get_pool_contract(address):
    # create the contract
    initial_contract = web3.eth.contract(
            address=address,
            abi=get_abi(address)
        )
    
    # contract has comptrollerImplementation function which returns the address for the pool implementation
    implementation_address = initial_contract.functions.comptrollerImplementation().call()
    # returns the pool contract
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

# creating the contract-object when contract and implementation are in different addresses
def get_abi_implementation_separate(address, implementation):

    return web3.eth.contract(
            address=address,
            abi=get_abi(implementation)
        )
        
# etherscan has api which allows to read abis for (verified) smart contracts
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