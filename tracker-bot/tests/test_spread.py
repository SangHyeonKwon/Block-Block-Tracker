"""스프레드 계산 테스트."""

from monitor.spread import calc_kimchi_premium, calc_basis


def test_kimchi_premium_positive():
    """국내가 해외보다 비쌀 때 양수."""
    result = calc_kimchi_premium(
        krw_price=135_000_000,
        usd_price=100_000,
        usd_krw=1_300,
    )
    # 135M / (100K * 1300) = 135M / 130M = 1.0384... → ~3.85%
    assert result > 0
    assert abs(result - 3.846) < 0.01


def test_kimchi_premium_negative():
    """해외가 국내보다 비쌀 때 음수."""
    result = calc_kimchi_premium(
        krw_price=125_000_000,
        usd_price=100_000,
        usd_krw=1_300,
    )
    assert result < 0


def test_kimchi_premium_zero_price():
    """가격이 0일 때 0 반환."""
    assert calc_kimchi_premium(0, 100_000, 1_300) == 0.0
    assert calc_kimchi_premium(135_000_000, 0, 1_300) == 0.0


def test_basis_negative():
    """선물 < 현물 → 역현선."""
    result = calc_basis(spot_usd=100_000, futures_usd=99_000)
    assert result < 0
    assert abs(result - (-1.0)) < 0.01


def test_basis_positive():
    """선물 > 현물 → 정상."""
    result = calc_basis(spot_usd=100_000, futures_usd=100_500)
    assert result > 0


def test_basis_zero_spot():
    assert calc_basis(spot_usd=0, futures_usd=100) == 0.0
