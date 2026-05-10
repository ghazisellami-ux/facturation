"""
Convertisseur de montants en dinars tunisiens en toutes lettres.
Supporte dinars et millimes.
"""

_UNITS = [
    '', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf',
    'dix', 'onze', 'douze', 'treize', 'quatorze', 'quinze', 'seize',
    'dix-sept', 'dix-huit', 'dix-neuf'
]

_TENS = [
    '', 'dix', 'vingt', 'trente', 'quarante', 'cinquante',
    'soixante', 'soixante', 'quatre-vingt', 'quatre-vingt'
]


def _below_100(n: int) -> str:
    if n < 20:
        return _UNITS[n]
    ten, unit = divmod(n, 10)
    if ten in (7, 9):
        # 70-79 -> soixante-dix..., 90-99 -> quatre-vingt-dix...
        base = _TENS[ten]
        remainder = n - (ten * 10)
        if ten == 7:
            return f"soixante-{_UNITS[10 + remainder]}"
        else:  # 9
            return f"quatre-vingt-{_UNITS[10 + remainder]}"
    if unit == 0:
        if ten == 8:
            return 'quatre-vingts'
        return _TENS[ten]
    if unit == 1 and ten in (2, 3, 4, 5, 6):
        return f"{_TENS[ten]} et un"
    return f"{_TENS[ten]}-{_UNITS[unit]}"


def _below_1000(n: int) -> str:
    if n < 100:
        return _below_100(n)
    hundreds, remainder = divmod(n, 100)
    if hundreds == 1:
        prefix = 'cent'
    else:
        prefix = f"{_UNITS[hundreds]} cent"
    if remainder == 0:
        if hundreds > 1:
            return f"{_UNITS[hundreds]} cents"
        return 'cent'
    return f"{prefix} {_below_100(remainder)}"


def _int_to_words(n: int) -> str:
    if n == 0:
        return 'zero'
    if n < 1000:
        return _below_1000(n)

    parts = []

    # Millions
    millions = n // 1_000_000
    if millions:
        if millions == 1:
            parts.append('un million')
        else:
            parts.append(f"{_below_1000(millions)} millions")
        n %= 1_000_000

    # Milliers
    thousands = n // 1000
    if thousands:
        if thousands == 1:
            parts.append('mille')
        else:
            parts.append(f"{_below_1000(thousands)} mille")
        n %= 1000

    if n:
        parts.append(_below_1000(n))

    return ' '.join(parts)


def amount_to_words(amount: float) -> str:
    """
    Convertit un montant TND en toutes lettres.
    Exemple: 1234.567 -> "mille deux cent trente-quatre dinars et cinq cent soixante-sept millimes"
    """
    # Arrondir à 3 décimales (millimes)
    amount = round(amount, 3)
    dinars = int(amount)
    millimes = round((amount - dinars) * 1000)

    dinars_text = _int_to_words(dinars)
    result = f"{dinars_text} dinar{'s' if dinars > 1 else ''}"

    if millimes > 0:
        millimes_text = _int_to_words(millimes)
        result += f" et {millimes_text} millime{'s' if millimes > 1 else ''}"

    return result
