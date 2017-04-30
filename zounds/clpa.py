import itertools
import collections

from pyclpa.base import get_clpa
from pyclpa.clts import Clts

from .constants import HAS_FEATURE, INAPPLICABLE_FEATURE, NOT_HAS_FEATURE
from .base_feature import BaseFeature
from .base_character import BaseCharacter
from .spacing_character import SpacingCharacter
from .diacritic_character import DiacriticCharacter
from .suprasegmental_feature import SuprasegmentalFeature
from .suprasegmental_character import SuprasegmentalCharacter
from .binary_features_model import BinaryFeaturesModel


def flip_dict(dict):
    """Generate the reverse lookup of a dict.

    Turn a {value: key} dictionary, with non-unique `key`s, into the
    reverse lookup dictionary {key: [value]}. Every value of the
    resulting dictionary is the list of all values pointing to that
    key in the original dict.

    """
    flipped = {}
    for value, key in dict.items():
        flipped.setdefault(key, []).append(value)
    return flipped


def apply_clts_features(clts=Clts()):
    """Construct a BinaryFeaturesModel from the features in clts.
    """
    model = BinaryFeaturesModel()
    
    SpacingCharacter(model, "'")
    SpacingCharacter(model, " ")
    SpacingCharacter(model, ",")

    characters = {}
    values_are_unique = {}
    for sound, properties in itertools.chain(
            clts.consonants.items(),
            clts.vowels.items(),
            clts.clicks.items()):
        if properties.get('alias'):
            continue
        if len(sound) == 1:
            characters[sound] = BaseCharacter(
                model, sound), properties
            for prop, value in properties.items():
                if value in values_are_unique:
                    if values_are_unique[value] != prop:
                        raise ValueError
                else:
                    values_are_unique[value] = prop

    for group, mods in clts.diacritics.items():
        for mod, properties in mods.items():
            if properties.get('alias'):
                continue
            mod = mod.replace("◌", "")
            if len(mod) == 1:
                characters[mod] = (
                    DiacriticCharacter(model, mod),
                    properties)
            for prop, value in properties.items():
                if value in values_are_unique:
                    if values_are_unique[value] != prop:
                        raise ValueError
                else:
                    values_are_unique[value] = prop

    for mark in clts.markers.items():
        pass

    for tone, properties in clts.tones.items():
        if properties.get('alias'):
            continue
        if len(tone) == 1:
            SuprasegmentalCharacter(model, tone)
            SuprasegmentalFeature(
                model,
                "t{:}".format(properties["start"]))

    props = flip_dict(values_are_unique)
    for prop, values in props.items():
        if len(values) <= 1:
            binary = BaseFeature(
                model, values[0])
            for _, (sound, properties) in characters.items():
                    if prop in properties and properties[prop] == value:
                            v = HAS_FEATURE
                    else:
                        v = NOT_HAS_FEATURE
                    model.set_character_feature_value(
                        sound, binary, v)
        else:
            for value in values:
                binary = BaseFeature(
                    model, value)
                for _, (sound, properties) in characters.items():
                    if prop in properties:
                        if properties[prop] == value:
                            v = HAS_FEATURE
                        else:
                            v = NOT_HAS_FEATURE
                    else:
                        v = INAPPLICABLE_FEATURE
                    model.set_character_feature_value(
                        sound, binary, v)
            if len(values) == 2:
                break

    return model


cltsfeaturemodel = apply_clts_features()
