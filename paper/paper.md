---
title: "PyDPEET: A Python Package for automating Data Processing of Eelectrical Energy Storages"
tags:
  - Python
  - Battery
  - Data-Processing
  - Automatisation
  - Energy-Storages
  - processing
  - Big Data
authors:
  - name: Martin Otto
    orcid: 0009-0006-5262-6429
    equal-contrib: true
    corresponding: true
    affiliation: 1
  - name: Anton Schlösser
    orcid: 0009-0004-3794-0079
    equal-contrib: true
    corresponding: true
    affiliation: 1
  - name: Daniel Schröder
    affiliation: 1
  - name: Jan Kalisch
    affiliation: 1
  - name: Alexander Günter
    affiliation: 1
  # - name: Giada Vaccarello
  #   affiliation: 1
  - name: Cataldo Pasquale Hermann De Simone
    affiliation: 1
  # - name: Domink Droese
  #   orcid: 0009-0002-2065-4119
  #   affiliation: 1
  - name: Julia Kowal
    orcid: 0000-0002-8802-6365
    corresponding: true
    affiliation: 1
affiliations:
  - name: Electrical Energy Storage Technology (EET), Institute of Energy and Automation, Technische Universität Berlin, Einsteinufer 11, D-10587 Berlin, Germany
    index: 1
    ror: 03v4gjf40
date: 25.06.2026
bibliography: paper.bib
---


# Summary



# State of the field

<!-- - Es gibt viele verschiedene software(teile), die sich mit der Auswertung und verarbeiten von Batteriemessdaten auseinadersetzen. Häufig sind sie spezialisert auf bestimmte dinge. Zum Beispiel 
- EIS/DRT [@murbach_impedancepy_2020; @wan_influence_2015; @huang_joint-domain_2026]
- Degradation mode Analysis [@rehm_how_2026; @dubarry_synthesize_2012]
- Zeitreihen (@holland_pyprobe_2025, @wind_cellpy_2024)
- other (@herring_beep_2020) -->



# Statement of Need



# Software Design
<!-- 
1. Einlesen in einheitliches Format
    2. verschiedenen Reader unterschiedliche Formate (in Klassen sodass die möglichkeiten von der IDE vorgeschlagen werden)
        STANDARD_COLUMNS = [
    "Meta_Data",
    "Step_Count",
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Test_Time[s]",
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]"
]
    3. Ausgabe als ein einheitliches Pandas Dataframe 
2. Mehrere Tests einer Batteriezelle in ein Dataframe zusammenführen (Merge). Um verhalten über die Alterung gut nachvollziehen zu können und eineinheitliche verarbbeitung zu vereinfachen 
3. Optional: Einteilen der Tests in ein  Sequenzen, wie Laden, Entladen und Pulse für vereinfachte und gleichmäßige weitere Auswertung.
4. Analysieren der Datein und berechnen von zum Beispiel State of Charge (SOH), Kapazitäten und Innenwiderstände und mit ihnen den State of Health des Innenwiderstandes und der Kapazität (SOH-C, SOH-R)
5. Exportieren

-->


![Overview over the Structure and functionalities of the Python Package PyDPEET](PyDPEET_Overview.svg)

# Research impect Statement

<!-- 
Durch viele Abschlussarbeiten (Bachelor und Master) genutzt und zum Teil weiterentwickelt
Mit großem interesse auf der Advanced Battery Power 2026 Conference Vorgestellt[@otto_pydpeet_2026] und verwendet für [@schlosser_automated_2026].
 -->


# Ai usage disclosure

<!-- 
Generative AI tools were used during the development of this project to assist with code suggestions, debugging, documentation and docstring drafting, algorithmic suggestions, website development, and improving the wording of the manuscript. All AI-generated suggestions and content were reviewed, modified where necessary, and verified by the authors before inclusion

--------------
---- oder-----
--------------

Generative AI tools were used to assist with code suggestions, debugging, documentation, website development, and improving the wording of the manuscript. All AI-assisted output was reviewed, validated, and, where necessary, revised by the authors
 -->
