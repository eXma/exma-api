from collections import defaultdict
from flask.ext.restful import reqparse, unpack, marshal, fields
from functools import wraps
import api.fields as api_fields


class FieldsetMeta(type):
    def __init__(cls, what, bases, attrs):
        super().__init__(what, bases, attrs)
        cls._unbound_fields = None
        cls._metadata_cls = None

    def __call__(cls, *args, **kwargs):
        if cls._unbound_fields is None:
            fields = []
            for name in dir(cls):
                if not name.startswith('_'):
                    unbound_field = getattr(cls, name)
                    if hasattr(unbound_field, 'format') and hasattr(unbound_field, "output"):
                        fields.append((name, unbound_field))
            cls._unbound_fields = fields
        if cls._metadata_cls is None:
            bases = []
            for mro_class in cls.__mro__:
                if 'Meta' in mro_class.__dict__:
                    bases.append(mro_class.Meta)
            cls._metadata_cls = type('Meta', tuple(bases), {})
            # noinspection PyArgumentList
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, name, value):
        """
        Add an attribute to the class, clearing `_unbound_fields` if needed.
        """
        if name == 'Meta':
            cls._metadata_cls = None
        elif not name.startswith('_') and hasattr(value, 'format') and hasattr(value, "output"):
            cls._unbound_fields = None
        type.__setattr__(cls, name, value)

    def __delattr__(cls, name):
        """
        Remove an attribute from the class, clearing `_unbound_fields` if
        needed.
        """
        if not name.startswith('_'):
            cls._unbound_fields = None
        type.__delattr__(cls, name)


class DefaultMeta(object):
    default_fields = None
    default_embedd = None
    fields_kw = "fields"
    embedd_kw = "embedd"


class FieldsetBase(object, metaclass=FieldsetMeta):
    def __init__(self, fields, meta):
        self.meta = meta
        self._fields = fields

        self._nested = self._find_nested()
        self._nested_recursive = self._find_nested_all()
        self._fields_recursive = self._find_fields_all()

        self._default_fields = self._find_default_fields()
        self._default_embedd = self._find_default_embedd()

    def _find_nested(self):
        names = []
        for field in self._fields:
            if getattr(self._fields[field], "_optional_nested", None):
                names.append(field)
        return names

    def _find_nested_all(self):
        names = []
        for name in self._nested:
            names.append(name)
            nested_field = self._fields.get(name)
            if nested_field is not None:
                nested_fieldset = nested_field.nested_fieldset()
                if nested_fieldset is not None:
                    for nested_nest_field_name in nested_fieldset.nested_field_names:
                        names.append("%s.%s" % (name, nested_nest_field_name))
        return names

    def _find_fields_all(self):
        names = []
        for name in self._fields:
            names.append(name)
        for name in self._nested:
            nested_field = self._fields.get(name)
            if nested_field is not None:
                nested_fieldset = nested_field.nested_fieldset()
                if nested_fieldset is not None:
                    for nested_field_name in nested_fieldset.all_field_names:
                        names.append("%s.%s" % (name, nested_field_name))
        return names

    def _find_default_fields(self):
        names = []
        if self.meta is None or self.meta.default_fields is None:
            names.extend(self._fields.keys())
        else:
            names.extend(self.meta.default_fields)
        return set(names)

    def _find_default_embedd(self):
        names = []
        if self.meta is None or self.meta.default_embedd is None:
            names.extend(self._nested)
        else:
            names.extend(self.meta.default_embedd)
        return set(names)

    @property
    def all_field_names(self):
        return self._fields_recursive

    @property
    def nested_field_names(self):
        return self._nested_recursive


class FieldSetParser(object):
    def __init__(self, possible_fields):
        self.possible_fields = set(possible_fields)

    # noinspection PyUnusedLocal
    def __call__(self, value, *args, **kwargs):
        if not isinstance(value, str):
            raise ValueError("Need a str")

        if not len(value):
            return None
        elements = set(value.split(","))
        unknown = elements.difference(self.possible_fields)
        if len(unknown):
            raise ValueError("Unknown fields: %s" % ", ".join(sorted(unknown)))

        return elements


class Fieldset(FieldsetBase):
    Meta = DefaultMeta

    def __init__(self):
        # noinspection PyCallingNonCallable
        meta_obj = self._metadata_cls()
        # noinspection PyArgumentList,PyTypeChecker
        super().__init__(dict(self._unbound_fields), meta=meta_obj)
        self._parser = None

    def _parse_request_overrides(self):
        if self._parser is None:
            parser = reqparse.RequestParser()
            parser.add_argument(self.meta.fields_kw, type=FieldSetParser(self.all_field_names))
            parser.add_argument(self.meta.embedd_kw, type=FieldSetParser(self.nested_field_names))
            self._parser = parser
        result = self._parser.parse_args()
        return getattr(result, self.meta.fields_kw), getattr(result, self.meta.embedd_kw)

    def marshall_dict(self, selected_fields=None, selected_embed=None):
        """
        :type selected_fields: set[str]
        :type selected_embed: set[str]
        """
        result_dict = {}
        if selected_fields is None or len(selected_fields) == 0:
            selected_fields = self._default_fields

        fields_direct = selected_fields.intersection(self._fields.keys())

        if selected_embed is None or len(selected_embed) == 0:
            selected_embed = self._default_embedd

        embed_direct = selected_embed.intersection(fields_direct)

        filtered_nested = defaultdict(set)
        for nested in selected_fields - fields_direct:
            if "." not in nested:
                continue
            field, nested_field = nested.split(".", 1)
            filtered_nested[field].add(nested_field)

        filtered_embedd = defaultdict(set)
        for embed in selected_embed - embed_direct:
            if "." not in embed:
                continue
            field, nested_field = embed.split(".", 1)
            filtered_embedd[field].add(nested_field)

        for field in fields_direct:
            if field in self._nested:
                if field in embed_direct:
                    nested_fieldset = self._fields[field].nested_fieldset()
                    result_dict[field] = fields.Nested(nested_fieldset.marshall_dict(filtered_nested[field],
                                                                                     filtered_embedd[field]),
                                                       **self._fields[field].nested_kwargs())
                else:
                    result_dict[field] = self._fields[field].key_field()
            else:
                result_dict[field] = self._fields[field]

        return result_dict

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            parsed = self._parse_request_overrides()
            marshall_data = self.marshall_dict(*parsed)
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return marshal(data, marshall_data), code, headers
            else:
                return marshal(resp, marshall_data)

        return wrapper

    @classmethod
    def do_marshall(cls, *args, **kwargs):
        return cls(*args, **kwargs)
