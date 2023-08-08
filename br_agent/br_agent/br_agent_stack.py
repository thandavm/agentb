from constructs import Construct
import uuid
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_ssm as ssm,   
    aws_iam as iam,
)
from aws_cdk.aws_ssm import StringParameter

class BrAgentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # 1. Create a bucket  
        unique_id = str(uuid.uuid4())
        bucket_name = f'br-agent-bucket{unique_id}'

        bucket = s3.Bucket(self, 
            "bedrock_bucket",
            bucket_name=bucket_name,
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
                           
        # 2. parameter to store bucket name, 
        ssm_param = StringParameter(self, "bucket_name_param",
                                    parameter_name="/br_agent/bucket_name",
                                    string_value=bucket_name)
        
        ssm_param = StringParameter(self, "sqlite_db_name",
                            parameter_name="/br_agent/sqlite_db_name",
                            string_value="pets.db")
        
        # 3. create a RDS with secret for rds username and password

        
        # lambda functions
        lambda_action_role = iam.Role(
            self, 'lambda_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMFullAccess')],
            
            description='lambda_role for br_agent actions'
        )
        
        lambda_aurora = _lambda.Function(
            self, 'lambda_aurora',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('lambda'),
            handler='lambda_aurora.handler',
            timeout=Duration.seconds(300),
            role=lambda_action_role
        )
        
        lambda_sqlite = _lambda.Function(
            self, 'lambda_sqlite',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('lambda'),
            handler='lambda_sqlite.lambda_handler',
            timeout=Duration.seconds(300),
            role=lambda_action_role
        )
        
        #create an apigateway
        api_role = iam.Role(
            self, 'api_role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonAPIGatewayPushToCloudWatchLogs'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambda_FullAccess')])
            
        lambda_proxy = _lambda.Function(
            self, 'lambda_proxy',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('lambda'),
            handler='lambda_proxy.lambda_handler',
            timeout=Duration.seconds(300),
            role=lambda_action_role
        )
        
        lambda_api = apigateway.LambdaRestApi(self, 'lambda_api',
                                               handler=lambda_proxy,
                                               proxy=False,
                                               rest_api_name='br_agent_lambda_api',
                                               description='br_agent_lambda_api')
        
        agent = lambda_api.root.add_resource("agent")
        agent.add_method("GET") # GET /items
        agent.add_method("POST") # POST /items
        
        