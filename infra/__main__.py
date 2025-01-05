import pulumi
import pulumi_aws as aws

# Create VPC and networking
vpc = aws.ec2.Vpc("bouncing-circles-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "bouncing-circles-vpc"}
)

# Create public subnets in different AZs
public_subnet_1 = aws.ec2.Subnet("public-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-west-2a",
    map_public_ip_on_launch=True,
    tags={"Name": "public-subnet-1"}
)

public_subnet_2 = aws.ec2.Subnet("public-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-west-2b",
    map_public_ip_on_launch=True,
    tags={"Name": "public-subnet-2"}
)

# Create Internet Gateway
igw = aws.ec2.InternetGateway("igw",
    vpc_id=vpc.id,
    tags={"Name": "bouncing-circles-igw"}
)

# Create route table for public subnets
public_rt = aws.ec2.RouteTable("public-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id
        )
    ],
    tags={"Name": "public-rt"}
)

# Associate route table with public subnets
rt_assoc_1 = aws.ec2.RouteTableAssociation("rt-assoc-1",
    subnet_id=public_subnet_1.id,
    route_table_id=public_rt.id
)

rt_assoc_2 = aws.ec2.RouteTableAssociation("rt-assoc-2",
    subnet_id=public_subnet_2.id,
    route_table_id=public_rt.id
)

# Create ECR repository
repo = aws.ecr.Repository("bouncing-circles-repo",
    image_tag_mutability="MUTABLE",
    force_delete=True
)

# Create ECS cluster
cluster = aws.ecs.Cluster("bouncing-circles-cluster",
    tags={"Name": "bouncing-circles-cluster"}
)

# Create ALB
alb = aws.lb.LoadBalancer("bouncing-circles-alb",
    internal=False,
    load_balancer_type="application",
    security_groups=[aws.ec2.SecurityGroup("alb-sg",
        vpc_id=vpc.id,
        ingress=[aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"]
        )],
        egress=[aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"]
        )]
    ).id],
    subnets=[public_subnet_1.id, public_subnet_2.id],
    tags={"Name": "bouncing-circles-alb"}
)

# Create ALB target group
target_group = aws.lb.TargetGroup("bouncing-circles-tg",
    port=8000,
    protocol="HTTP",
    target_type="ip",
    vpc_id=vpc.id,
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        path="/",
        port="8000",
        healthy_threshold=2,
        unhealthy_threshold=10,
        timeout=5,
        interval=10
    )
)

# Create ALB listener
listener = aws.lb.Listener("bouncing-circles-listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[aws.lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=target_group.arn
    )]
)

# Create ECS task execution role
task_execution_role = aws.iam.Role("task-execution-role",
    assume_role_policy=aws.iam.get_policy_document(statements=[{
        "actions": ["sts:AssumeRole"],
        "principals": [{
            "type": "Service",
            "identifiers": ["ecs-tasks.amazonaws.com"]
        }]
    }]).json
)

# Attach task execution policy
task_execution_policy = aws.iam.RolePolicyAttachment("task-execution-policy",
    role=task_execution_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
)

# Create CloudWatch logs policy
cloudwatch_policy = aws.iam.RolePolicy("cloudwatch-policy",
    role=task_execution_role.name,
    policy=pulumi.Output.json_dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }]
    })
)

# Create ECS task definition
task_definition = aws.ecs.TaskDefinition("bouncing-circles-task",
    family="bouncing-circles",
    cpu="256",
    memory="1024",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn=task_execution_role.arn,
    container_definitions=repo.repository_url.apply(
        lambda url: pulumi.Output.json_dumps([{
            "name": "bouncing-circles",
            "image": f"{url}:latest",
            "portMappings": [{
                "containerPort": 8000,
                "protocol": "tcp"
            }],
            "essential": True,
            "environment": [
                {"name": "FLASK_DEBUG", "value": "1"},
                {"name": "PYTHONUNBUFFERED", "value": "1"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/bouncing-circles",
                    "awslogs-region": "us-west-2",
                    "awslogs-stream-prefix": "ecs",
                    "awslogs-create-group": "true"
                }
            }
        }])
    )
)

# Create ECS service
service = aws.ecs.Service("bouncing-circles-service",
    cluster=cluster.arn,
    desired_count=1,
    launch_type="FARGATE",
    task_definition=task_definition.arn,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        assign_public_ip=True,
        subnets=[public_subnet_1.id, public_subnet_2.id],
        security_groups=[aws.ec2.SecurityGroup("service-sg",
            vpc_id=vpc.id,
            ingress=[aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=8000,
                to_port=8000,
                cidr_blocks=["0.0.0.0/0"]
            )],
            egress=[aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"]
            )]
        ).id]
    ),
    load_balancers=[aws.ecs.ServiceLoadBalancerArgs(
        target_group_arn=target_group.arn,
        container_name="bouncing-circles",
        container_port=8000
    )]
)

# Export useful values
pulumi.export('repository_url', repo.repository_url)
pulumi.export('alb_dns_name', alb.dns_name) 