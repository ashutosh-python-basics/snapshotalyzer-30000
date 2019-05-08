import boto3
import botocore
import click

##below line creates asession with your user under profile 'shotty'
session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

##purpose of function filter_instnaces is to get the list of all instances under a project (tag)
##if not passed list of instances
def filter_instances(project):
    ##intitialize variable list instances with zero items
    instances = []

    if project:
    ## filter is a list having dictionary of name key and value the value of proejct tag name as passed
       filters = [{'Name':'tag:Project','Values':[project]}]
       instances = ec2.instances.filter(Filters=filters)
    else:
       instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only Snapshots for project (tag Project:<name>)")
@click.option('--all','list_all', default=False,is_flag=True, help="List all snapshots for each volume, not just the most recent one ")
def list_snapshots(project, list_all):
    "List EC2 Snashots my buddy"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(",".join((
                    s.id,
                    s.description,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all:break

    return


@cli.group('volumes')
def volumes():
    """Commands for Volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only Volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 Volumes my buddy"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(",".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or 'NOT Encrypted'
            )))
    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command("createsnapshot")
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")

def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:

        print("Stopping..{0}".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="CReated by snapshotalyzer 30000")

        print("Starting..{0}".format(i.id))

        i.start()
        i.wait_until_running()

    print("JOB's DONE!")

    return


@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 Instances my friend"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(','.join((
             i.id,
             i.instance_type,
             i.placement['AvailabilityZone'],
             i.state['Name'],
             i.public_dns_name,
             tags.get('Project', '<no project passsed>')
             )))
    return

@instances.command('stop')
@click.option('--project', default=None, help='Only instnaces for project')
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping...",format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None, help='Only instnaces for project')
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting...",format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}. ".format(i.id) + str(e))
            continue

    return


if __name__ == '__main__':
    cli()
