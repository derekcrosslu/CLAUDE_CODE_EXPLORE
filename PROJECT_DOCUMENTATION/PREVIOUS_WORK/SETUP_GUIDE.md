# Setup Guide: QuantConnect Autonomous System

## Prerequisites

### 1. QuantConnect Account
- Sign up at https://www.quantconnect.com
- Get your API credentials from Account → API
- Set in `.env` file (already configured)

### 2. Python Environment

**Required Python version**: 3.8+

**Required packages**:
```bash
# Install dependencies (choose one method):

# Method 1: Using virtual environment (RECOMMENDED)
python3 -m venv venv
source venv/bin/activate
pip install requests python-dotenv

# Method 2: Using pipx (for system-wide tools)
brew install pipx
pipx install requests python-dotenv

# Method 3: System-wide with flag (use cautiously)
pip install requests python-dotenv --break-system-packages
```

## Installation

### Step 1: Verify Credentials

Check `.env` file contains:
```bash
QUANTCONNECT_USER_ID="your_user_id"
QUANTCONNECT_API_TOKEN="your_api_token"
```

### Step 2: Install Dependencies

```bash
# Recommended: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install requests python-dotenv
```

### Step 3: Test Wrapper

```bash
# Test help
python3 qc_backtest.py --help

# List projects
python3 qc_backtest.py --list
```

## Usage

### Quick Test: Run Complete Workflow

```bash
# Create project + upload strategy + run backtest
python3 qc_backtest.py --run \
    --name "TestStrategy" \
    --file test_strategy.py \
    --output results.json
```

### Individual Commands

**Create Project**:
```bash
python3 qc_backtest.py --create --name "MyStrategy"
```

**Submit Backtest** (existing project):
```bash
python3 qc_backtest.py --backtest --project-id 12345
```

**Check Status**:
```bash
python3 qc_backtest.py --status \
    --project-id 12345 \
    --backtest-id abc123
```

**Get Results**:
```bash
python3 qc_backtest.py --results \
    --project-id 12345 \
    --backtest-id abc123 \
    --output results.json
```

## Output Format

The wrapper returns structured JSON:

```json
{
  "success": true,
  "backtest_id": "abc123",
  "project_id": 12345,
  "performance": {
    "sharpe_ratio": 1.23,
    "max_drawdown": 0.15,
    "total_return": 0.25,
    "win_rate": 0.55
  },
  "trading": {
    "total_trades": 87,
    "average_win": 0.03,
    "average_loss": -0.02
  },
  "risk": {
    "alpha": 0.05,
    "beta": 0.95,
    "volatility": 0.18
  }
}
```

## Integration with Autonomous Workflow

The wrapper is designed to be called from Claude Code during autonomous operation:

```python
# Autonomous backtest execution
result = subprocess.run([
    "python3", "qc_backtest.py",
    "--run",
    "--name", f"Hypothesis_{hypothesis_id}",
    "--file", "strategy.py",
    "--output", f"backtest_results/h{hypothesis_id}_run1.json"
], capture_output=True, text=True)

# Parse results
with open(f"backtest_results/h{hypothesis_id}_run1.json") as f:
    metrics = json.load(f)

# Make autonomous decision
if metrics["performance"]["sharpe_ratio"] >= 1.0:
    decision = "PROCEED_TO_VALIDATION"
elif metrics["performance"]["sharpe_ratio"] >= 0.7:
    decision = "PROCEED_TO_OPTIMIZATION"
else:
    decision = "ABANDON_HYPOTHESIS"
```

## Troubleshooting

### Error: "requests library not installed"
```bash
# Activate virtual environment
source venv/bin/activate

# Install requests
pip install requests
```

### Error: "QuantConnect credentials not found"
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env

# Should show:
# QUANTCONNECT_USER_ID="..."
# QUANTCONNECT_API_TOKEN="..."
```

### Error: "Backtest timed out"
```bash
# Increase timeout (default 300s)
# Edit qc_backtest.py, line with wait_for_backtest():
# timeout=600  # 10 minutes
```

## Next Steps

1. **Test wrapper manually** (Week 1, Day 3-4)
   - Run `--list` command
   - Run `--run` with test_strategy.py
   - Verify JSON output

2. **Manual workflow test** (Week 1, Day 5-7)
   - Select simple hypothesis
   - Execute full cycle manually
   - Validate decision framework

3. **Build plugin** (Week 2+)
   - Create `/qc-backtest` command
   - Integrate wrapper into plugin
   - Add state management

## References

- **qc_backtest.py**: Wrapper script
- **test_strategy.py**: Sample strategy for testing
- **.env**: API credentials
- **autonomous_decision_framework.md**: Decision logic
- **autonomous_workflow_architecture.md**: Complete workflow
