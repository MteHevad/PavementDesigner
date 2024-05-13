
import unittest
import solvesection
import app

class CoreTest(unittest.TestCase):
    def test_solve(self):
        table = app.Parametrization._material_table_defaults
        goal_sn = 5.0
        top_3 = solvesection.solve(table, goal_sn)
        self.assertTrue(len(top_3) == 3)
        for section in top_3:
            self.assertAlmostEqual(solvesection.section_sn(section), goal_sn, delta=0.1)
