from .constants import BNFM, HAS_FEATURE, INAPPLICABLE_FEATURE, NOT_HAS_FEATURE, SNFM
from .exceptions import IllegalArgumentError, NormalisedFormValueError


class NormalisedForm:

    """Base class for normalised forms.

    A normalised form is a collection of feature values, ordered
    alphabetically by `.Feature` name. It does not explicitly
    reference any other Zounds objects. A normalised form may be
    generated by a `.Character`, by a `.FeatureSet`, by a `.Cluster`
    (adding one or more normalised forms together), or from the string
    output of an `.Applier`.

    Calls to the class constructor will return an instance of the
    appropriate subclass, depending on the normalised form marker.

    """    

    def __init__ (self, normalised_form):
        self._marker = normalised_form[0]
        self._normalised_form = normalised_form[1:]

    def __add__ (self, other):
        if type(self) != type(other):
            # QAZ: error message.
            raise TypeError
        length = len(self)
        if length != len(other):
            # QAZ: error message.
            raise NormalisedFormValueError
        new = []
        # QAZ: raise an error if one of the NormalisedForms contains a
        # homorgranic variable as a feature value. These only occur in
        # normalised forms derived from a feature set, so this should
        # not occur, but it's as well to be sure.
        for i in range(length):
            if self[i] == INAPPLICABLE_FEATURE or \
                    other[i] != INAPPLICABLE_FEATURE:
                new.append(other[i])
            else:
                new.append(self[i])
        return NormalisedForm('{}{}'.format(self._marker, ''.join(new)))

    def __contains__ (self, feature_value):
        return feature_value in self._normalised_form
    
    def __eq__ (self, other):
        if type(self) != type(other):
            return False
        return str(self) == str(other)

    def __getitem__ (self, key):
        return self._normalised_form[key]

    def __len__ (self):
        return len(self._normalised_form)
    
    def __new__ (cls, normalised_form):
        marker = normalised_form[0]
        if marker == BNFM:
            from .base_normalised_form import BaseNormalisedForm
            cls = BaseNormalisedForm
        elif marker == SNFM:
            from .suprasegmental_normalised_form import SuprasegmentalNormalisedForm
            cls = SuprasegmentalNormalisedForm
        else:
            # QAZ: error message.
            raise IllegalArgumentError
        return object.__new__(cls)

    def __str__ (self):
        return '{}{}'.format(self._marker, self._normalised_form)

    def __sub__ (self, other):
        """Returns the result of subtracting `normalised_form` from
        this normalised form, which is the normalised form that, when
        added to `normalised_form`, results in this normalised form.

        Raises `.NormalisedFormValueError` if there is no possible
        normalised form result. This occurs whenever this normalised
        form has a feature value of INAPPLICABLE_FEATURE, and
        `normalised_form` has a different value for that feature.

        :rtype: `.NormalisedForm`

        """
        if type(self) != type(other):
            # QAZ: error message.
            raise TypeError
        length = len(self)
        if length != len(other):
            # QAZ: error message.
            raise NormalisedFormValueError
        new = []
        # QAZ: raise an error if one of the NormalisedForms contains a
        # homorgranic variable as a feature value. These only occur in
        # normalised forms derived from a feature set, so this should
        # not occur, but it's as well to be sure.
        for i in range(length):
            if self[i] == other[i]:
                new.append(INAPPLICABLE_FEATURE)
            elif self[i] == INAPPLICABLE_FEATURE:
                # QAZ: error message.
                raise NormalisedFormValueError
            else:
                new.append(self[i])
        return NormalisedForm('{}{}'.format(self._marker, ''.join(new)))

    def is_empty (self):
        """Returns True if this normalised form consists solely of
        INAPPLICABLE_FEATURE values (ie, it matches an
        empty/non-existent character).

        :rtype: `bool`

        """
        return HAS_FEATURE not in self and NOT_HAS_FEATURE not in self