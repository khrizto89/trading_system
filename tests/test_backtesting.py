from services.learning.backtesting import Backtesting
import pandas as pd

def test_backtesting():
    backtester = Backtesting()
    market_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'price': [100 + i * 0.5 for i in range(100)],
        'signal': [{'action': 'BUY'} if i % 10 == 0 else {'action': 'HOLD'} for i in range(100)]
    })
    strategy_params = {'stop_loss_pct': 2, 'take_profit_pct': 4, 'fee_pct': 0.1, 'position_size_pct': 10}
    report = backtester.run_backtest('BTC/USDT', '2023-01-01', '2023-04-10', 10000, strategy_params, market_data)
    print(report)

if __name__ == "__main__":
    test_backtesting()