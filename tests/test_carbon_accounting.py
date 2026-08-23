"""Tests for carbon accounting calculations."""

import unittest

from src.carbon_accounting import (
    emissions_from_activity,
    emissions_from_sources,
    emissions_intensity,
    emissions_reduction,
    greenhouse_gas_inventory,
    scope_2_emissions,
)


class CarbonAccountingTests(unittest.TestCase):
    def test_emissions_from_activity(self) -> None:
        self.assertEqual(emissions_from_activity(10_000, 0.42), 4_200)

    def test_emissions_from_multiple_sources(self) -> None:
        self.assertEqual(emissions_from_sources([(1_000, 0.20), (500, 0.50)]), 450)

    def test_scope_2_dual_reporting(self) -> None:
        result = scope_2_emissions(
            10_000, location_based_factor=0.42, market_based_factor=0.05
        )
        self.assertEqual(result, {"location_based": 4_200, "market_based": 500})

    def test_inventory_sums_scopes(self) -> None:
        result = greenhouse_gas_inventory(
            {"scope_1": 100, "scope_2": 200, "scope_3": 700}
        )
        self.assertEqual(result["total"], 1_000)

    def test_emissions_intensity(self) -> None:
        self.assertEqual(emissions_intensity(1_000, 2_000_000), 0.0005)

    def test_emissions_reduction(self) -> None:
        self.assertEqual(
            emissions_reduction(1_000, 750),
            {"absolute": 250, "percentage": 0.25},
        )

    def test_negative_activity_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than or equal to zero"):
            emissions_from_activity(-1, 0.42)


if __name__ == "__main__":
    unittest.main()

