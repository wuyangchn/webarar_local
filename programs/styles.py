"""
存放显示内容样式，如表头，颜色，字体等
"""

NEW_SAMPLE_INTERCEPT_HEADERS = [
    'Sequence', '', '36Ar', '1σ', '37Ar', '1σ', '38Ar', '1σ', '39Ar', '1σ', '40Ar', '1σ'
]
NEW_BLANK_INTERCEPT_HEADERS = [
    'Sequence', '', '36Ar', '1σ', '37Ar', '1σ', '38Ar', '1σ', '39Ar', '1σ', '40Ar', '1σ'
]
NEW_PARAMS_HEADERS = []

SAMPLE_INTERCEPT_HEADERS = [
    'Sequence', '', '36Ar', '1σ', '37Ar', '1σ', '38Ar', '1σ', '39Ar', '1σ', '40Ar', '1σ'
]
BLANK_INTERCEPT_HEADERS = [
    'Sequence', '', '36Ar', '1σ', '37Ar', '1σ', '38Ar', '1σ', '39Ar', '1σ', '40Ar', '1σ'
]

CORRECTED_HEADERS = [
    'Sequence', '', '36Ar', '1σ', '37Ar', '1σ', '38Ar', '1σ', '39Ar', '1σ', '40Ar', '1σ'
]

DEGAS_HEADERS = [
    'Sequence', '', '36Ara', '1σ', '36Arc', '1σ', '36ArCa', '1σ', '36ArCl', '1σ',  # 0-9
    '37ArCa', '1σ',  # 10-11
    '38ArCl', '1σ', '38Ara', '1σ', '38Arc', '1σ', '38ArK', '1σ', '38ArCa', '1σ',  # 12-21
    '39ArK', '1σ', '39ArCa', '1σ',  # 22-25
    '40Arr', '1σ', '40Ara', '1σ', '40Arc', '1σ', '40ArK', '1σ'  # 26-33
]

PARAMS_TABLE_HEADERS = []

PUBLISH_TABLE_HEADERS = [
    'Sequence', '', '36Ara', '37ArCa', '38ArCl', '39ArK', '40Arr', 'Age', '1σ', '40Arr%', '39ArK%', 'Ca/K', '1σ'
]
SPECTRUM_TABLE_HEADERS = ['40/39', '1σ', 'Age', '1σ', '1σ', '1σ', '∑40Arr%', '∑39Ark%']
ISOCHRON_TABLE_HEADERS = [
    'Sequence', '', 'Mark',  # 0-2
    '39/36', '1σ', '40/36', '1σ', 'ri', '', '39/40', '1σ', '36/40', '1σ', 'ri', '',  # 3-14
    '39/38', '1σ', '40/38', '1σ', 'ri', '', '39/40', '1σ', '38/40', '1σ', 'ri', '',  # 15-26
    '38/39', '1σ', '40/39', '1σ', 'ri', '',  # 27-32
    '36/39', '1σ', '38/39', '1σ', '40/39', '1σ'  # 33-39
]
TOTAL_PARAMS_HEADERS = [
    'Sequence', '',  # 0-1
    '(40Ar/36Ar)t', '%1σ', '(40Ar/36Ar)c', '%1σ',  # 2-5
    '(38Ar/36Ar)t', '%1σ', '(38Ar/36Ar)c', '%1σ',  # 6-9
    '(39Ar/37Ar)Ca', '%1σ', '(38Ar/37Ar)Ca', '%1σ', '(36Ar/37Ar)Ca', '%1σ',  # 10-15
    '(40Ar/39Ar)K', '%1σ', '(38Ar/39Ar)K', '%1σ',  # 16-19
    '(36Ar/38Ar)Cl', '%1σ',  # 20-21
    'K/Ca', '%1σ', 'K/Cl', '%1σ', 'Ca/Cl', '%1σ',  # 22-27
    'Cycle Number', 'Irradiation Cycles',  # 28-29
    'Irradiation', 'duration', 'Irradiation Time', 'Experiment Time',  # 30-33
    'Extrapolate', '',  # 34-35
    'Decay Constant 40K', '%1σ',  # 36-37
    'Decay Constant 40K(EC)', '%1σ',  # 38-39
    'Decay Constant 40K(B-)', '%1σ',  # 40-41
    'Decay Constant 40K(B+)', '%1σ',  # 42-43
    'Decay Constant 39Ar', '%1σ',  # 44-45
    'Decay Constant 37Ar', '%1σ',  # 46-47
    'Decay Constant 36Cl', '%1σ',  # 48-49
    'Decay Activity 40K', '%1σ',  # 50-51
    'Decay Activity 40K(EC)', '%1σ',  # 52-53
    'Decay Activity 40K(B-)', '%1σ',  # 54-55
    'Decay Activity 40K(B+)', '%1σ',  # 56-57
    '36/38Cl Productivity', '%1σ',  # 58-59
    'Std Name', 'Std Age', '1σ', '40Ar%', '1σ', 'K%', '1σ', '40Ar*/K', '1σ',  # 60-68
    'J', '%1σ', 'MDF', '%1σ',  # 69-72
    'Mass 36', '%1σ', 'Mass 37', '%1σ', 'Mass 38', '%1σ', 'Mass 39', '%1σ', 'Mass 40', '%1σ', 'K Mass', '%1σ',  # 73-84
    'No', '%1σ', 'Year', '%1σ', '40K/K', '%1σ', '35Cl/37Cl', '%1σ', 'HCl/Cl', '%1σ',  # 85-94
    '40Ar/36Ar air', '%1σ', '38Ar/36Ar air', '%1σ',  # 95-98
    'Isochron Fitting', 'Convergence', 'Iteration', 'Discrimination',  # 99-102
    'Not Zero', 'CorrBlank', 'CorrDiscr', 'Corr37ArDecay', 'Corr39ArDecay',  # 103-107
    'K Degassing', 'Ca Degassing', 'Air Degassing', 'Cl Degassing',  # 108-111
    'Using Min Equation', 'Recalibration', 'Using Std Age', 'Use Std Ratio',  # 112-115
    'Auto Plateau Method',   # 116
]
