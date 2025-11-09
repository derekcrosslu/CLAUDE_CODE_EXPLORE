---
description: Initialize a new QuantConnect strategy development session
---

Initialize a new autonomous strategy development session with QuantConnect.

This command will:
1. Create a new hypothesis entry
2. Initialize iteration_state.json
3. Set up project structure
4. Create decisions_log.md

**Usage**:
```
/qc-init
```

You will be prompted for:
- Hypothesis name
- Hypothesis description
- Strategy file path (optional, if already exists)
- Project name (optional, will reuse existing if found)

**What happens next**:
- iteration_state.json is created/updated with new hypothesis
- decisions_log.md is initialized
- QuantConnect project is checked (created if needed)
- Status is set to "research" phase

**Example**:
```
/qc-init
> Hypothesis name: MACD Momentum Strategy
> Description: Buy on MACD crossover with volume confirmation
> Strategy file: momentum_strategy.py
> Project name: MACD_Momentum_v1
```

**Output**:
- ✅ Hypothesis initialized
- 📊 iteration_state.json created
- 📝 decisions_log.md ready
- 🚀 Ready for implementation phase
