#!/usr/bin/env python3
"""
Kalshi CLI - Progressive Disclosure for Prediction Markets

Provides quick access to Kalshi prediction market data with
progressive disclosure pattern.

Usage:
    kalshi --help                  # Show available commands
    kalshi help <component>        # Show JSON help for component
    kalshi --help-component api    # Show detailed API help
    kalshi markets                 # List current markets
    kalshi fed                     # Get Fed rate probabilities
    kalshi vix                     # Get VIX range probabilities
    kalshi regime                  # Get current market regime
    kalshi sentiment               # Get sentiment signal
    kalshi hedge                   # Get Fed hedge recommendation
    kalshi docs <topic>            # Show detailed documentation

Examples:
    kalshi fed                     # Show Fed rate probabilities
    kalshi regime                  # Show market regime classification
    kalshi help api                # Show KalshiAPI help from JSON
    kalshi help regime             # Show regime detector help
    kalshi docs api                # Show API integration guide
"""

import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from SCRIPTS.strategy_components.sentiment import (
        KalshiAPI,
        KalshiRegimeDetector,
        KalshiFedHedge,
        KalshiVolForecast,
        KalshiSentimentMonitor,
        get_regime_signal,
        get_expected_volatility,
        should_hedge_fed
    )
except ImportError as e:
    print(f"Error: Could not import Kalshi components: {e}")
    print("Make sure you're running from the repository root.")
    sys.exit(1)


def show_markets(args):
    """Show available Kalshi markets."""
    print("📊 Kalshi Markets Overview")
    print("=" * 60)
    print()

    kalshi = KalshiAPI()

    try:
        # Get Fed markets
        print("🏦 Federal Reserve Rate Markets:")
        fed_markets = kalshi.get_markets(series_ticker="FED", limit=10)
        if fed_markets:
            for i, market in enumerate(fed_markets[:5], 1):
                ticker = market.get("ticker", "N/A")
                title = market.get("title", "N/A")
                print(f"  {i}. {ticker}")
                print(f"     {title}")
        else:
            print("  No Fed markets available")
        print()

        # Get VIX markets
        print("📈 VIX Volatility Markets:")
        vix_markets = kalshi.get_markets(series_ticker="VIX", limit=10)
        if vix_markets:
            for i, market in enumerate(vix_markets[:5], 1):
                ticker = market.get("ticker", "N/A")
                title = market.get("title", "N/A")
                print(f"  {i}. {ticker}")
                print(f"     {title}")
        else:
            print("  No VIX markets available")
        print()

        print("💡 Use 'kalshi fed' or 'kalshi vix' for probabilities")

    except Exception as e:
        print(f"❌ Error fetching markets: {e}")
        print("💡 Check your internet connection and try again")


def show_fed(args):
    """Show Fed rate probabilities."""
    print("🏦 Federal Reserve Rate Probabilities")
    print("=" * 60)
    print()

    kalshi = KalshiAPI()

    try:
        probs = kalshi.get_fed_rate_probabilities()

        if not probs:
            print("No Fed rate data available")
            return

        # Sort by rate
        sorted_probs = sorted(probs.items(), key=lambda x: float(x[0]))

        print("Rate    Probability")
        print("-" * 25)
        for rate, prob in sorted_probs:
            bar = "█" * int(prob * 40)
            print(f"{rate}%    {prob:6.1%}  {bar}")

        print()

        # Calculate expected direction
        rates = [float(r) for r in probs.keys()]
        most_likely = max(probs.items(), key=lambda x: x[1])[0]
        most_likely_idx = rates.index(float(most_likely))

        hike_prob = sum(probs[str(r)] for r in rates[most_likely_idx + 1:])
        cut_prob = sum(probs[str(r)] for r in rates[:most_likely_idx])

        print(f"Most likely rate: {most_likely}%")
        print(f"Hike probability: {hike_prob:.1%}")
        print(f"Cut probability:  {cut_prob:.1%}")
        print()

        print("💡 Use 'kalshi regime' for regime classification")

    except Exception as e:
        print(f"❌ Error fetching Fed data: {e}")


def show_vix(args):
    """Show VIX range probabilities."""
    print("📈 VIX Volatility Range Probabilities")
    print("=" * 60)
    print()

    kalshi = KalshiAPI()
    vol_forecast = KalshiVolForecast()

    try:
        probs = kalshi.get_vix_range_probabilities()

        if not probs:
            print("No VIX data available")
            return

        print("Range         Probability")
        print("-" * 40)
        for range_name, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(prob * 30)
            print(f"{range_name:12}  {prob:6.1%}  {bar}")

        print()

        # Expected VIX
        expected_vix = vol_forecast.get_expected_vix()
        print(f"Expected VIX: {expected_vix:.1f}")

        # Classify regime
        if expected_vix < 15:
            regime = "LOW (Complacent)"
        elif expected_vix < 20:
            regime = "NORMAL"
        elif expected_vix < 25:
            regime = "ELEVATED (Cautious)"
        else:
            regime = "HIGH (Risk-off)"

        print(f"Vol Regime:   {regime}")
        print()

        print("💡 Use 'kalshi regime' for complete market regime")

    except Exception as e:
        print(f"❌ Error fetching VIX data: {e}")


def show_regime(args):
    """Show current market regime."""
    print("🎯 Market Regime Classification")
    print("=" * 60)
    print()

    detector = KalshiRegimeDetector()

    try:
        regime = detector.get_current_regime()

        print(f"Fed Policy:     {regime['fed']}")
        print(f"Volatility:     {regime['volatility']}")
        print(f"Risk Sentiment: {regime['risk']}")
        print()

        # Position sizing recommendation
        multiplier = detector.get_position_sizing_multiplier()
        print(f"Position Sizing Multiplier: {multiplier:.1f}x")
        print()

        # Interpretation
        print("📝 Interpretation:")
        if regime['risk'] == 'RISK_OFF':
            print("  ⚠️  RISK-OFF regime detected")
            print("  💡 Consider reducing position sizes")
            print("  💡 Increase hedges or defensive positions")
        elif regime['risk'] == 'RISK_ON':
            print("  ✅ RISK-ON regime detected")
            print("  💡 Consider increasing exposure")
            print("  💡 Favorable for risk assets")
        else:
            print("  ➡️  NEUTRAL regime")
            print("  💡 Maintain normal position sizing")

        print()
        print("💡 Use 'kalshi sentiment' for sentiment shifts")

    except Exception as e:
        print(f"❌ Error calculating regime: {e}")


def show_sentiment(args):
    """Show sentiment signal."""
    print("💭 Market Sentiment Analysis")
    print("=" * 60)
    print()

    monitor = KalshiSentimentMonitor()

    try:
        # Update with current data
        monitor.update_probabilities()

        # Get sentiment signal
        signal = monitor.get_sentiment_signal()

        print(f"Fed Signal:     {signal['fed_signal']}")
        print(f"VIX Signal:     {signal['vix_signal']}")
        print(f"Overall:        {signal['overall']}")
        print()

        # Detect shifts
        shifts = monitor.detect_sentiment_shifts(lookback_hours=24)

        if shifts['fed']['significant']:
            print("⚠️  Significant Fed sentiment shift detected!")
            print(f"   Max shift: {shifts['fed']['max_shift']:.1%}")

        if shifts['vix']['significant']:
            print("⚠️  Significant VIX sentiment shift detected!")
            print(f"   Max shift: {shifts['vix']['max_shift']:.1%}")

        if not shifts['fed']['significant'] and not shifts['vix']['significant']:
            print("✅ No significant sentiment shifts (24h)")

        print()
        print("💡 Use 'kalshi docs sentiment' for more details")

    except Exception as e:
        print(f"❌ Error analyzing sentiment: {e}")


def show_hedge(args):
    """Show Fed hedge recommendation."""
    print("🛡️  Fed Event Hedge Analysis")
    print("=" * 60)
    print()

    hedge = KalshiFedHedge()

    try:
        signal = hedge.get_hedge_signal()

        print(f"Should Hedge:   {signal['should_hedge']}")
        print(f"Uncertainty:    {signal['uncertainty']:.1%}")
        print(f"Tail Risk:      {signal['tail_risk']:.1%}")
        print(f"Hedge Ratio:    {signal['hedge_ratio']:.1%}")
        print()

        print(f"Rationale: {signal['rationale']}")
        print()

        if signal['should_hedge']:
            print("💡 Recommendation:")
            print(f"  - Reduce positions by {signal['hedge_ratio']:.0%}")
            print("  - Consider defensive positioning")
            print("  - Monitor Fed communications closely")
        else:
            print("✅ No hedging needed - market expectations clear")

    except Exception as e:
        print(f"❌ Error calculating hedge: {e}")


def show_help(args):
    """Show detailed help from JSON files."""
    component = args.component if hasattr(args, 'component') and args.component else None

    help_dir = Path(__file__).parent.parent / ".claude/skills/kalshi/help"

    if not component:
        # Show index
        index_file = help_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index = json.load(f)

            print("📚 Kalshi CLI Help")
            print("=" * 60)
            print()
            print(f"Version: {index['kalshi_cli']['version']}")
            print(f"Components: {index['kalshi_cli']['components']}")
            print()
            print("Available help topics:")
            print()
            for comp_name, comp_info in index['components'].items():
                print(f"  {comp_name}")
                print(f"    {comp_info['description']}")
                print(f"    File: {comp_info['file']}")
                print()
            print("Usage: kalshi --help <component>")
            print("Example: kalshi --help api")
            print()
            print("Component shortcuts:")
            print("  api        - KalshiAPI")
            print("  regime     - KalshiRegimeDetector")
            print("  fed_hedge  - KalshiFedHedge")
            print("  vol        - KalshiVolForecast")
            print("  sentiment  - KalshiSentimentMonitor")
        else:
            print("📚 Kalshi CLI Help")
            print("=" * 60)
            print()
            print("Available components:")
            print("  api        - KalshiAPI")
            print("  regime     - KalshiRegimeDetector")
            print("  fed_hedge  - KalshiFedHedge")
            print("  vol        - KalshiVolForecast")
            print("  sentiment  - KalshiSentimentMonitor")
            print()
            print("Usage: kalshi --help <component>")
        return

    # Map component shortcuts to help files
    component_map = {
        "api": "kalshi_api.json",
        "regime": "kalshi_regime.json",
        "fed_hedge": "kalshi_fed_hedge.json",
        "vol": "kalshi_vol_forecast.json",
        "sentiment": "kalshi_sentiment.json"
    }

    if component not in component_map:
        print(f"❌ Unknown component: {component}")
        print(f"💡 Use 'kalshi --help' to see available components")
        return

    help_file = help_dir / component_map[component]

    if help_file.exists():
        with open(help_file, 'r') as f:
            help_data = json.load(f)

        print(f"📘 {help_data['component']}")
        print("=" * 60)
        print()
        print(f"File: {help_data['file']}")
        print(f"Description: {help_data['description']}")
        print()

        if 'features' in help_data:
            print("Features:")
            for feature in help_data['features']:
                print(f"  • {feature}")
            print()

        print("Methods:")
        for method_name, method_info in help_data['methods'].items():
            print(f"\n  {method_name}()")
            print(f"    {method_info['description']}")
            if 'returns' in method_info:
                print(f"    Returns: {method_info['returns']}")
            if 'example' in method_info:
                print(f"    Example: {json.dumps(method_info['example'], indent=6)}")

        print()
        if 'usage_example' in help_data:
            print("Usage Example:")
            print("-" * 60)
            print(help_data['usage_example'])
            print()

        if 'caching' in help_data:
            print(f"Caching: {help_data['caching']}")

        if 'helper_function' in help_data:
            print(f"Helper: {help_data['helper_function']}")
    else:
        print(f"📘 Help: {component}")
        print("=" * 60)
        print()
        print(f"Help file not found: {help_file}")
        print()
        print("💡 See SCRIPTS/strategy_components/sentiment/README.md")


def show_docs(args):
    """Show detailed documentation."""
    topic = args.topic if hasattr(args, 'topic') and args.topic else None

    docs_dir = Path(__file__).parent.parent / ".claude/skills/kalshi/reference"

    if not topic:
        print("📚 Kalshi Documentation")
        print("=" * 60)
        print()
        print("Available topics:")
        print()
        print("  api          - API Integration Guide")
        print("  components   - Component Library Overview")
        print("  regime       - Regime Detection Details")
        print("  fed_hedge    - Fed Event Hedging")
        print("  volatility   - Volatility Forecasting")
        print("  sentiment    - Sentiment Monitoring")
        print("  examples     - Strategy Examples")
        print()
        print("Usage: kalshi docs <topic>")
        print("Example: kalshi docs api")
        return

    # Map topics to files
    topic_map = {
        "api": "api_integration.md",
        "components": "component_overview.md",
        "regime": "regime_detection.md",
        "fed_hedge": "fed_hedge.md",
        "volatility": "volatility_forecast.md",
        "sentiment": "sentiment_monitor.md",
        "examples": "strategy_examples.md"
    }

    if topic not in topic_map:
        print(f"❌ Unknown topic: {topic}")
        print(f"💡 Use 'kalshi docs' to see available topics")
        return

    doc_file = docs_dir / topic_map[topic]

    if doc_file.exists():
        with open(doc_file, 'r') as f:
            print(f.read())
    else:
        print(f"📄 Documentation: {topic}")
        print("=" * 60)
        print()
        print(f"Documentation file not found: {doc_file}")
        print()
        print("💡 See SCRIPTS/strategy_components/sentiment/README.md")
        print("   for complete documentation")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Kalshi Prediction Markets CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kalshi markets      # List available markets
  kalshi fed          # Show Fed rate probabilities
  kalshi vix          # Show VIX range probabilities
  kalshi regime       # Show market regime classification
  kalshi sentiment    # Show sentiment analysis
  kalshi hedge        # Show Fed hedge recommendation
  kalshi docs api     # Show API integration docs

For complete documentation:
  cat SCRIPTS/strategy_components/sentiment/README.md
        """
    )

    # Add custom --help flag
    parser.add_argument('--help-component', dest='help_component', metavar='COMPONENT',
                       help='Show detailed help for component (api, regime, fed_hedge, vol, sentiment)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Markets command
    subparsers.add_parser('markets', help='List available Kalshi markets')

    # Fed command
    subparsers.add_parser('fed', help='Show Fed rate probabilities')

    # VIX command
    subparsers.add_parser('vix', help='Show VIX range probabilities')

    # Regime command
    subparsers.add_parser('regime', help='Show market regime classification')

    # Sentiment command
    subparsers.add_parser('sentiment', help='Show sentiment analysis')

    # Hedge command
    subparsers.add_parser('hedge', help='Show Fed hedge recommendation')

    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Show detailed documentation')
    docs_parser.add_argument('topic', nargs='?', help='Documentation topic')

    # Help command (for JSON help files)
    help_parser = subparsers.add_parser('help', help='Show component help from JSON files')
    help_parser.add_argument('component', nargs='?', help='Component name (api, regime, fed_hedge, vol, sentiment)')

    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Handle --help-component flag
    if hasattr(args, 'help_component') and args.help_component:
        # Create an args object for show_help
        help_args = argparse.Namespace(component=args.help_component)
        show_help(help_args)
        sys.exit(0)

    # Route to appropriate handler
    commands = {
        'markets': show_markets,
        'fed': show_fed,
        'vix': show_vix,
        'regime': show_regime,
        'sentiment': show_sentiment,
        'hedge': show_hedge,
        'docs': show_docs,
        'help': show_help
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
