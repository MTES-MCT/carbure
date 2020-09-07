from core.models import LotValidationError


def eval_node(lot_value, operator, rule_value):
    if operator == 'EQ':
        return lot_value == rule_value
    elif operator == 'GT':
        return lot_value > float(rule_value)
    elif operator == 'LT':
        return lot_value < float(rule_value)
    elif operator == 'GTE':
        return lot_value >= float(rule_value)
    elif operator == 'LTE':
        return lot_value <= float(rule_value)
    elif operator == 'DIFF':
        return lot_value != rule_value
    elif operator == 'IN':
        return lot_value in rule_value.split(',')
    elif operator == 'NIN':
        return lot_value not in rule_value.split(',')
    else:
        raise Exception('Unknown operator %s' % (operator))


def exec_rule(obj, rule):
    lot_value = getattr(obj, rule.condition_col)
    if eval_node(lot_value, rule.condition, rule.condition_value):
        # keep going for second condition
        second_value = getattr(obj, rule.check_col)
        if eval_node(second_value, rule.check, rule.check_value):
            # rule triggered, create error
            LotValidationError.objects.update_or_create(lot=obj, rule=rule)
            return 1
    return 0
