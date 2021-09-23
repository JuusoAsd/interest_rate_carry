from dotenv import dotenv_values

conf = dotenv_values(".env")
INFURA = conf['infura']