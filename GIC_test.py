import textwrap
import unittest
from datetime import date

from beancount import loader
from beancount.parser import cmptest


class testGIC(cmptest.TestCase):

    # Test if the entries are generated properly
    # AccountFrom, Name, Interest Calculations, InterestAccount, Currency, Duration

    def test_GIC(self):
        input_text = textwrap.dedent("""
            plugin "GIC"

            2021-01-02 open Assets:MainBank:Chequing
            2021-01-02 open Income:GIC:Interest

            2021-01-02 custom "GIC" Assets:GIC:Flexible Assets:MainBank:Chequing Income:GIC:Interest 5000 CAD 4.55 12
        """)

        entries, errors, _ = loader.load_string(input_text)
        self.assertFalse(errors)

        self.assertEqualEntries("""

            2021-01-02 open Assets:MainBank:Chequing
            2021-01-02 open Income:GIC:Interest

            2021-01-02 open Assets:GIC:Flexible

            2021-01-02 * 
             Assets:GIC:Flexible 5000 CAD
             Assets:MainBank:Chequing -5000 CAD

            2022-01-02 *
             Assets:MainBank:Chequing 5227.5000 CAD
             Assets:GIC:Flexible -5000 CAD
             Income:GIC:Interest -227.5000 CAD

            2022-01-02 close Assets:GIC:Flexible
        """, entries)
    
    def test_future_entry(self):
        input_text = textwrap.dedent("""
            plugin "GIC"

            2021-01-02 open Assets:MainBank:Chequing
            2021-01-02 open Income:GIC:Interest

        """)

        currYear = date.today().year

        input_text += f"{currYear}-01-02 custom \"GIC\" Assets:GIC:Flexible Assets:MainBank:Chequing Income:GIC:Interest 5000 CAD 2.55 3"

        entries, errors, _ = loader.load_string(input_text)
        self.assertFalse(errors)

        self.assertEqualEntries(f"""
            2021-01-02 open Assets:MainBank:Chequing
            2021-01-02 open Income:GIC:Interest

            {currYear}-01-02 open Assets:GIC:Flexible

            {currYear}-01-02 * 
             Assets:GIC:Flexible 5000 CAD
             Assets:MainBank:Chequing -5000 CAD
        """, entries)

    def test_metadata_preserve(self):
        #Test if metadata is preserved in the open entry
        return


if __name__ == '__main__':
    unittest.main()
