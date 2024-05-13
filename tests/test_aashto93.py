# a test suite for the function in aashto93.py

import unittest
import aashto93

class CoreTest(unittest.TestCase):

    def test_serviceability_loss_factor(self):
        self.assertAlmostEqual(-0.2009, aashto93.serviceability_loss_factor(2.5), delta=0.01)

    def test_serviceability_given_axle_load(self):
        self.assertAlmostEqual(4.388, aashto93.serviceability_given_axle_load(30, 1, 3), delta=0.01)

    def test_flexible_equivalent_single_axle_load(self):
        self.assertAlmostEqual(7.9, aashto93.flexible_equivalent_single_axle_load(30000, 1, 2.5, 3), delta=0.1)
        self.assertAlmostEqual(2.08, aashto93.flexible_equivalent_single_axle_load(40000, 2, 2.5, 5), delta=0.1)