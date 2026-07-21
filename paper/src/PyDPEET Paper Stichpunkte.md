---
title: "PyDPEET: A Python Package for automating Data Processing of Eelectrical Energy Storages"
tags:
  - Python
  - Battery
  - Data-Processing
  - Automatisation
  - Energy-Storages
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
  - name: Giada Vaccarello
    affiliation: 1
  - name: Cataldo Pasquale Hermann De Simone
    affiliation: 1
  - name: Domink Droese
    orcid: 0009-0002-2065-4119
    affiliation: 1
  - name: Julia Kowal
    orcid: 0000-0002-8802-6365
    corresponding: true
    affiliation: 1
affiliations:
  - name: Electrical Energy Storage Technology (EET), Institute of Energy and Automation, Technische Universität Berlin, Einsteinufer 11, D-10587 Berlin, Germany
    index: 1
    ror: 03v4gjf40
date: 15.02.2026
bibliography: paper.bib
---

# Summary


PyDPEET (Python Data Processing for Electrical Energy Storage) is an open-source battery data processing package written in Python. Its mission is to simplify and accelerate the development, execution, and comparability of battery data processing and analysis by providing a unified, extensible tool that reduces repetitive work and enables efficient, multi-institutional and interdisciplinary collaboration.
# Statement of need
1. **Problem in der aktuellen Praxis**
- Welche Lücke, welches Defizit oder welche Ineffizienz existiert heute?  
	- Data Processing und Analyse ist in der Forschung von Energiespeichern ist eine fast tägliche Arbeit um sie zum Beispiel neue Materialien und Batteriezellen Charakterisieren zu können. Diese Arbeit wird typischerweise von den Forschenden für jede Kampagne händisch durchgeführt mit Anpassungen an die von den Testgeräten (z.B. Zyklisierern)  und die exakte Durchführung der Tests. Wie das exakte Processing durchgeführt wurde, wird dabei selten veröffentlicht. Dies macht das Processing langwierig und die Ergebnisse schlecht vergleichbar. 
- Wo scheitern bestehende Tools oder Workflows?
	- hier auf Analyse von Jan in seiner BA eingehen. 

    
3. **Zielgruppe / Nutzerkreis**  
 - Wer hat dieses Problem (Forschende, Ingenieur:innen, Labs, Industrie, Open-Source-Community)?  
 - Warum betrifft es gerade diese Gruppe stark?
	 - Forschende:
		 - lang dauernde iterative Arbeit 
		 - entwickeln von mehr Automatierten, schnelleren, genaueren Methodikenzur Charakterisierung und Blechmarken diesen mit bereits vorhanden. 
	 - Industrie:
		 - können Code nutzen um Analysen von speichern durchzuführen ohne viel neue Methoden entwickeln zu müssen. 
    
5. **Relevanz und Impact**  
-  Warum ist das Problem wichtig?  
- Was sind die wissenschaftlichen oder praktischen Folgen, wenn es nicht gelöst wird?
	- wenn dieses Problem nicht gelöst wird, führt das zur verlangsamung von der Entwicklung neuer Batterietechnologien und Methodiken zur Charakterisierung, weil schlecht auf bestehende Methodiken aufgebaut werden bzw. Diese für seinen eigenen Fall neu implementiert werden müssen 
    
    
6. **Stand der bisherigen Lösungen**  
    – Welche existierenden Tools gibt es?  
    – Welche Einschränkungen oder Lücken bleiben trotz dieser Tools bestehen?
    
7. **Motivation für das neue Tool**  
    – Warum ist ein neues, offenes, erweiterbares oder reproduzierbares Tool nötig?  
    – Welche Eigenschaften müssen verbessert werden (Performance, Usability, Standardisierung, Interoperabilität etc.)?

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References