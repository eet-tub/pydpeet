# Examples

Here you can find tutorials and practical examples for the most important public PyDPEET functions.

In addition, this section contains research publications and posters that used PyDPEET for battery data processing and analysis. These examples provide insight into how PyDPEET was applied in real scientific workflows and include example notebooks and scripts where available.

## Tutorials

```{eval-rst}
.. nbgallery::
   :name: Tutorials

   notebooks/Tutorial_01_Convert_Import
   notebooks/Tutorial_02_Merge
   notebooks/Tutorial_03_Sequence
   notebooks/Tutorial_04_iOCV
   notebooks/Tutorial_05_SOC
   notebooks/Tutorial_06_SOH_C
   notebooks/Tutorial_07_SOH_R
```


## Usage in Research Publications

:::{card} 2026/04 | PyDPEET: A Python Package for Fast and Easy Battery Data Unification, Processing, and Analysis
:class-card: sd-rounded-3 sd-shadow-sm

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; align-items: start;">

<div>

```{image} research/2026_KWB/KWB2026_otto_Preview.png
:width: 100%
<!-- :target: research/2026_KWB/P3-005_Otto.pdf -->
```

</div>

<div>

### Abstract

PyDPEET ("Data Processing for Electrical Energy Storage Technologies") is an open-source Python package developed to facilitate battery data analysis. It targets a common problem: lab and field tests produce large, mixed datasets in different file formats. Manual preprocessing is slow, error-prone, and hard to reproduce. PyDPEET offers a transparent workflow that standardises raw files, processes them with consistent rules, and provides evaluation functionality within a highly integrated code base. The package also offers full user flexibility via custom parameter configuration.

</div>

<div>

### Resources

- {doc}`Example Notebook <research/2026_KWB/Usage_Example>`
- [Poster PDF](research/2026_KWB/P3-005_Otto.pdf)
<!-- - [DOI]() -->

### Cite
Otto, M., Schlösser, A., Schröder, D., De Simone, C., Hinrichsen, A., Kalisch, J., & Kowal, J. (2026). PyDPEET: A Python Package for Fast and Easy Battery Data Unification, Processing, and Analysis [Poster]. Advanced Battery Power, Münster, Germany.

</div>

</div>

:::