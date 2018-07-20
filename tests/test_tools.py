"""Tests on toolbox."""

from ifc_datareader.tools import clean_str


class TestTools:

    def test_tools_clean_str(self):

        # cleaning strings
        assert clean_str('G!o"#o$d%&b\'y(e)') == 'Goodbye'
        assert clean_str('*a+n,d-') == 'and'
        assert clean_str('.t/h:a;n<k=s>') == 'thanks'
        assert clean_str('?f@o[r] ^a_l`l') == 'for all'
        assert clean_str('t{h|e} ~fish') == 'the fish'

        # almost nothing to clean
        assert clean_str(
            'The Ultimate Question of Life, the Universe and Everything') == \
            'The Ultimate Question of Life the Universe and Everything'
        # nothing to clean
        assert clean_str('42') == '42'
