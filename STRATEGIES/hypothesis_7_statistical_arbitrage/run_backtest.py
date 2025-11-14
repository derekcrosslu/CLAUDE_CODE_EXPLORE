#!/usr/bin/env python3
"""Run backtest for hypothesis 7 - Statistical Arbitrage"""

import sys
import time
import json
from pathlib import Path

# Add SCRIPTS to path
scripts_path = Path(__file__).parent.parent.parent / 'SCRIPTS'
sys.path.insert(0, str(scripts_path))

from qc_api import QuantConnectAPI

def main():
    api = QuantConnectAPI()
    project_id = 26204235

    # Upload main.py
    print('Uploading main.py...')
    main_py_path = Path(__file__).parent / 'main.py'
    with open(main_py_path, 'r') as f:
        content = f.read()

    upload_result = api.upload_file(project_id, 'main.py', content)
    if not upload_result.get('success'):
        print('❌ Upload failed:', upload_result)
        return 1
    print('✅ Upload successful')

    # Compile
    print('\nCompiling project...')
    compile_result = api.compile_project(project_id)
    if not compile_result.get('success'):
        print('❌ Compile request failed:', compile_result)
        return 1

    compile_id = compile_result.get('compileId')
    print(f'✅ Compile ID: {compile_id}')

    # Wait for compilation
    print('\nWaiting for compilation...')
    max_wait = 120
    waited = 0
    while waited < max_wait:
        status = api.read_compile(project_id, compile_id)
        state = status.get('state')
        print(f'  State: {state} ({waited}s elapsed)')

        if state == 'BuildSuccess':
            print('✅ Compilation successful!')
            break
        elif state == 'BuildError':
            print('❌ Compilation failed!')
            logs = status.get('logs', [])
            if logs:
                print('\nCompilation logs:')
                for log in logs:
                    print(f'  {log}')
            else:
                print('  No logs available')
            return 1

        time.sleep(5)
        waited += 5
    else:
        print('⏱️ Compilation timeout after', max_wait, 'seconds')
        return 1

    # Create backtest
    print('\nCreating backtest...')
    backtest_result = api.create_backtest(project_id, compile_id, name='H7_Statistical_Arbitrage_Iter1')
    if not backtest_result.get('success'):
        print('❌ Backtest creation failed:')
        print(json.dumps(backtest_result, indent=2))
        return 1

    backtest_id = backtest_result.get('backtestId')
    print(f'✅ Backtest created: {backtest_id}')
    print(f'   URL: https://www.quantconnect.com/project/{project_id}?b={backtest_id}')

    # Wait for backtest completion
    print('\nWaiting for backtest completion...')
    final_result = api.wait_for_backtest(project_id, backtest_id, timeout=600, poll_interval=10)

    if not final_result.get('success'):
        print('❌ Backtest failed or timed out:')
        print(json.dumps(final_result, indent=2))
        return 1

    # Parse and save results
    print('\n✅ Backtest completed!')
    parsed_result = api.read_backtest_results(project_id, backtest_id)

    # Save to file
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_file = Path(__file__).parent / 'backtest_logs' / f'backtest_iteration_1_{timestamp}.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(parsed_result, f, indent=2)

    print(f'\n📝 Results saved to: {output_file}')

    # Display key metrics
    if parsed_result.get('success'):
        perf = parsed_result.get('performance', {})
        print('\n📊 Key Metrics:')
        print(f'   Sharpe Ratio: {perf.get("sharpe_ratio", "N/A")}')
        print(f'   Max Drawdown: {perf.get("max_drawdown", "N/A")}')
        print(f'   Total Return: {perf.get("total_return", "N/A")}')
        print(f'   Total Trades: {perf.get("total_trades", "N/A")}')
        print(f'   Win Rate: {perf.get("win_rate", "N/A")}')

    return 0

if __name__ == '__main__':
    sys.exit(main())
