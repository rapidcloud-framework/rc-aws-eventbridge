__author__ = "Pjain@kinect-consulting.com"
from commands.kc_metadata_manager.aws_metadata import Metadata
from commands.kc_metadata_manager.aws_infra import AwsInfra

import pprint
import json
import os
from boto3.dynamodb.conditions import Attr


class ModuleMetadata(Metadata):

    def __init__(self, args):
        super().__init__(args)
        self.args = args
        self.boto3_session = super().get_boto3_session()

    def pp(self, v):
        if 'RAPIDCLOUD_TEST_MODE_AWS_EVENTBRIDGE' in os.environ and os.environ.get('RAPIDCLOUD_TEST_MODE_AWS_EVENTBRIDGE') == "true":
            print(pprint.pformat(v))

    def load_params(self, module, command, args):
        # we will populate this dict and pass it to the command functions
        params = {}
        try:
            # we're pulling all valus from the args object into a dict
            args_dict = vars(args)

            # we then load the actual args from the module's json
            json_args = self.get_module_json("eventbridge")[module][command]['args']

            # now we'll loop over them all
            for arg in json_args.keys():
                params[arg] = args_dict[f"{module}_{arg}"]
                if arg == 'tags' or arg == 'labels' or arg == 'selectors':
                    # convert string to dict here
                    arg_json = json.loads(args_dict[f"{module}_{arg}"].replace("\\", ""))
                    try:
                        params[arg] = arg_json
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(f"init.py error: {e}")
        return params


    def create_eventbus(self, metadata=None):
        super().delete_infra_metadata(name=self.args.eventbus_name)
        params = self.load_params('eventbridge', 'create_eventbus', self.args)
        resource_name = self.args.eventbus_name
        resource_type = "aws_event_bus"
        super().add_aws_resource(resource_type, resource_name, params)

    def create_event_rule(self, metadata=None):
        super().delete_infra_metadata(name=self.args.eventrule_name)
        params = self.load_params('eventbridge', 'create_event_rule', self.args)
        resource_name = self.args.eventrule_name
        resource_type = "aws_event_rule"
        super().add_aws_resource(resource_type, resource_name, params)

    def check_for_aws_auth_refresh(self, eventbus_name):
        # check if a metadata item exists for aws_auth_command and this cluster
        aws_auth_md = {}
        filters = (Attr('command').eq('manage_aws_auth') & Attr('params.eventbus_name').eq(eventbus_name))

        aws_auth_result = super().get_all_resources(extra_filters=filters)

        # if we get a result, call the aws_auth manage function
        if len(aws_auth_result) > 0:
            aws_auth_md['profile'] = aws_auth_result[0]['profile']
            aws_auth_md['phase'] = aws_auth_result[0]['phase']
            aws_auth_md['cmd_id'] = aws_auth_result[0]['cmd_id']
            aws_auth_md['command'] = aws_auth_result[0]['command']
            aws_auth_md['fqn'] = aws_auth_result[0]['fqn']
            aws_auth_md['params'] = aws_auth_result[0]['params']
            for k, v in aws_auth_result[0]['params'].items():
                aws_auth_md[f"eventbridge_{k}"] = v
            self.manage_aws_auth(aws_auth_md, True)


    def remove_eventbus(self, metadata=None):
        try:
            command_list = []
            filters = Attr('phase').eq('eventbridge') & Attr('params.eventbus_name').eq(self.args.eventbus_name)
            result = super().get_all_resources(extra_filters=filters)
            for i in result:
                command_list.append(i['command'])
            command_list.remove('create_eventbus')
        except Exception as e:
            self.pp(e)

        # if we get a result, call the aws_auth manage function
        if len(command_list) > 0:
            raise Exception(
                f"Validation Failed!, Please make sure you remove and APPLY any dependent module prior to remove this module"
                f"({','.join(command_list)})")
        else:
            AwsInfra(self.args).undo_command()