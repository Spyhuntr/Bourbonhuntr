import boto3
import docker
import base64

session = boto3.session.Session()
region = session.region_name

docker_client = docker.from_env()
ecr_client = boto3.client('ecr', region_name=region)
ecr_creds = (ecr_client.get_authorization_token()['authorizationData'][0])

ecr_uname, ecr_password = base64.b64decode(ecr_creds['authorizationToken']).decode('utf-8').split(':')
ecr_url = ecr_creds['proxyEndpoint']

docker_client.login(
    username = ecr_uname,
    password = ecr_password,
    registry = ecr_url
)

ecr_repo_name = f"{ecr_url.replace('https://', '')}/bourbon-app"

for log_line in docker_client.images.push(ecr_repo_name, stream=True, tag='latest', decode=True):
    print(log_line)



ecs_client = boto3.client('ecs')
ecs_cluster = 'arn:aws:ecs:us-east-1:098810842820:cluster/bourbon-app-cluster'

running_tasks = ecs_client.list_tasks(
    cluster = ecs_cluster,
    desiredStatus='RUNNING',
    launchType='FARGATE'
)

for tasks in running_tasks['taskArns']:
    print(f'Stopping task {tasks}')
    ecs_client.stop_task(
        cluster = ecs_cluster,
        task = tasks
    )

print("Starting new task")
ecs_client.run_task(
    cluster = ecs_cluster,
    count=1,
    enableECSManagedTags=True,
    launchType='FARGATE',
    networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-a90d4187',
            ],
            'securityGroups': [
                'sg-065198b6df8cf9a1d',
            ],
            'assignPublicIp': 'ENABLED'
        }
    },
    overrides={
        'executionRoleArn': 'arn:aws:iam::098810842820:role/ecsTaskExecutionRole',
        'taskRoleArn': 'arn:aws:iam::098810842820:role/bourbonAppTaskRole'
    },
    platformVersion='LATEST',
    taskDefinition='bourbon-app'
)