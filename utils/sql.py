def build_values(values):
    if not isinstance(values, list):
        values = [values]

    sql = ','.join('(' + ','.join(quote_value(v) for v in row) + ')' for row in values)
    if sql:
        return 'VALUES ' + sql
    else:
        return None


def quote_value(value):
    if isinstance(value, bool):
        return str(1) if value else str(0)
    if isinstance(value, (int, float)):
        return str(value)
    else:
        return "'%s'" % str(value)

