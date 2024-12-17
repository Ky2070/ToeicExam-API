from django import forms

class ArrayFieldWidget(forms.TextInput):
    def format_value(self, value):
        if value:
            return ', '.join(str(v) for v in value) if isinstance(value, (list, tuple)) else value
        return ''

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            return [x.strip() for x in value.split(',') if x.strip()]
        return [] 