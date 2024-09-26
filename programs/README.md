# ArArPy

ArArPy is a module for the reduction of <sup>40</sup>Ar/<sup>39</sup>Ar 
geochronologic data. 

It packages the whole processing steps, including reading data from local files, 
blank correction, decay correction, interference reactions correction, age 
calculation, isochron regression, etc. 

The current version supports exported files in Thermo Scientific Qtegra (ISDS) 
platform software.

ArArPy is written in Python language combined with some open source packages, 
such as numpy, pandas, os, scipy, pickle, xlrd, xlsxwriter, and json. 

## Installing from PyPI
ArArPy can be installed via pip from PyPI.

    pip install ararpy
    
## API

#### Sample

##### new Sample(**kwargs)

    __init__(
        Doi = "",
        RawData = RawData(),
        Info = Info(),
        SequenceName = [],
        SequenceValue = [],
        SequenceUnit = [],
        NewIntercept = [],
        NewBlank = [],
        NewParam = [],
        SampleIntercept = [],
        BlankIntercept = [],
        AnalysisDateTime = [],
        BlankCorrected = [],
        MassDiscrCorrected = [],
        DecayCorrected = [],
        InterferenceCorrected = [],
        CorrectedValues = [],
        DegasValues = [],
        ApparentAgeValues = [],
        IsochronValues = [],
        TotalParam = [],
        PublishValues = [],
        SelectedSequence1 = [],
        SelectedSequence2 = [],
        UnselectedSequence = [],
        IsochronMark = [],
        UnknownTable = Table(),
        BlankTable = Table(),
        CorrectedTable = Table(),
        DegasPatternTable = Table(),
        PublishTable = Table(),
        AgeSpectraTable = Table(),
        IsochronsTable = Table(),
        TotalParamsTable = Table(),
        AgeSpectraPlot = Plot(),
        NorIsochronPlot = Plot(),
        InvIsochronPlot = Plot(),
        KClAr1IsochronPlot = Plot(),
        KClAr2IsochronPlot = Plot(),
        KClAr3IsochronPlot = Plot(),
        ThreeDIsochronPlot = Plot(),
        CorrelationPlot = Plot(),
        DegasPatternPlot = Plot(),
        AgeDistributionPlot = Plot(),
    )   
    
- ``` Doi``` ``` type: str ""``` ```default: ""```

    Instance id, created by uuid.uuid4().hex.

- ``` RawData ``` ``` type: RawData() ```

    RawData instance, contains information and data of the imported raw files.

- ``` Info ``` ``` type: Info() ```

    Info instance. it may contain:
    
    - ``` attr_name ``` ``` type: str ``` Info
    - ``` id ``` ``` type: str ``` 0
    - ``` name ``` ``` type: str ``` info
    - ``` type ``` ``` type: str ``` Info
    - ``` sample ``` Info instance.
        - ``` name ``` ``` type: str ``` Sample name.
        - ``` material ``` ``` type: str ``` Sample material.
        - ``` location ``` ``` type: str ``` Sample location.
    - ``` researcher ``` Info instance
        - ``` name ``` ``` type: str ``` Researcher name.
        - ``` email ``` ``` type: str ``` Researcher email.
    - ``` laboratory ``` Info instance
        - ``` name ``` ``` type: str ``` Laboratory name.
        - ``` email ``` ``` type: str ``` Laboratory email.
        - ``` addr ``` ``` type: str ``` Laboratory address.
        - ``` analyst ``` ``` type: str ``` Laboratory analyst.
        - ``` info ``` ``` type: str ``` Laboratory info.
    - ``` results ``` Info instance
        - ``` name ``` ``` type: str ``` RESULTS
        - ``` age_plateau ``` ``` type: List[float] ``` Age plateau.
        - ``` age_spectra ``` ``` type: List[float] ``` Age spectra.
        - ``` isochron ``` ``` type: List[float] ``` Isochron.
        - ``` isochron_F ``` ``` type: List[float] ``` Isochron F.
        - ``` isochron_age ``` ``` type: List[float] ``` Isochron age.
        - ``` J ``` ``` type: List[float] ``` J value, a list of value and error.
        - ``` plateau_F ``` ``` type: List[float] ``` Plateau F.
        - ``` plateau_age ``` ``` type: List[float] ``` Plateau age.
        - ``` total_F ``` ``` type: List[float] ``` total F.
        - ``` total_age ``` ``` type: List[float] ``` total age.
    - ``` reference ``` Info instance
        - ``` name ``` ``` type: str ``` REFERENCE.
        - ``` doi ``` ``` type: str ``` Paper doi.
        - ``` journal ``` ``` type: str ``` Journal name.

- ``` SequenceName = [] ``` ``` type: List[str] ``` 
    
    Sequence name list.

- ``` SequenceValue = [] ``` ``` type: List[str] ``` 

    Sequence label list.

- ``` SequenceUnit = [] ``` ``` type: List[str] ``` 

    Sequence unit list.

- ``` NewIntercept = [] ``` ``` type: List[str] ``` 

    New intercept list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` NewBlank = [] ``` ``` type: List[str] ``` 

    New Blank list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` NewParam = [] ``` ``` type: List[str] ``` 

    New Param list, 2d list, shape = (123, n), n is the number of sample sequences.

- ``` SampleIntercept = [] ``` ``` type: List[str] ``` 

    Unknown intercept list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` BlankIntercept = [] ``` ``` type: List[str] ``` 

    Blank intercept list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` AnalysisDateTime = [] ``` ``` type: List[str] ``` 

    Analysis DateTime list, 1d list, length equals the number of sample sequences.

- ``` BlankCorrected = [] ``` ``` type: List[str] ``` 

    Blank-corrected list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` MassDiscrCorrected = [] ``` ``` type: List[str] ``` 

    Mass discrimination corrected list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` DecayCorrected = [] ``` ``` type: List[str] ``` 

    Decay corrected list, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` InterferenceCorrected = [] ``` ``` type: List[str] ``` 

    Interference Corrected, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` CorrectedValues = [] ``` ``` type: List[str] ``` 

    Corrected values, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` DegasValues = [] ``` ``` type: List[str] ``` 

    Degas values, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` ApparentAgeValues = [] ``` ``` type: List[str] ``` 

    Degas values, 2d list, shape = (10, n), n is the number of sample sequences.

- ``` IsochronValues = [] ``` ``` type: List[str] ``` 

- ``` TotalParam = [] ``` ``` type: List[str] ``` 

- ``` PublishValues = [] ``` ``` type: List[str] ``` 

- ``` SelectedSequence1 = [] ``` ``` type: List[str] ``` 

- ``` SelectedSequence2 = [] ``` ``` type: List[str] ``` 

- ``` UnselectedSequence = [] ``` ``` type: List[str] ``` 

- ``` IsochronMark = [] ``` ``` type: List[str] ``` 

- ``` UnknownTable = Table() ```

- ``` BlankTable = Table() ```

- ``` CorrectedTable = Table() ```

- ``` DegasPatternTable = Table() ```

- ``` PublishTable = Table() ```

- ``` AgeSpectraTable = Table() ```

- ``` IsochronsTable = Table() ```

- ``` TotalParamsTable = Table() ```

- ``` AgeSpectraPlot = Plot() ```

- ``` NorIsochronPlot = Plot() ```

- ``` InvIsochronPlot = Plot() ```

- ``` KClAr1IsochronPlot = Plot() ```

- ``` KClAr2IsochronPlot = Plot() ```

- ``` KClAr3IsochronPlot = Plot() ```

- ``` ThreeDIsochronPlot = Plot() ```

- ``` CorrelationPlot = Plot() ```

- ``` DegasPatternPlot = Plot() ```

- ``` AgeDistributionPlot = Plot() ```

    
    

## Testing
#### 1. **Running the test function from a Python terminal**

    >>> import ararpy as ap
    >>> ap.test()
    Running: ararpy.test()
    ============= Open an example .arr file =============
    file_path = 'your_dir\\examples\\22WHA0433.arr'
    sample = from_arr(file_path=file_path)
    sample.name() = '22WHA0433 -PFI'
    sample.help = 'builtin methods:\n __class__\t__delattr__\t__dir__\t__eq__\t__format__\t__ge__\t__getattribute__\t__gt__\t__hash__\t__init__\t__init_subclass__\t__le__\t__lt__\t__ne__\t__new__\t__reduce__\t__reduce_ex__\t__repr__\t__setattr__\t__sizeof__\t__str__\t__subclasshook__\ndunder-excluded methods:\n apparent_ages\tblank\tcalc_ratio\tcorr_atm\tcorr_blank\tcorr_ca\tcorr_cl\tcorr_decay\tcorr_k\tcorr_massdiscr\tcorr_r\tdoi\tinitial\tisochron\tlaboratory\tname\tparameters\tpublish\trecalculation\tresearcher\tresults\tsample\tsequence\tset_selection\tunknown\tupdate_table\n'
    sample.parameters() = <ararpy.ArArData object at 0x0000027F7FBEC9D0>
    sample.parameters().to_df() = 
             0    1      2       3       4    5  ...   117     118   119 120 121 122
    0   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    1   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    2   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    3   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    4   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    ... ...     ...  ...    ...     ...     ...  ...  ...   ...     ...    ... ... ...
    22  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    23  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    24  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    25  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    26  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1

#### 2. **Example 1： create an empty sample**

    >>> import ararpy as ap    
    >>> sample = ap.from_empty()  # create new sample instance
    >>> print(sample.show_data())
    # Sample Name:
    #
    # Doi:
    #    9a43b5c1a99747ee8608676ac31814da  # uuid
    # Corrected Values:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # Index: []
    # Parameters:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    #           30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
    #           57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
    #           84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...]
    # Index: []
    #
    # [0 rows x 123 columns]
    # Isochron Values:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    #           30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
    # Index: []
    # Apparent Ages:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7]
    # Index: []
    # Publish Table:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # Index: []
    
#### 3. **Example 2： change data point selection and recalculate**

    >>> import ararpy as ap 
    >>> import os
    >>> example_dir = os.path.join(os.path.dirname(os.path.abspath(ap.__file__)), r'examples')
    >>> file_path = os.path.join(example_dir, r'22WHA0433.arr')
    >>> sample = ap.from_arr(file_path)
    # normal isochron age
    >>> print(f"{sample.results().isochron.inverse.set1.age = }")
    # sample.results().isochron.inverse.set1.age = 163.10336210925516
    # check current data point selection
    >>> print(f"{sample.sequence().mark.value}")
    # [nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    >>> print(f"{sample.sequence().mark.set1.index}")
    # [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    
    # change data point selection
    >>> sample.set_selection(10, 1)
    # check new data point selection
    >>> print(f"{sample.sequence().mark.set1.index}")
    # [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    
    # recalculate
    >>> sample.recalculate(re_plot=True)
    # check new results
    >>> print(f"{sample.results().isochron.inverse.set1.age = }")
    # sample.results().isochron.inverse.set1.age = 164.57644271385772

## Classes

    Info
    Plot
    Sample
    Table
    
    class Info(builtins.object)
     |  Info(id='', name='', type='Info', **kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, id='', name='', type='Info', **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Plot(builtins.object)
     |  Plot(id='', type='', name='', data=None, info=None, **kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, id='', type='', name='', data=None, info=None, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  Axis = <class 'sample.Plot.Axis'>
     |  
     |  BasicAttr = <class 'sample.Plot.BasicAttr'>
     |  
     |  Label = <class 'sample.Plot.Label'>
     |  
     |  Set = <class 'sample.Plot.Set'>
     |  
     |  Text = <class 'sample.Plot.Text'>
    
    class Sample(builtins.object)
     |  Sample(**kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  apparent_ages(self)
     |  
     |  blank(self)
     |  
     |  calc_ratio(self)
     |  
     |  corr_atm(self)
     |  
     |  corr_blank(self)
     |  
     |  corr_ca(self)
     |  
     |  corr_cl(self)
     |  
     |  corr_decay(self)
     |  
     |  corr_k(self)
     |  
     |  corr_massdiscr(self)
     |  
     |  corr_r(self)
     |  
     |  corrected(self)
     |  
     |  doi(self)
     |
     |  degas(self)
     |  
     |  initial(self)
     |  
     |  isochron(self)
     |  
     |  laboratory(self)
     |  
     |  name(self)
     |  
     |  parameters(self)
     |  
     |  publish(self)
     |  
     |  recalculation(self)
     |  
     |  researcher(self)
     |  
     |  results(self)
     |  
     |  sample(self)
     |  
     |  sequence(self)
     |  
     |  set_selection(self)
     |  
     |  show_data(self)
     |  
     |  unknown(self)
     |  
     |  update_table(self)
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties defined here:
     |  
     |  version
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Table(builtins.object)
     |  Table(id='', name='Table', colcount=None, rowcount=None, header=None, data=None, coltypes=None, textindexs=None, numericindexs=None, **kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, id='', name='Table', colcount=None, rowcount=None, header=None, data=None, coltypes=None, textindexs=None, numericindexs=None, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

