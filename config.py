"""Default configuration for the stock analysis tool."""
import os
from dataclasses import dataclass, field

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "cache")


@dataclass
class IndicatorConfig:
    sma_periods: tuple = (20, 50, 200)
    ema_periods: tuple = (12, 26)
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    stochastic_k: int = 14
    stochastic_d: int = 3
    williams_r_period: int = 14
    cci_period: int = 20
    roc_period: int = 12
    adx_period: int = 14
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    keltner_period: int = 20
    keltner_atr_mult: float = 1.5
    atr_period: int = 14
    mfi_period: int = 14
    chaikin_mf_period: int = 20
    donchian_period: int = 20
    regime_adx_threshold: float = 25.0


@dataclass
class SignalConfig:
    trend_weight_trending: float = 0.40
    momentum_weight_trending: float = 0.20
    volume_weight_trending: float = 0.20
    volatility_weight_trending: float = 0.10
    fundamental_weight_trending: float = 0.10
    trend_weight_ranging: float = 0.20
    momentum_weight_ranging: float = 0.30
    volume_weight_ranging: float = 0.20
    volatility_weight_ranging: float = 0.20
    fundamental_weight_ranging: float = 0.10
    time_decay_half_life_days: int = 10


@dataclass
class RiskConfig:
    var_confidence: float = 0.95
    kelly_cap: float = 0.25
    risk_free_rate: float = 0.05


@dataclass
class AppConfig:
    indicator: IndicatorConfig = field(default_factory=IndicatorConfig)
    signal: SignalConfig = field(default_factory=SignalConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    cache_dir: str = ""
    cache_expiry_hours: int = 4
    default_period: str = "1y"
    default_interval: str = "1d"

    def __post_init__(self):
        if not self.cache_dir:
            self.cache_dir = CACHE_DIR
        import os
        os.makedirs(self.cache_dir, exist_ok=True)


CONFIG = AppConfig()
