from rest_framework import serializers
from policies import models
from pyeda.inter import *
import json
import re

class Attribute_categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute_category
        fields = ('description',)

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Operator
        fields = ('description',)

class Cloud_platformSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cloud_platform
        fields = ('description', 'accept_negated_conditions', 'operators', 'attribute_categories')

class Cloud_providerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cloud_provider
        fields = ('description', 'cloud_platform')

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Policy
        fields = ('description', 'cloud_provider')

class And_ruleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.And_rule
        fields = ('policy', 'description', 'enabled', 'conditions')

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Condition
        fields = ('attribute_category', 'attribute', 'operator', 'value', 'description')
