from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

import jsonschema

from ..exceptions import ValidationError
from .deserializers import deserialize_parameter


def unmarshal_parameters(schema_unmarshaler, parameters, parameter_spec_dicts):
    unmarshaled = defaultdict(dict)
    errors = []

    for index, parameter_spec_dict in enumerate(parameter_spec_dicts):
        name = parameter_spec_dict['name']
        location = parameter_spec_dict['in']

        try:
            value, schema = deserialize_parameter(
                parameters, location, name, parameter_spec_dict
            )
        except KeyError:
            if parameter_spec_dict.get('required', False):
                error = jsonschema.ValidationError(
                    '{!r} is a required in {!r} parameter'.format(
                        name, location
                    ),
                    validator='required',
                    validator_value=True,
                    schema=parameter_spec_dict,
                    schema_path=(index, 'required'),
                    path=(location, name),
                )
                errors.append(error)
        else:
            try:
                value = schema_unmarshaler.unmarshal(value, schema)
            except ValidationError as e:
                for error in e.errors:
                    error.schema_path.extendleft(('schema', index))
                    error.path.extendleft([name, location])
                errors.extend(e.errors)
            else:
                unmarshaled[location][name] = value

    return unmarshaled, errors or None
