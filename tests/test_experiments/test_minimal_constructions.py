from unittest import TestCase
from geompy.experiments.MinimalConstructions.MinimalConstructionsCore import (find_all_constructions_of_length,
                                                                              count_unique_constructions)


class MinimalConstructionsTestCase(TestCase):
    def assertConstructionCountsCorrect(self, constructions_set):
        expected_construction_count_dict = {0: 1, 1: 3, 2: 3, 3: 16}
        constructions_count = count_unique_constructions(constructions_set)
        # Check if expected_construction_count_dict is a subdictionary of constructions_count
        return self.assertDictEqual({**expected_construction_count_dict, **constructions_count}, constructions_count)

    def test_find_all_constructions_length_3_verbose_true_same(self):
        report = find_all_constructions_of_length(3, verbose=False, report=True)
        verbose = find_all_constructions_of_length(3, verbose=True, report=False)
        report_verbose = find_all_constructions_of_length(3, verbose=True, report=True)
        no_report_no_verbose = find_all_constructions_of_length(3, verbose=False, report=False)

        # Make sure sets are equal to each other
        self.assertSetEqual(report, verbose)
        self.assertSetEqual(report, report_verbose)
        self.assertSetEqual(report, no_report_no_verbose)

    def test_find_all_constructions_length_3(self):
        report = find_all_constructions_of_length(3, verbose=False, report=True)
        verbose = find_all_constructions_of_length(3, verbose=True, report=False)
        report_verbose = find_all_constructions_of_length(3, verbose=True, report=True)
        no_report_no_verbose = find_all_constructions_of_length(3, verbose=False, report=False)

        # Make sure all the counts are correct
        self.assertConstructionCountsCorrect(report)
        self.assertConstructionCountsCorrect(verbose)
        self.assertConstructionCountsCorrect(report_verbose)
        self.assertConstructionCountsCorrect(no_report_no_verbose)
