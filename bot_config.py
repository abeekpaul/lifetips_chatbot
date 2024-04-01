import boto3

class AWSParameterStore:
    def __init__(self, region):
        self.ssm_client = boto3.client('ssm', region_name=region)

    def get_parameter(self, parameter_name):
        try:
            response = self.ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
            return response['Parameter']['Value']
        except Exception as e:
            print(f"Error retrieving parameter {parameter_name}: {e}")
            return None

# Usage example
if __name__ == '__main__':
    # Set AWS region
    region_name = 'ap-southeast-2'
    parameter_store = AWSParameterStore(region_name)

    # Retrieve parameters
    TG_ACCESS_TOKEN = parameter_store.get_parameter('TG_ACCESS_TOKEN')
    GPT_BASICURL = parameter_store.get_parameter('GPT_BASICURL')
    GPT_MODELNAME = parameter_store.get_parameter('GPT_MODELNAME')
    GPT_APIVERSION = parameter_store.get_parameter('GPT_APIVERSION')
    GPT_ACCESS_TOKEN = parameter_store.get_parameter('GPT_ACCESS_TOKEN')
    REDIS_HOST = parameter_store.get_parameter('REDIS_HOST')
    REDIS_PORT = parameter_store.get_parameter('REDIS_PORT')
    REDIS_PASSWORD = parameter_store.get_parameter('REDIS_PASSWORD')

    # Now you can use these variables throughout your script.
