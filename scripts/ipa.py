#!/usr/bin/env python

# IPA Zounds, a sound change engine with support for the IPA.
# Copyright (C) 2003 Jamie Norrish
#
# This file is part of IPA Zounds.
#
# IPA Zounds is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPA Zounds is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPA Zounds; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""This is the IPA command line program for IPA Zounds."""

import codecs
from argparse import ArgumentParser, FileType
import os
import sys

import zounds
import zounds.word
import zounds.applier
import zounds.ruleset_parser
import zounds.binary_features_model_parser
from zounds import __version__


class CLIParameterError(ValueError):
    """A command line parametr had an invalid value."""


def main ():
    """Command line handling."""
    version = '%prog ' + __version__
    parser = ArgumentParser(description="An IPA-aware sound change applier")
    parser.add_argument('lexicon', type=FileType('r'))
    parser.add_argument('ruleset', type=FileType('r'))
    parser.add_argument('--features', type=FileType('r'),
                        default=None, help="Parse this file for binary features")
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('-b', '--brackets', action='store_const',
                      const='bracket_input', dest='format',
                      help=('bracket input words'))
    parser.add_argument('-d', '--dialect', metavar='DIALECT',
                      dest='dialect', default=None,
                      help=('specify DIALECT (abbreviated form) of output'))
    parser.add_argument('-e', '--end-date', type=int, metavar='END DATE',
                      dest='end_date', default=None,
                      help=('specify END DATE of transformation'))
    parser.add_argument('-f', '--file', dest='filename', metavar='FILE',
                      help=('write output to FILE'))
    parser.add_argument('-l', '--omit', action='store_const',
                      const='omit_input', dest='format',
                      help=('omit input words'))
    parser.add_argument('-m', '--max-format', action='store_true',
                      dest='full_format', default=False,
                      help=('format rules fully if -p used'))
    parser.add_argument('-o', '--output-script', metavar='SCRIPT',
                      dest='output_script', default='ipa',
                      help=('show output written in SCRIPT'))
    parser.add_argument('-p', '--history', action='store_const',
                      const='history', dest='format',
                      default='plain', help=('output transformation history'))
    parser.add_argument('-r', '--rule-script', dest='rule_script',
                      metavar='SCRIPT', default='ipa',
                      help=('specify RULESET is written in SCRIPT'))
    parser.add_argument('-s', '--start-date', type=int,
                      metavar='START DATE', dest='start_date', default=None,
                      help=('specify START DATE of transformation'))
    parser.add_argument('-v', '--reverse', dest='reverse', action='store_true',
                      default=False, help=('perform reverse derivation'))
    parser.add_argument('-w', '--word-script', dest='word_script',
                      metavar='SCRIPT', default='ipa',
                      help=('specify LEXICON is written in SCRIPT'))
    options = parser.parse_args()
    if options.features is None:
        from zounds.clpa import cltsfeaturemodel as features
    else:
        features = (
            zounds.binary_features_model_parser.
            BinaryFeaturesModelParser().parse(
                options.features.read()))
    rules = zounds.ruleset_parser.RulesetParser(features).parse(
        options.ruleset.read())
    print(vars(rules))

    lexicon = list(get_lexicon(options.lexicon, rules.languages))

    applier = zounds.applier.Applier(rules)
    for word in applier.transform_lexicon(lexicon):
        print(word)


def get_lexicon(wordlist, languages):
    """Read LingPy file into lexicon."""
    import pandas
    words = pandas.read_csv(wordlist, sep="\t")
    langs = {language.name: (language, language.dates[-1])
             for language in languages}
    for e, entry in words.iterrows():
        try:
            language, most_recent = langs[entry["DOCULECT_ID"]]
        except KeyError:
            continue
        yield zounds.word.Word(list(entry["IPA"]),
                               language,
                               most_recent)
   

if __name__ == '__main__':
    main()
