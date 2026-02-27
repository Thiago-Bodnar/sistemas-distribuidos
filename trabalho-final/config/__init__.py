from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

CLOUDAMQP_URL= os.getenv('CLOUDAMQP_URL')
NODE_ID = os.getenv('NODE_ID')

EXCHANGE_NAME=os.getenv('EXCHANGE_NAME')
ROUTING_AJUDA=os.getenv('ROUTING_AJUDA')
ROUTING_STATUS=os.getenv('ROUTING_STATUS')
