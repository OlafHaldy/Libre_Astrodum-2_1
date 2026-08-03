"""
Liber Astrodum — zodiac.py
Константы Зодиака.
"""

ZODIAC = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

SIGN_ELEMENT = {
    'Aries':'Fire','Leo':'Fire','Sagittarius':'Fire',
    'Taurus':'Earth','Virgo':'Earth','Capricorn':'Earth',
    'Gemini':'Air','Libra':'Air','Aquarius':'Air',
    'Cancer':'Water','Scorpio':'Water','Pisces':'Water'
}

SIGN_MODE = {
    'Aries':'Cardinal','Cancer':'Cardinal','Libra':'Cardinal','Capricorn':'Cardinal',
    'Taurus':'Fixed','Leo':'Fixed','Scorpio':'Fixed','Aquarius':'Fixed',
    'Gemini':'Mutable','Virgo':'Mutable','Sagittarius':'Mutable','Pisces':'Mutable'
}

SIGN_POLARITY = {
    'Aries':'Positive','Gemini':'Positive','Leo':'Positive','Libra':'Positive','Sagittarius':'Positive','Aquarius':'Positive',
    'Taurus':'Negative','Cancer':'Negative','Virgo':'Negative','Scorpio':'Negative','Capricorn':'Negative','Pisces':'Negative'
}

OPPOSITE_SIGN = {
    'Aries':'Libra','Taurus':'Scorpio','Gemini':'Sagittarius','Cancer':'Capricorn',
    'Leo':'Aquarius','Virgo':'Pisces','Libra':'Aries','Scorpio':'Taurus',
    'Sagittarius':'Gemini','Capricorn':'Cancer','Aquarius':'Leo','Pisces':'Virgo'
}
