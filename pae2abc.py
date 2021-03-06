#!/usr/bin/python3
# -*- coding: utf-8 -*-

# A Plaine and Easie Code to ABC music notation converter

# References:
# PAE: http://www.iaml.info/en/activities/projects/plain_and_easy_code
# ABC: http://abcnotation.com/wiki/abc:standard:v2.1
# pae2abc: https://github.com/fjorba/pae2abc

# Released under GPLv3 or later

from __future__ import print_function, division

import os
import sys
import argparse

# Valid characters for each pae element
valid_pae_chars = {
    'bar': ':/',
    'octaves': "',",
    'notes': 'CDEFGAB',
    'clef': 'GgCcFf+-12345',
    'timesig': '12346789/co.',
    'notelength': '0123456789.',
    'accidentals': 'xbnCDEFGAB[]',
    'tune': "CDEFGAB ',0123456789.xbngqr-=/:t+^();{}!fi",
    }

# Valid characters for a few abc elements
valid_abc_chars = {
    'fields': 'XTtBCDFGHIKLMmNOPQRrSsUVWwZ',
    # L, M and K fields do not appear in the next header_fields
    # list because they are created from the original pae value.
    'header_fields': 'XTABCDFGHImNOPRrSUZ',
    # Next body_fields list is somewhat more restricted than the
    # standard one; for simplicity, we only consider those fields
    # not allowed in file header.  As they are hardly conceivable
    # as pae values, this restriction should not be a problem.
    'body_fields': 'NQsVWw',
    'notes': 'CDEFGABcdefgab',
    'accidentals': '^_=',
    }


def clef2abc(pae):
    '''Translate pae clef to abc'''
    pae2abc = {
        # List is short enough, it is easier to be explicit.
        'C1': 'alto1',
        'C2': 'alto2',
        'C3': 'alto3',
        'C4': 'alto4',
        'C5': 'alto5',
        'F1': 'bass1',
        'F2': 'bass2',
        'F3': 'bass3',
        'F4': 'bass4',
        'F5': 'bass5',
        'G1': 'treble1',
        'G2': 'treble2',
        'G3': 'treble3',
        'G4': 'treble4',
        'G5': 'treble5',
        'c2': 'alto-8',
        'f2': 'bass-8',
        'g2': 'treble-8',
        }
    if len(pae) == 3:
        # Either has the correct length, or it is invalid
        shape = pae[0]
        notation = pae[1]
        position = pae[2]
    else:
        # Default values
        shape = 'G'
        notation = '-'
        position = '2'
    clef = shape + position
    if clef in pae2abc:
        abc = pae2abc[clef]
    else:
        abc = pae2abc['G2']	# Default
    if notation == '+':
        abc += ' stafflines=4'	# Old notation
    return abc


def accidentals2abc(pae):
    '''Translate pae accidentals to abc'''
    # TODO: check notes order and maybe choose old modes or explicit notes
    pae2abc = {
        '':   'C',
        'x1': 'G',
        'x2': 'D',
        'x3': 'A',
        'x4': 'E',
        'x5': 'B',
        'x6': 'F#',
        'x7': 'C#',
        'b1': 'F',
        'b2': 'Bb',
        'b3': 'Eb',
        'b4': 'Ab',
        'b5': 'Db',
        'b6': 'Gb',
        'b7': 'Cb',
        }
    if pae:
        pae = pae.replace('[', '').replace(']', '')
        accidental = pae[0]
        notes = pae[1:]
        key = '%s%s' % (accidental, len(notes))
        if key in pae2abc:
            abc = pae2abc[key]
        else:
            abc = pae2abc['']
    else:
        abc = pae2abc['']
    return abc


def timesig2abc(pae):
    '''Translate pae time signature to abc'''
    abc = pae.replace('c', 'C').replace('C/', 'C|')
    return abc


def bar2abc(pae):
    '''Translate pae bars to abc'''
    pae2abc = {
        '/': '|',
        '//': '||',
        '//:': '[|:',
        '://': ':|]',
        '://:': '::',
        }
    if pae in pae2abc:
        abc = pae2abc[pae]
    else:
        abc = pae2abc['/']
    return abc


def notelength2abc(pae):
    '''Translate note lengths bars to abc, using abc 1/4 as base'''
    # Thanks to http://www.asafraction.co.uk/
    pae2abc = {
        '0':    '16',	# longa
        '9...': '15',
        '9..':  '14',
        '9.':   '12',
        '9':    '8',	# breve
        '1...': '15/2',
        '1..':  '7',
        '1.':   '6',
        '1':    '4',	# whole note / semibreve (rodona)
        '2...': '15/4',
        '2..':  '7/2',
        '2.':   '3',
        '2':    '2',	# half-note / minim (blanca)
        '4...': '15/8',
        '4..':  '7/4',
        '4.':   '3/2',
        '4':    '',	# quarter-note / crochet / semminim (negra)
        '8...': '15/16',
        '8..':  '7/8',
        '8.':   '3/4',
        '8':    '/2',	# eighth-note / quaver / fusa /
        '6...': '15/32',
        '6..':  '7/16',
        '6.':   '3/8',
        '6':    '/4',	# 16th-note / semiquaver / semifusa /
        '3...': '15/64',
        '3..':  '7/32',
        '3.':   '3/16',
        '3':    '/8',	# 32nd-note / demisemiquaver
        '5...': '15/128',
        '5..':  '7/64',
        '5.':   '3/32',
        '5':    '/16',	# 64th- note / hemidemisemiquaver
        '7...': '15/256',
        '7..':  '7/128',
        '7.':   '3/64',
        '7':    '/32',	# 128th-note
        }
    if pae in pae2abc:
        abc = pae2abc[pae]
    else:
        abc = pae
    return abc


def tune2abc(pae, number=''):
    '''Translate pae tune to abc'''

    # Set some defaults
    note = ''
    octave = "'"
    slur = False
    trill = False
    chord = False
    beaming = False
    acciaccatura = False
    appoggiatura = False
    rhythmic_model = False
    rhythmic_backup = False
    irregular_group = False

    # Input and output structures are lists.
    pae_list = list(pae)
    abc_list = []
    while pae_list:
        # Main loop parser. Get next pae character and convert it to abc
        c = pae_list.pop(0)
        if c == 'b':
            # flatten
            note = '_'
        elif c == 'x':
            # sharpen
            note = '^'
        elif c == 'n':
            # naturalise
            note = '='
        elif c == 't':
            # trill
            trill = c
        elif c == '+':
            # slur
            slur = c
        elif c == 'g':
            # acciacciatura
            acciaccatura = c
            if pae_list and pae_list[0] == c:
                acciaccatura += pae_list.pop(0)
                beaming = True
        elif c == 'q':
            # appoggiatura
            appoggiatura = c
            if pae_list and pae_list[0] == c:
                appoggiatura += pae_list.pop(0)
                beaming = True
        elif c == '(':
            # This can be either a fermata (includes only one note or
            # rest; accidentals or octave symbols must be outside the
            # parentheses) or an irregular rhythmic group.
            i = 0
            notes = ''
            while pae_list and pae_list[i] != ')' and i < len(pae_list)-1:
                if pae_list[i] in valid_pae_chars['notes'] + '-':
                    notes += pae_list[i]
                i += 1
            if len(notes) == 1:
                # Single note or silence: fermata
                abc_list.append('H')
            else:
                if not number:
                    number = '8'
                irregular_group = number
                abc_list.append('(') # Remember the position where it starts
        elif c == ';':
            # Second number of irregular group
            if pae_list and pae_list[0].isdigit():
                number = pae_list.pop(0)
                # In ABC the order of the numbers is reversed
                irregular_group = '%s:%s' % (number, irregular_group)
        elif c == ')':
            if irregular_group:
                # close irregular group
                if len(irregular_group) == 1:
                    irregular_group = '3'
                # Look for ( to add the pair of p:q numbers
                found = [i for i in range(len(abc_list)) if '(' in abc_list[i]]
                if found:
                    i = found[-1]
                    abc_list[i] = '(%s' % (irregular_group)
                    if not beaming:
                        abc_list[i] += ' '
                irregular_group = ''
                number = '' # Needed?
        elif c == 'i':
            # Repeat last measure
            # Fist, find where bar signs are
            found = [i for i in range(len(abc_list)) if '|' in abc_list[i]]
            if len(found) == 1:
                # If there was a single bar sign, add a -2 (that will
                # become a zero later) as first position.
                found.insert(0, -2)
            # Extract last measure values, excluding bar signs,
            # because they are handled by the /i/ syntax anyway.
            last_measure = abc_list[found[-2]+2:found[-1]]
            abc_list.extend(last_measure)
        elif c == '!':
            # Repetition of notes
            if c in abc_list:
                # A previous ! marks the start position of the group
                # to repeat
                found = abc_list.index(c)
                abc_list.remove(c)
                # Count how many times (how many f) has to be repeated
                n = 0
                while pae_list and pae_list[0] == 'f':
                    pae_list.pop(0)
                    n += 1
                repeat = abc_list[found:] * n
                abc_list.extend(repeat)
            else:
                abc_list.append(c)
        elif c == '{':
            beaming = True
        elif c == '}':
            abc_list.append(' ')
            beaming = False
        elif c == 'r':
            abc_list.append('}')
            beaming = False
        elif c in valid_pae_chars['octaves']:
            # octave
            octave = c
            while pae_list and pae_list[0] in valid_pae_chars['octaves']:
                octave += pae_list.pop(0)
        elif c in valid_pae_chars['notelength']:
            # note length
            number = c
            while pae_list and pae_list[0] in valid_pae_chars['notelength']:
                number += pae_list.pop(0)
            if pae_list and '(' in pae_list[0]:
                irregular_group = number
        elif c == '=':
            # measure rest
            number = ''
            while pae_list and pae_list[0].isdigit():
                number += pae_list.pop(0)
            if number == '1':
                number = ''
            abc_list.append('Z' + number)
            abc_list.append(' ')
            number = ''
        elif c == '-':
            # note rest
            abc_list.append('z' + notelength2abc(number))
            abc_list.append(' ')
        elif c == '^':
            # Chord
            chord = c
        elif c in valid_pae_chars['bar']:
            # bar
            bar = c
            while pae_list and pae_list[0] in valid_pae_chars['bar']:
                bar += pae_list.pop(0)
            abc_list.append(bar2abc(bar))
            abc_list.append(' ')
        elif c in valid_pae_chars['notes']:
            # notes
            if octave == "'":
                note += c
            elif octave == "''":
                note += c.lower()
            elif octave == "'''":
                note += c.lower() + "'"
            elif octave == "''''":
                note += c.lower() + "'''"
            elif octave in [',', ',,', ',,,']:
                note += c + octave
            if number:
                if number.startswith('.'):
                    # That's a syntax error, ignore
                    number = number[1:]
                if rhythmic_model:
                    # A new number signals the end of previous rhythmic model
                    rhythmic_model = None
                    rhythmic_backup = None
                if len(number) > 1:
                    # Start a new rhythmic model pattern
                    rhythmic_model = []
                    for c in number:
                        if c == '.':
                            # Group dot with its preceding value
                            rhythmic_model[-1] += c
                        else:
                            rhythmic_model.append(c)
                    # We need a full [:] backup of the rhythmic model
                    # as we will consume the working copy as we use it.
                    rhythmic_backup = rhythmic_model[:]
                    number = ''
                    note += notelength2abc(rhythmic_model.pop(0))
                else:
                    note += notelength2abc(number)
            elif rhythmic_model or rhythmic_backup:
                if not rhythmic_model:
                    # Model exhausted; start anew
                    rhythmic_model = rhythmic_backup[:]
                note += notelength2abc(rhythmic_model.pop(0))
            if appoggiatura:
                if len(appoggiatura) == 1:
                    note = '{%s}' % (note)
                else:
                    # closed by the next r
                    note = '{%s' % (note)
                appoggiatura = False
            elif acciaccatura:
                if len(acciaccatura) == 1:
                    note = '{/%s}' % (note)
                else:
                    # closed by the next r
                    note = '{/%s' % (note)
                acciaccatura = False
            elif slur or trill or chord:
                # All share the same logic; handle them together.
                # Look for most recent note or silence (for slur only)
                valid_chars = valid_abc_chars['notes']
                if slur:
                    valid_chars +=  'z'
                i = len(abc_list) - 1
                while i >= 0:
                    found = [True for c in abc_list[i]
                             if c in valid_chars]
                    if found:
                        break
                    else:
                        i -= 1
                if i >= 0:
                    if trill:
                        abc_list[i] = 'T%s' % (abc_list[i])
                        trill = False
                    if slur:
                        abc_list[i] = '(%s' % (abc_list[i])
                        note += ')'
                        slur = False
                    if chord:
                        # Leave notes only, remove spaces
                        while abc_list and abc_list[-1] == ' ':
                            abc_list.pop()
                        # Check whether the chord is already opened
                        open_chord = True
                        j = i
                        while j >= 0:
                            if abc_list[j] == '[':
                                # Found a 2 or more notes chord
                                open_chord = False
                                break
                            elif abc_list[j] == ']':
                                break
                            j -= 1
                        if open_chord:
                            abc_list.insert(i, '[')
                            if pae_list:
                                if pae_list[0] == '^':
                                    chord = ''
                                else:
                                    chord = ']'
                        else:
                            chord = ']'
            abc_list.append(note)
            note = ''
            if chord == ']':
                abc_list.append(chord)
                chord = ''
            if not beaming:
                abc_list.append(' ')
    abc = ''.join(abc_list)
    return (abc, number)


def pae2abc(pae, fields={}):
    '''Main converter funcion; split the pae string into header and
    body, and convert them'''

    # Destination structure
    abc = {
        'header': {
            'clef': '',
            'accidentals': '',
            'timesig': '',
            },
        'body': {
            'tune': '',
            }
        }

    # Add pseudo-abc fields
    if not 'X' in fields:
        abc['header']['X'] = 1
    for field in fields:
        abc['header'][field] = fields[field]
    number = ''

    # Split the pae string in header (clef, accidentals and time
    # signature) and body, looping one char at a time.
    pae_list = list(pae)
    while pae_list:
        c = pae_list.pop(0)
        if c == '%':
            value = ''
            while pae_list and pae_list[0] in valid_pae_chars['clef']:
                value += pae_list.pop(0)
            if not abc['header']['clef']:
                abc['header']['clef'] = clef2abc(value)
            else:
                abc['body']['tune'] += '[K: %s] ' % (clef2abc(value))
        elif c == '$':
            value = ''
            while pae_list and pae_list[0] in valid_pae_chars['accidentals']:
                value += pae_list.pop(0)
            if not abc['header']['accidentals']:
                abc['header']['accidentals'] = accidentals2abc(value)
            else:
                abc['body']['tune'] += '[K: %s] ' % (accidentals2abc(value))
        elif c == '@':
            value = ''
            while pae_list and pae_list[0] in valid_pae_chars['timesig']:
                value += pae_list.pop(0)
            if not abc['header']['timesig']:
                abc['header']['timesig'] = timesig2abc(value)
            else:
                abc['body']['tune'] += '[M: %s] ' % (timesig2abc(value))
        elif c == ' ':
            value = ''
            while pae_list and pae_list[0] in valid_pae_chars['tune']:
                value += pae_list.pop(0)
            (tune, number) = tune2abc(value, number)
            abc['body']['tune'] += tune

    # Build a proper abc stanza, filling only those available fields
    out = []
    for field in valid_abc_chars['header_fields']:
        if field in abc['header']:
            out.append('%s: %s' % (field, abc['header'][field]))
    out.append('L: 1/4')
    out.append('M: %s' % (abc['header']['timesig']))
    out.append('K: %s %s' % (abc['header']['accidentals'],
                             abc['header']['clef']))
    out.append('%s' % (abc['body']['tune']))
    for field in valid_abc_chars['body_fields']:
        if field in abc['header']:
            out.append('%s: %s' % (field, abc['header'][field]))
    if args.debug:
        # TODO: change to new syntax (stylesheet?)
        out.append('%%writefields N true')
        out.append('%%annotationfont Courier 11')
        out.append('N: pae: %s' % (pae.replace('%', '')))
        out.append('N: abc: %s' % (abc['body']['tune']))
    out.append('')

    return '\n'.join(out)


def convert_pae_file(filename):
    '''Convert a file with PAE entries, with optional ABC fields'''

    print('%abc-2.1\n')
    n = 0
    pae = ''
    fields = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if len(line) > 2:
                if line[0] in valid_abc_chars['fields'] and line[1] == ':':
                    key = line[0]
                    value = line[2:].strip()
                    fields[key] = value
                elif line[0] == '@' and ':' in line:
                    # Verovio PAE file format
                    key, value = line.split(':', 1)
                    if key == '@clef':
                        pae += '%%%s' % (value)
                    elif key == '@keysig':
                        pae += '$%s' % (value)
                    elif key == '@timesig':
                        pae += '@%s' % (value)
                    elif key == '@data':
                        pae += ' %s' % (value)
                        abc = pae2abc(pae, {})
                        print(abc)
                        fields = {}
                        pae = ''
                elif line[0].startswith('%'):
                    if not 'X' in fields:
                        n += 1
                        fields['X'] = n
                    abc = pae2abc(line, fields)
                    print(abc)
                    fields = {}
    return


def main(args):
    '''Either convert a file or a supplied string as parameter.'''

    if args.file:
        if os.path.isfile(args.file):
            convert_pae_file(args.file)
        else:
            print('Error: %s not found' % (args.file), file=sys.stderr)
            sys.exit(1)
    elif args.pae:
        abc = pae2abc(args.pae)
        print(abc)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Plaine and Easie Code to ABC music notation converter')
    parser.add_argument('-f', '--file',
                        nargs='?',
                        default='',
                        help='input file')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='debug mode')
    parser.add_argument('pae',
                        nargs='?',
                        default='',
                        action='store')
    args = parser.parse_args()
    if not args.file and not args.pae:
        parser.error('Either --file or a pae string are required')

    main(args)
