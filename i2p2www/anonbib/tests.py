#!/usr/bin/python2
# Copyright 2004-2008, Nick Mathewson.  See LICENSE for licensing info.

"""Unit tests for anonbib."""

import BibTeX
import metaphone
#import reconcile
#import writeHTML
#import updateCache

import unittest

class MetaphoneTests(unittest.TestCase):
    def testMetaphone(self):
        pass

class BibTeXTests(unittest.TestCase):
    def testTranslation(self):
        ut = BibTeX.url_untranslate
        self.assertEquals(ut("Fred"),"Fred")
        self.assertEquals(ut("Hello, World."), "Hello_2c_20World.")

        te = BibTeX.TeXescapeURL
        ute = BibTeX.unTeXescapeURL
        self.assertEquals(te("http://example/~me/my_file"),
                          r"http://example/\{}~me/my\_file")
        self.assertEquals(ute(r"http:{}//example/\{}~me/my\_file"),
                          "http://example/~me/my_file")

        h = BibTeX.htmlize
        self.assertEquals(h("Hello, world"), "Hello, world")
        self.assertEquals(h(r"\'a\`e\'{i}(\'\i)\"o&\^u"),
                          "&aacute;&egrave;&iacute;(&iacute;)&ouml;&amp;"
                          "&ucirc;")
        self.assertEquals(h(r"\~n and \c{c}"), "&ntilde; and &ccedil;")
        self.assertEquals(h(r"\AE---a ligature"), "&AElig;&mdash;a ligature")
        self.assertEquals(h(r"{\it 33}"), " 33")
        self.assertEquals(h(r"Pages 33--99 or vice--versa?"),
                          "Pages 33-99 or vice&ndash;versa?")

        t = BibTeX.txtize
        self.assertEquals(t("Hello, world"), "Hello, world")
        self.assertEquals(t(r"\'a\`e\'{i}(\'\i)\"o&\^u"),
                          "aei(i)o&u")
        self.assertEquals(t(r"\~n and \c{c}"), "n and c")
        self.assertEquals(t(r"\AE---a ligature"), "AE---a ligature")
        self.assertEquals(t(r"{\it 33}"), " 33")
        self.assertEquals(t(r"Pages 33--99 or vice--versa?"),
                          "Pages 33--99 or vice--versa?")

    def authorsParseTo(self,authors,result):
        pa = BibTeX.parseAuthor(authors)
        self.assertEquals(["|".join(["+".join(item) for item in
                                     [a.first,a.von,a.last,a.jr]])
                           for a in pa],
                          result)

    def testAuthorParsing(self):
        pa = BibTeX.parseAuthor
        PA = BibTeX.ParsedAuthor
        apt = self.authorsParseTo

        apt("Nick A. Mathewson and Roger Dingledine",
            ["Nick+A.||Mathewson|", "Roger||Dingledine|"])
        apt("John van Neumann", ["John|van|Neumann|"])
        apt("P. Q. Z. de la Paz", ["P.+Q.+Z.|de+la|Paz|"])
        apt("Cher", ["||Cher|"])
        apt("Smith, Bob", ["Bob||Smith|"])
        apt("de Smith, Bob", ["Bob|de|Smith|"])
        apt("de Smith, Bob Z", ["Bob+Z|de|Smith|"])
        #XXXX Fix this.
        #apt("Roberts Smith Wilkins, Bob Z", ["Bob+Z||Smith+Wilkins|"])
        apt("Smith, Jr, Bob", ["Bob||Smith|Jr"])

        #XXXX Fix this.
        #apt("R Jones, Jr.", ["R||Jones|Jr."])
        apt("Smith, Bob and John Smith and Last,First",
            ["Bob||Smith|", "John||Smith|", "First||Last|"])
        apt("Bob Smith and John Smith and John Doe",
            ["Bob||Smith|", "John||Smith|", "John||Doe|"])


if __name__ == '__main__':
    unittest.main()

