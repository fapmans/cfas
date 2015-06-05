from policies import models
from policies import serializers
import json
import re

def create_and_rules_and_conditions(instance, policy):
    if 'and_rules' in policy: # If there is no and_rules, do nothing
        # Delete all and rules from the database for a Policy ID
        models.And_rule.objects.filter(policy = instance.id).delete()

        for ar in policy['and_rules']:         # For each and rule...
            # Create and_rule in database, associated to the current policy
            enabled = True
            if 'enabled' in ar:
                enabled = ar['enabled']

            data = {
                     "policy": instance,
                     "description": ar['description'],
                     "enabled": enabled,
                   }

            new_ar = models.And_rule.objects.create(**data)

            # Create conditions in database (if they are not already there), and add them to the new_ar
            if 'conditions' in ar:     # If there is no condition, do nothing
                for c in ar['conditions']:
                    num = models.Condition.objects.filter(attribute=c['attribute'], operator=c['operator'], value=c['value'], type=c['type']).count()
                    if num == 0:
                        new_c = models.Condition.objects.create(**c)
                        new_ar.conditions.add(new_c)
                    elif num == 1:
                        old_c = models.Condition.objects.get(attribute=c['attribute'], operator=c['operator'], value=c['value'], type=c['type'])
                        new_ar.conditions.add(old_c)

def export_dnf_policy(policy_id):
    policy = {}
    and_rules = models.And_rule.objects.filter(policy = policy_id).all()
    policy_and_rules = []
    for and_rule in and_rules: # For each and_rule
        if and_rule.enabled:  # If it is enabled
            policy_and_rule = {}
            policy_and_rule['id'] = and_rule.id
            policy_and_rule['description'] = and_rule.description
            policy_and_rule['conditions'] = []
            for cond in and_rule.conditions.all():     # Check all Conditions
                serializer = serializers.ConditionSerializer(cond)
                policy_and_rule['conditions'].append(serializer.data)
            policy_and_rules.append(policy_and_rule)
    policy['and_rules'] = policy_and_rules
    return policy

def search(policy_id, data):
    and_rules = models.And_rule.objects.filter(policy = policy_id).all()
    policy_and_rules = []
    for and_rule in and_rules: # For each and_rule
        if and_rule.enabled:  # If it is enabled
            policy_and_rule = {}
            policy_and_rule['id'] = and_rule.id
            policy_and_rule['description'] = and_rule.description
            policy_and_rule['conditions'] = []

            if data['criteria'] == []:
                all_criteria_matched = False
            else:
                all_criteria_matched = True

            one_criterium_matched = False                # Start with none criterium matched
            for cri_cond in data['criteria']:            # For each criterium
                this_criterium_matched = False               # Start not matching this criterium
                for cond in and_rule.conditions.all():       # For each condition
                    if cri_cond["attribute"] == cond.attribute and cri_cond["operator"] == cond.operator:
                        if (cond.type == 'c' and cri_cond["value"] == cond.value) or cond.type == 'v':
                            one_criterium_matched = True     # At least one criterium matched
                            this_criterium_matched = True    # This criterium matched

                    serializer = serializers.ConditionSerializer(cond)
                    if serializer.data not in policy_and_rule["conditions"]:
                        policy_and_rule["conditions"].append(serializer.data)

                all_criteria_matched = all_criteria_matched and this_criterium_matched # Check if all criteria matched

            if (data['combining_rule'] == "or" and one_criterium_matched) or (data['combining_rule'] == "and" and all_criteria_matched):
                policy_and_rules.append(policy_and_rule)

    return policy_and_rules
