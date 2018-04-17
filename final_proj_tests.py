import unittest
from final_proj import *

class TestClasses(unittest.TestCase):

    def test_player(self):
        player =  Player("David Wright", "New York Mets", "Third Baseman", 2018)

        self.assertEqual(player.name, "David Wright")
        self.assertEqual(player.position, "Third Baseman")
        self.assertEqual(player.team, "New York Mets")
        self.assertEqual(player.year_inducted, 2018)
        self.assertEqual(player.__str__(), "David Wright, Third Baseman for the New York Mets (Inducted in 2018)")

    def test_players_table(self):
        conn = sqlite3.connect('baseball.db')
        cur = conn.cursor()

        sql = 'SELECT LastName FROM Players'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Bagwell',), result_list)
        self.assertEqual(len(result_list), 323)

        sql = '''
            SELECT FirstName, LastName, YearInducted
            FROM Players
            WHERE Position = "Pitcher"
            ORDER BY YearInducted DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 79)
        self.assertEqual(result_list[0][1], "Hoffman")
        self.assertEqual(result_list[2][2], 2015)

        conn.close()

    def test_bar_graph(self):
        lst = get_famers_per_team()

        self.assertEqual(len(lst[0]), 54)
        self.assertEqual(lst[0][2], "Baltimore Orioles NL")

    def test_pie_graph(self):
        lst = get_famers_per_position()

        self.assertEqual(len(lst[0]), 13)
        self.assertEqual(lst[0][2], "3rd Baseman")

    def test_line_graph(self):
        lst = get_famers_per_year()

        self.assertEqual(len(lst[0]), 77)
        self.assertEqual(lst[0][2], 1938)

unittest.main()
