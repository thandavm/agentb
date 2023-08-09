from constructs import Construct
import uuid
import os
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_ssm as ssm,   
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_events as events,
    custom_resources as cr
)
from aws_cdk.aws_ssm import StringParameter

class BrAgentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # 1. Create a bucket  
        unique_id = str(uuid.uuid4())
        bucket_name = f'br-agent-bucket{unique_id}'

        br_bucket = s3.Bucket(self, 
            "bedrock_bucket",
            bucket_name=bucket_name,
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )    
        
        # 2. parameter to store bucket name, 
        ssm_param_bucket = StringParameter(self, "bucket_name_param",
                                    parameter_name="/br_agent/bucket_name",
                                    string_value=bucket_name)
        
        ssm_param_sqlite = StringParameter(self, "sqlite_db_name",
                            parameter_name="/br_agent/sqlite_db_name",
                            string_value="database/pets.db")
        
        ssm_param_dynamotbl = StringParameter(self, "dynamo_table",
                    parameter_name="/br_agent/dynamo_table",
                    string_value="pets")
        
        
        # 3. Run set up lambda to set up tables
        ## Lambda role
        lambda_action_role = iam.Role(
            self, 'lambda_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMFullAccess')],
            
            description='lambda_role for br_agent actions'
        )
        
        ## Bedrock role
        bedrock_role = iam.Role(
            self, 'bedrock_role',
            assumed_by=iam.ServicePrincipal('bedrock.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambda_FullAccess'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess')],
            
            description='lambda_role for setup'
        )
        
        lambda_setup = _lambda.Function(
            self, 'lambda_setup',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('lambda'),
            handler='lambda_setup.lambda_handler',
            timeout=Duration.seconds(300),
            role=lambda_action_role
        )

        # 4. Run sqllite lambda to retrieve information
        lambda_sqlite = _lambda.Function(
            self, 'lambda_sqlite',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('lambda'),
            handler='lambda_sqlite.lambda_handler',
            timeout=Duration.seconds(300),
            role=lambda_action_role
        )
        
        principal = iam.ServicePrincipal('bedrock.amazonaws.com')
        policy_statement_sqlite = iam.PolicyStatement(
            actions=["lambda:InvokeFunction"],
            resources=[lambda_sqlite.function_arn],
            principals=[principal]
        )
        
        # Run google search lambda to retrieve information
        lambda_search = _lambda.Function(
            self, 'lambda_search',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('lambda'),
            handler='lambda_search.lambda_handler',
            timeout=Duration.seconds(300),
            role=lambda_action_role
        )
        
        policy_statement_search  = iam.PolicyStatement(
            actions=["lambda:InvokeFunction"],
            resources=[lambda_search.function_arn],
            principals=[principal]
        )