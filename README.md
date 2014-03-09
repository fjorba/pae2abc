pae2abc
=======

A Plaine and Easie Code to ABC musical notation converter


Introduction
============

Both Plaine an Easie Code (from now, PAE) and ABC were born to allow
musical notation using just alphanumeric characters.  PAE's manifesto
by Barry S. Brook, a musicologist, had the title "Notating Music with
Ordinary Typewriter Characters" (1964), with the stated goal to
identify otherwise ambiguous works in musical library catalogs.  The
idea is that the few first bars of the musical composition, the
musical incipit, should be part of the library catalog, so works with
a identical name could be differentiated if the musical incipit is
known and available.  On the other hand, ABC was designed by Chris
Walshaw, a (at that time) "musically illiterate" musician that was
hitch-hicking around Europe with his rucksack and carrying a flute,
and its first implementation was a computer program released in 1983.
Both are based on the German and Anglo-Saxon tradition of naming the
notes using the first letters of the alphabet, A to G, and share
similar, although not identical, solutions for common situations, like
using the comma (,) and the apostroph (') for designing lower or upper
octaves, or using a similar visual symbol for the bar line: the slash
(/) for PAE and the vertical bar or pipe (|) for ABC.  They also share
another common characteristic: their initial goal is for transcribing
short fragments, and monodic, or single-voice, melodies.  Although ABC
has clearly overcome its initial limitations (most notably abcm2ps),
its software implementations naturaly lead to more compact engraving
representations than other, more ambitious, packages.

PAE has always been used in a niche context, that is, in music library
catalogs, and formalised in scholarly journals and meetings by
musicologists and librarians, while ABC, born in the Internet era by
music aficionados and computer entusiasts, has been discussed in the
open, using mailing lists, web pages, tutorials and forums.  ABC
enjoys a very lively community and a myriad of software packages that
PAE lacks.  Using the classical Eric S. Raymond dichotomy, PAE would
be the cathedral, and ABC the bazaar.

ABC software implementations include editors, converters, engravers,
sound generators, web plugins, etc.  For PAE, only a few converters
exist, and all of them to convert from PAE to some other notation that
can produce a graphical (pentagram) output.


Previous existing converters
============================

In 2003, Rainer Typke released pae2xml, that converts PAE to,
unsurprisingly, MusicXML notation.  It was developed for converting
music incipits as they can be found in the RISM database.  Written in
Perl, it relies heavily on regular expreesions.  Available at
http://rainer.typke.org/pae2xml.html.

Reinhold Kainhofer took pae2xml's maintenance, updated and polished
it, and in 2010 published version 1.0.  Besides general improvements
and fixes, it has gained input file format flexibility and a test
suite.  However, to my taste it is still somewhat unstructured and
difficult to contribute to.  It can be found at
http://repo.or.cz/w/pae2xml.git.

In 2007, Michal Žbodák wrote another converter as part of his master
thesis.  Also written in Perl, incipity.pl converts PAE to Lilypond.
Unfortunately, the variable names and comments are in Slovak, the
program is not particularly well structured, it is written using a CGI
interface, and there are a few hardcoded addresses.  It is available
at http://is.muni.cz/th/60712.

In 2011, Ignacio José Lizarán combined Michal Žbodák's script with
Typke's and Kainhofer's pae2xml.pl, published pae2ly.pl.  It requires
the input file to be coded in Marc21, using 031 subfields.  This
requirement is unsurprising given the niche field PAE is used.
However, the program is written using a mix of English and Spanish,
poorly commented, also with a heavy use of long regular expressions
and, again, not easy to follow.  It is available at
http://sourceforge.net/projects/paetolilypond/.

Finally, there is the pae2kern converter, that takes a PAE notation
file, using a special syntax to code the incipit part, and converts it
to Humdrum.  For printing, Humdrum relies on ABC format, using
abcm2ps.  pae2kern can be found at
http://extra.humdrum.org/man/pae2kern/.


Motivation to write pae2abc
===========================
pae2abc converts PAE musical incipits to ABC, as I think that the ABC
tools are perfectly capable to express all the musical elements
defined in the PAE standard, and its output more appropiate for those
incipits that full score oriented software like Lilypond.  For
example, ABC optional information fields allow abcm2ps to add some
identification fields to the incipit, like the title, the author,
origin, literary incipits or even notes, all in a compact form that is
suitable for music catalogs.  Even more, the style can be changed via
ABC stylesheets.

On the other side, I've tried to write pae2abc as clear and as
explicit as possible, easy to follow, and to contribute to, and to
debug.  I've seen that it is perfectly possible to write such a
converter without resorting to regular expressions, and I hope that
the code legibility benefits from that.

Currently it converts most of the basic constructs (clefs,
accidentals, bars, notes, octaves, rests, beaming, trills, slurs,
acciacciaturas and appoggiaturas, fermatas, etc. but it is not yet
complete.  However, in it current state it can convert in less than 2
minutes about 930.00 incipits from the RISM export database.

TODO: syntax, examples, test suite, irregular groups, chords, etc.
