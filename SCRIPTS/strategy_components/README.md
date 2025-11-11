# Strategy Component Library

Reusable, modular components for QuantConnect strategy development.

**Progressive Disclosure Pattern**: Browse components with CLI, don't read source code.

## Categories

### indicators/
Technical indicators (RSI, SMA, MACD, Bollinger, ATR, etc.)

**When to use**: Add technical analysis to strategy
**Example**: `add_rsi.py`, `add_sma.py`, `add_macd.py`

### signals/
Entry/exit signal logic (mean reversion, momentum, crossover, etc.)

**When to use**: Define when to enter/exit trades
**Example**: `mean_reversion.py`, `momentum_breakout.py`, `crossover.py`

### risk_management/
Position sizing, stop loss, drawdown control

**When to use**: Control risk and position size
**Example**: `stop_loss.py`, `position_sizing.py`, `max_drawdown.py`

### sentiment/
Kalshi prediction market integration for regime detection

**When to use**: Adapt strategy to market regime
**Example**: `kalshi_regime_detector.py`, `kalshi_fed_hedge.py`

## Usage

### Discovery
```bash
# List all components
./component list

# List components in category
./component list indicators

# Search by keyword
./component search "momentum"
```

### Integration
```bash
# View component code
./component show add-rsi

# Get integration guide
./component explain add-rsi
```

### Beyond MCP Principles

**Do not read component source files directly**. Use:
1. `./component list` - Browse available components
2. `./component show COMPONENT` - View specific component
3. `./component explain COMPONENT` - Get integration instructions

**Progressive Disclosure**: Load only components you need, not entire library.

## Component Structure

Each component is self-contained:
- Docstring with purpose and parameters
- Integration guide in docstring
- Minimal dependencies
- Works independently

## Contributing

When adding components:
1. Self-contained (no external dependencies if possible)
2. Clear docstring with integration guide
3. Follows existing patterns
4. Add to appropriate category
