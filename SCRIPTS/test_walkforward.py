#!/usr/bin/env python3
"""
Unit tests for Monte Carlo Walk-Forward Wrapper

Tests all core logic without requiring QC API access:
- Random train/test split generation
- Strategy date modification
- Statistical analysis
- Decision framework
- Parameter stability assessment
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Import functions from wrapper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qc_walkforward_wrapper import (
    generate_random_split,
    modify_strategy_dates,
    analyze_results,
    apply_robustness_decision
)


class TestRandomSplit(unittest.TestCase):
    """Test random train/test split generation"""

    def test_basic_split(self):
        """Test basic 60/40 split"""
        start = datetime(2020, 1, 1)
        end = datetime(2023, 12, 31)
        train_pct = 0.60

        train_start, train_end, test_start, test_end = generate_random_split(
            start, end, train_pct, seed=42
        )

        # Verify types
        self.assertIsInstance(train_start, datetime)
        self.assertIsInstance(train_end, datetime)
        self.assertIsInstance(test_start, datetime)
        self.assertIsInstance(test_end, datetime)

        # Verify ordering
        self.assertLess(train_start, train_end)
        self.assertLess(train_end, test_start)
        self.assertLess(test_start, test_end)

        # Verify train_start >= start and test_end <= end
        self.assertGreaterEqual(train_start, start)
        self.assertLessEqual(test_end, end)

    def test_split_percentages(self):
        """Test that split percentages are approximately correct"""
        start = datetime(2020, 1, 1)
        end = datetime(2023, 12, 31)
        train_pct = 0.60

        train_start, train_end, test_start, test_end = generate_random_split(
            start, end, train_pct, seed=42
        )

        train_days = (train_end - train_start).days + 1  # Inclusive
        test_days = (test_end - test_start).days + 1     # Inclusive

        # For Monte Carlo, train+test uses ~80% of total (with buffer for random sampling)
        # Check that train is 60% of the combined train+test period
        combined_days = train_days + test_days
        actual_train_pct = train_days / combined_days

        self.assertAlmostEqual(actual_train_pct, train_pct, delta=0.05)

    def test_minimum_test_period(self):
        """Test that test period is at least 90 days"""
        # Use 18 months to have enough space after buffer (20% = ~108 days)
        start = datetime(2020, 1, 1)
        end = datetime(2021, 6, 30)  # 18 months (~547 days)
        train_pct = 0.70

        train_start, train_end, test_start, test_end = generate_random_split(
            start, end, train_pct, seed=42
        )

        test_days = (test_end - test_start).days + 1  # Inclusive
        self.assertGreaterEqual(test_days, 90)

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same split"""
        start = datetime(2020, 1, 1)
        end = datetime(2023, 12, 31)
        train_pct = 0.60

        split1 = generate_random_split(start, end, train_pct, seed=42)
        split2 = generate_random_split(start, end, train_pct, seed=42)

        self.assertEqual(split1, split2)

    def test_different_seeds_produce_different_splits(self):
        """Test that different seeds produce different splits"""
        start = datetime(2020, 1, 1)
        end = datetime(2023, 12, 31)
        train_pct = 0.60

        split1 = generate_random_split(start, end, train_pct, seed=42)
        split2 = generate_random_split(start, end, train_pct, seed=123)

        self.assertNotEqual(split1, split2)

    def test_period_too_short_raises_error(self):
        """Test that too short period raises ValueError"""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 31)  # Only 3 months
        train_pct = 0.60

        with self.assertRaises(ValueError):
            generate_random_split(start, end, train_pct, seed=42)


class TestStrategyDateModification(unittest.TestCase):
    """Test strategy date modification via regex"""

    def setUp(self):
        """Create temporary strategy file for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.strategy_file = os.path.join(self.temp_dir, "test_strategy.py")

        # Create sample strategy content
        self.strategy_content = """
class TestStrategy(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2023, 12, 31)
        self.set_cash(100000)

        # Strategy logic here
        pass
"""
        with open(self.strategy_file, 'w') as f:
            f.write(self.strategy_content)

    def tearDown(self):
        """Clean up temp files"""
        if os.path.exists(self.strategy_file):
            os.remove(self.strategy_file)
        os.rmdir(self.temp_dir)

    def test_modify_start_date(self):
        """Test that start date is correctly modified"""
        new_start = datetime(2020, 6, 15)
        new_end = datetime(2021, 12, 31)

        modified = modify_strategy_dates(self.strategy_file, new_start, new_end)

        # Check that new dates are in the modified content
        self.assertIn("self.set_start_date(2020, 6, 15)", modified)
        self.assertNotIn("self.set_start_date(2023, 1, 1)", modified)

    def test_modify_end_date(self):
        """Test that end date is correctly modified"""
        new_start = datetime(2020, 1, 1)
        new_end = datetime(2022, 8, 20)

        modified = modify_strategy_dates(self.strategy_file, new_start, new_end)

        # Check that new dates are in the modified content
        self.assertIn("self.set_end_date(2022, 8, 20)", modified)
        self.assertNotIn("self.set_end_date(2023, 12, 31)", modified)

    def test_modify_both_dates(self):
        """Test that both dates are modified correctly"""
        new_start = datetime(2021, 3, 10)
        new_end = datetime(2022, 11, 25)

        modified = modify_strategy_dates(self.strategy_file, new_start, new_end)

        # Check both dates
        self.assertIn("self.set_start_date(2021, 3, 10)", modified)
        self.assertIn("self.set_end_date(2022, 11, 25)", modified)

        # Old dates should be gone
        self.assertNotIn("2023, 1, 1", modified)
        self.assertNotIn("2023, 12, 31", modified)

    def test_other_code_unchanged(self):
        """Test that other code remains unchanged"""
        new_start = datetime(2020, 1, 1)
        new_end = datetime(2021, 12, 31)

        modified = modify_strategy_dates(self.strategy_file, new_start, new_end)

        # Check that other parts of code are preserved
        self.assertIn("self.set_cash(100000)", modified)
        self.assertIn("class TestStrategy(QCAlgorithm):", modified)
        self.assertIn("# Strategy logic here", modified)


class TestStatisticalAnalysis(unittest.TestCase):
    """Test statistical analysis of Monte Carlo results"""

    def create_sample_results(self, n_runs=10):
        """Create sample results for testing"""
        results = []
        for i in range(n_runs):
            results.append({
                'run': i + 1,
                'train_start': '2020-01-01',
                'train_end': '2021-12-31',
                'test_start': '2022-01-01',
                'test_end': '2023-12-31',
                'train_sharpe': 0.8 + (i * 0.05),  # 0.8 to 1.25
                'test_sharpe': 0.7 + (i * 0.04),   # 0.7 to 1.06
                'degradation': 0.1 + (i * 0.01),   # 0.1 to 0.19
                'best_params': {
                    'rsi_oversold': 35 if i < 7 else 40,  # 70% consensus on 35
                    'use_trend_filter': 0 if i < 8 else 1  # 80% consensus on 0
                },
                'test_trades': 50 + i * 5
            })
        return results

    def test_basic_statistics(self):
        """Test basic statistical calculations"""
        results = self.create_sample_results(10)
        stats = analyze_results(results)

        # Check that all expected keys exist
        self.assertIn('mean_train_sharpe', stats)
        self.assertIn('mean_test_sharpe', stats)
        self.assertIn('mean_degradation', stats)
        self.assertIn('std_degradation', stats)
        self.assertIn('pct_overfit', stats)
        self.assertIn('pct_good', stats)
        self.assertIn('most_common_params', stats)

    def test_mean_calculations(self):
        """Test that mean calculations are correct"""
        results = self.create_sample_results(10)
        stats = analyze_results(results)

        # Calculate expected means
        train_sharpes = [r['train_sharpe'] for r in results]
        expected_mean_train = sum(train_sharpes) / len(train_sharpes)

        self.assertAlmostEqual(stats['mean_train_sharpe'], expected_mean_train, places=3)

    def test_overfitting_detection(self):
        """Test overfitting percentage calculation"""
        # Create results with high degradation
        results = []
        for i in range(10):
            degradation = 0.35 if i < 6 else 0.15  # 60% have >30% degradation
            results.append({
                'run': i + 1,
                'train_start': '2020-01-01',
                'train_end': '2021-12-31',
                'test_start': '2022-01-01',
                'test_end': '2023-12-31',
                'train_sharpe': 1.0,
                'test_sharpe': 1.0 * (1 - degradation),
                'degradation': degradation,
                'best_params': {'rsi_oversold': 35, 'use_trend_filter': 0},
                'test_trades': 50
            })

        stats = analyze_results(results)

        # Should detect 60% overfitting
        self.assertAlmostEqual(stats['pct_overfit'], 0.60, places=2)

    def test_parameter_stability(self):
        """Test parameter stability assessment"""
        results = self.create_sample_results(10)
        stats = analyze_results(results)

        # 70% should choose rsi_oversold=35
        self.assertEqual(stats['most_common_params']['rsi_oversold'], 35)

        # 80% should choose use_trend_filter=0
        self.assertEqual(stats['most_common_params']['use_trend_filter'], 0)


class TestRobustnessDecision(unittest.TestCase):
    """Test robustness decision framework"""

    def test_robust_strategy_decision(self):
        """Test ROBUST_STRATEGY decision"""
        stats = {
            'mean_degradation': 0.12,  # <15%
            'std_degradation': 0.08,   # <10%
            'pct_overfit': 0.05,
            'mean_train_sharpe': 1.2,
            'mean_test_sharpe': 1.05
        }

        decision, reason, recommendation = apply_robustness_decision(stats)

        self.assertEqual(decision, "ROBUST_STRATEGY")
        self.assertIn("Low degradation", reason)
        self.assertIn("excellent generalization", recommendation)

    def test_abandon_strategy_decision(self):
        """Test ABANDON_STRATEGY decision"""
        stats = {
            'mean_degradation': 0.25,
            'std_degradation': 0.15,
            'pct_overfit': 0.60,  # >50%
            'mean_train_sharpe': 1.2,
            'mean_test_sharpe': 0.5
        }

        decision, reason, recommendation = apply_robustness_decision(stats)

        self.assertEqual(decision, "ABANDON_STRATEGY")
        self.assertIn("Overfitting", reason)
        self.assertIn("new hypothesis", recommendation)

    def test_high_risk_decision(self):
        """Test HIGH_RISK decision"""
        stats = {
            'mean_degradation': 0.45,  # >40%
            'std_degradation': 0.12,
            'pct_overfit': 0.20,
            'mean_train_sharpe': 1.2,
            'mean_test_sharpe': 0.66
        }

        decision, reason, recommendation = apply_robustness_decision(stats)

        self.assertEqual(decision, "HIGH_RISK")
        self.assertIn("degradation", reason)
        self.assertIn("caution", recommendation)

    def test_unstable_parameters_decision(self):
        """Test UNSTABLE_PARAMETERS decision"""
        stats = {
            'mean_degradation': 0.20,
            'std_degradation': 0.28,  # >25%
            'pct_overfit': 0.15,
            'mean_train_sharpe': 1.2,
            'mean_test_sharpe': 0.96
        }

        decision, reason, recommendation = apply_robustness_decision(stats)

        self.assertEqual(decision, "UNSTABLE_PARAMETERS")
        self.assertIn("variance", reason)
        self.assertIn("search space", recommendation)

    def test_proceed_with_caution_decision(self):
        """Test PROCEED_WITH_CAUTION decision"""
        stats = {
            'mean_degradation': 0.25,  # 15-40%
            'std_degradation': 0.12,   # <25%
            'pct_overfit': 0.20,       # <50%
            'mean_train_sharpe': 1.2,
            'mean_test_sharpe': 0.90
        }

        decision, reason, recommendation = apply_robustness_decision(stats)

        self.assertEqual(decision, "PROCEED_WITH_CAUTION")
        self.assertIn("Moderate", reason)
        self.assertIn("reasonable", recommendation)

    def test_boundary_conditions(self):
        """Test decision boundary conditions"""
        # Exactly 15% degradation, 10% variance (boundary for ROBUST)
        stats1 = {
            'mean_degradation': 0.15,
            'std_degradation': 0.10,
            'pct_overfit': 0.10
        }
        decision1, _, _ = apply_robustness_decision(stats1)
        # Should NOT be ROBUST (needs < not <=)
        self.assertNotEqual(decision1, "ROBUST_STRATEGY")

        # Just under threshold
        stats2 = {
            'mean_degradation': 0.149,
            'std_degradation': 0.099,
            'pct_overfit': 0.10
        }
        decision2, _, _ = apply_robustness_decision(stats2)
        self.assertEqual(decision2, "ROBUST_STRATEGY")


class TestConfigurationLoading(unittest.TestCase):
    """Test configuration file loading"""

    def setUp(self):
        """Create temp config file"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp files"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_load_valid_config(self):
        """Test loading valid configuration"""
        config_file = os.path.join(self.temp_dir, "test_config.json")
        config_data = {
            "total_period": {"start": "2020-01-01", "end": "2023-12-31"},
            "train_test_split": 0.60,
            "monte_carlo_runs": 10,
            "parameters": [
                {"name": "rsi_oversold", "min": "30", "max": "45", "step": "5"}
            ]
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        from qc_walkforward_wrapper import load_walkforward_config
        config = load_walkforward_config(config_file)

        self.assertEqual(config['train_test_split'], 0.60)
        self.assertEqual(config['monte_carlo_runs'], 10)
        self.assertEqual(len(config['parameters']), 1)

    def test_missing_config_file(self):
        """Test that missing config raises FileNotFoundError"""
        from qc_walkforward_wrapper import load_walkforward_config

        with self.assertRaises(FileNotFoundError):
            load_walkforward_config("nonexistent_config.json")

    def test_invalid_config_missing_fields(self):
        """Test that config missing required fields raises ValueError"""
        config_file = os.path.join(self.temp_dir, "invalid_config.json")
        config_data = {
            "total_period": {"start": "2020-01-01", "end": "2023-12-31"}
            # Missing train_test_split, monte_carlo_runs, parameters
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        from qc_walkforward_wrapper import load_walkforward_config

        with self.assertRaises(ValueError):
            load_walkforward_config(config_file)


def run_tests():
    """Run all tests and provide summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRandomSplit))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyDateModification))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticalAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestRobustnessDecision))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationLoading))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
