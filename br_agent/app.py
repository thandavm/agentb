#!/usr/bin/env python3
import aws_cdk as cdk
from br_agent.br_agent_stack import BrAgentStack

app = cdk.App()
BrAgentStack(app, "br-agent")

app.synth()
