from __future__ import annotations


def network_hashrate_hs(difficulty: float, block_time_sec: float = 120.0) -> float:
    if difficulty <= 0 or block_time_sec <= 0:
        return 0.0
    return difficulty / block_time_sec


def estimate_mainchain_solo_xmr_per_day(
    your_hashrate_hs: float,
    difficulty: float,
    expected_reward_atomic: int,
    block_time_sec: float = 120.0,
) -> float:
    """
    Expected main-chain blocks per day if solo at network difficulty (theoretical).
    P2Pool payouts follow the sidechain; this line is a difficulty-based reference.
    """
    nh = network_hashrate_hs(difficulty, block_time_sec)
    if nh <= 0 or your_hashrate_hs <= 0 or expected_reward_atomic <= 0:
        return 0.0
    share = your_hashrate_hs / nh
    blocks_per_day = 86400.0 / block_time_sec
    reward_xmr = expected_reward_atomic / 1e12
    return share * blocks_per_day * reward_xmr


def daily_power_cost_usd(total_watts: float, usd_per_kwh: float) -> float:
    if total_watts <= 0:
        return 0.0
    kwh_per_day = (total_watts / 1000.0) * 24.0
    return kwh_per_day * usd_per_kwh


def net_usd_per_day(gross_xmr: float, xmr_usd: float | None, power_usd: float) -> float | None:
    if xmr_usd is None:
        return None
    return gross_xmr * xmr_usd - power_usd
