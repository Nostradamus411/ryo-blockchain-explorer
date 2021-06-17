from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

class AwsDeployStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve VPC information
        default_vpc = ec2.Vpc.from_lookup(self,
            "DefaultVpc",
            is_default=True,
        )

        ssh_explorer_sg = ec2.SecurityGroup(
            self,
            id='SshExplorerSg',
            vpc=default_vpc,
            allow_all_outbound=True,
            security_group_name='ssh_explorer_sg'
        )

        # # SSH ingress from home
        # ssh_explorer_sg.add_ingress_rule(
        #     peer=ec2.Peer.ipv4('200.200.200.200/32'),
        #     connection=ec2.Port.tcp(22),
        #     description='allow ssh from home ip'
        # )

        # HTTP ingress from anywhere
        ssh_explorer_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description='allow http from anywhere'
        )
        
        # HTTPS ingress from anywhere
        ssh_explorer_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description='allow https from anywhere'
        )

        # ryo node ingress from anywhere
        ssh_explorer_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(12211),
            description='allow ryo node from anywhere'
        )

        # aws ec2 describe-images --region us-east-1 --image-ids ami-0e4d932065378fd3d  : is cli cmd to find machine image root ebs
        ryo_bc_ebs = ec2.BlockDevice(
                        device_name='/dev/sda1',
                        volume=ec2.BlockDeviceVolume.ebs(volume_size=30,volume_type=ec2.EbsDeviceVolumeType.GP3)
                    )

        explorer_ec2 = ec2.Instance(
            self,
            id='ExplorerEc2',
            instance_name='Ryo Blockchain Explorer',
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3_AMD,ec2.InstanceSize.SMALL),
            machine_image=ec2.MachineImage.generic_linux({'us-east-1':'ami-0e4d932065378fd3d'}),
            vpc=default_vpc,
            security_group=ssh_explorer_sg,
            block_devices=[ryo_bc_ebs],
            key_name='ryo_explorer_ssh',
        )
        
        # public ipv4 address
        eip=ec2.CfnEIP(self,'Ryo-community Server IP')

        pub_ip_explorer_ec2 = ec2.CfnEIPAssociation(
            self,
            id='PubIpExplorerEc2',
            eip=eip.ref,
            instance_id=explorer_ec2.instance_id
        )