import boto3

# Set AWS region
region_name = 'ap-northeast-2'

# Create SSM client
ssm = boto3.client('ssm', region_name=region_name)

def get_parameter(parameter_name):
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']
TG_ACCESS_TOKEN = get_parameter('TG_ACCESS_TOKEN')
GPT_BASICURL = get_parameter('GPT_BASICURL')
GPT_MODELNAME = get_parameter('GPT_MODELNAME')
GPT_APIVERSION = get_parameter('GPT_APIVERSION')
GPT_ACCESS_TOKEN = get_parameter('GPT_ACCESS_TOKEN')
REDIS_HOST = get_parameter('REDIS_HOST')
REDIS_PORT = get_parameter('REDIS_PORT')
REDIS_PASSWORD = get_parameter('REDIS_PASSWORD')