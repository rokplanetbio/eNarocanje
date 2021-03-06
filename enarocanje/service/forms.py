from bootstrap_toolkit.widgets import BootstrapTextInput
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Textarea
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from enarocanje.common.timeutils import is_overlapping
from enarocanje.common.widgets import BootstrapDateInput
from models import Service, Discount, Comment

class DiscountForm(ModelForm):
    valid_from = forms.DateField(widget=BootstrapDateInput(), label=_('Discount valid from'))
    valid_to = forms.DateField(widget=BootstrapDateInput(), label=_('Discount valid to'))

    def clean_valid_to(self):
        data = self.cleaned_data['valid_to']
        if not data:
            return data
        if not self.cleaned_data.get('valid_from'):
            return data
        if data and data <= self.cleaned_data['valid_from']:
            raise ValidationError(_('Discount can\'t end before it starts.'))
        return data

    class Meta:
        model = Discount
        # all fields except service
        exclude = ('service', )

class DiscountBaseFormSet(BaseInlineFormSet):

    def clean(self):
        intervals = []
        for form in self.forms:
            valid_from = form.cleaned_data.get('valid_from')
            valid_to = form.cleaned_data.get('valid_to')
            if valid_from and valid_to:
                for valid_from2, valid_to2 in intervals:
                    if is_overlapping(valid_from, valid_to, valid_from2, valid_to2):
                        raise ValidationError(_('Discounts can\'t overlap.'))
                intervals.append((valid_from, valid_to))

class ServiceForm(ModelForm):

    """Form for adding and editing services"""
    active_until = forms.DateField(widget=BootstrapDateInput(), required=False, label=_('Active until'))

    class Meta:
        model = Service
        # all fields except service_provider (you can only create your own services)
        exclude = ('service_provider',)

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['duration'].label = _('Duration (in minutes)')
        self.fields['price'].label = _('Price (in EUR)')

DiscountFormSet = inlineformset_factory(Service, Discount, form=DiscountForm, formset=DiscountBaseFormSet, extra=1)

class FilterForm(forms.Form):
    ACTIVE_CHOICES = (
        ('all', _('All')),
        ('active', _('Active')),
        ('inactive', _('Inactive'))
    )

    active = forms.ChoiceField(choices=ACTIVE_CHOICES, label='')

    def __init__(self, *args, **kwargs):
        durations = kwargs.pop('durations')
        discounts = kwargs.pop('discounts')
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['duration'] = forms.ChoiceField(choices=[('all', _('All durations'))] + [(a, '%d min' % a) for a in durations], label='')
        self.fields['discount'] = forms.ChoiceField(choices=[('all', _('All discounts'))] + [(b, '%s' % b) for b in discounts], label='')

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ''

class EmailForm(forms.Form):
    subject = forms.CharField(widget=BootstrapTextInput(attrs={'style':'width:98%'}),label=_('Title'),required=True)
    message = forms.CharField(widget=Textarea(attrs={'style':'width:98%;max-width:98%'}),label=_('Text'),required=True)