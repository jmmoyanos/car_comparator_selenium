import yaml

def read_secrets_yaml():

    with open('./secrets/secrets.yaml') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        secrets = yaml.load(file, Loader=yaml.FullLoader)

    
    return secrets