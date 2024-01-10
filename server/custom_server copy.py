#!/usr/bin/env python3

__author__ = "Igor Royzis"
__copyright__ = "Copyright 2023, Kinect Consulting"
__license__ = "Commercial"
__email__ = "iroyzis@kinect-consulting.com"

import logging
import json
import os
import pprint

from boto3.dynamodb.conditions import Attr

logger = logging.getLogger("server")
logger.setLevel(logging.INFO)


def example_data():
    return [{"name": "example"}]


def example_vpc_2():
    return [{
        "type": "Theia::Option",
        "label": "Yes",
        "value": "true"
    }, {
        "type": "Theia::Option",
        "label": "No",
        "value": "false"
    }]


def pp(d):
    if 'RAPIDCLOUD_TEST_MODE_AWS_EVENTBRIDGE' in os.environ and os.environ.get('RAPIDCLOUD_TEST_MODE_AWS_EVENTBRIDGE') == "true":
        print(pprint.pformat(d))


def module_eventbridge(boto3_session, user_session, params):
    metadata_dict = module_eventbridge_metadata(boto3_session, user_session, 'create_eventbus', 'eventbus')
    output_list = []
    for fqn, cluster_name in metadata_dict.items():
        output_dict = {}
        output_dict['value'] = {}
        output_dict['type'] = "Theia::Option"
        output_dict['label'] = cluster_name
        output_dict['value']['type'] = "Theia::DataOption"
        output_dict['value']['value'] = cluster_name
        output_list.append(output_dict)
    return output_list


def module_eventbus_aws_auth(boto3_session, user_session, params):
    metadata_list = []
    d = boto3_session.resource('dynamodb')
    try:
        cmdfilter = Attr('profile').eq(user_session["env"]) & Attr('command').eq('manage_aws_auth')
        t = d.Table('aws_infra')
        r = t.scan(FilterExpression=cmdfilter)
        for i in r['Items']:
            metadata_list.append(format_eventbus_aws_auth_metadata(i))
        while 'LastEvaluatedKey' in r:
            r = t.scan(FilterExpression=cmdfilter, ExclusiveStartKey=r['LastEvaluatedKey'])
            for i in r['Items']:
                metadata_list.append(format_eventbus_aws_auth_metadata(i))
    except Exception as e:
        print(e)
    return metadata_list




def module_eventbus_metadata(boto3_session, user_session, cmd):
    # this is a generic function, it queries the aws_infra tables and filters results
    # based on "cmd"
    # when we create subnets, we give the user the option to create a route table
    # with the subnet OR use an existing subnet.
    # when we list route tables from our metadata we pass the `create_subnet` cmd
    # which means that some subnets will end up listed in the route table drop down
    # when `route_tables`is set to True we only include subnets if the `create_route_table`
    # is set to true
    metadata_dict = {}
    d = boto3_session.resource('dynamodb')
    try:
        cmdfilter = Attr('profile').eq(user_session["env"]) & Attr('command').eq(cmd) & Attr('phase').eq(phase)
        t = d.Table('aws_infra')
        r = t.scan(FilterExpression=cmdfilter)
        for i in r['Items']:
            metadata_dict[i['fqn']] = i['resource_name']

        while 'LastEvaluatedKey' in r:
            r = t.scan(FilterExpression=cmdfilter, ExclusiveStartKey=r['LastEvaluatedKey'])
            for i in r['Items']:
                metadata_dict[i['fqn']] = i['resource_name']
    except Exception as e:
        print(e)
    sorted_metadata_tuple = sorted(metadata_dict.items(), key=lambda x: x[1])
    sorted_metadata_dict = {k: v for k, v in sorted_metadata_tuple}
    return sorted_metadata_dict


def module_eventbus(boto3_session, user_session, params):
    metadata_dict = module_eventbus_metadata(boto3_session, user_session, 'create_event_rule')
    aws_dict = {}
    output_list = []
    events_client = boto3_session.client('events')

    try:
        #f = [{'Name': 'tag:profile', 'Values': [user_session['env']]}]
        r = events_client.list_event_buses()
        print(r)
        #for vpc in r['Vpcs']:
        #    for tag in vpc['Tags']:
        #        if tag['Key'] == 'fqn':
        #            aws_dict[tag['Value']] = vpc['VpcId']

    except Exception as e:
        print(e)

    for eventbus in r['EventBuses']():
        output_dict = {}
        output_dict['value'] = {}
        output_dict['type'] = "Theia::Option"
        output_dict['label'] = label
        output_dict['value']['type'] = "Theia::DataOption"
        output_dict['value']['value'] = eventbus['Name']
        output_list.append(output_dict)
    return output_list


def custom_endpoint(action, params, boto3_session, user_session):
    if action == "example":
        return example_data()
    elif action == "module_eventbus":
        return module_eventbus(boto3_session, user_session, params)
    elif action == "module_eks_vpcs":
        return module_eks_vpcs(boto3_session, user_session, params)
    else:
        return ["no such endpoint"]

    return []
