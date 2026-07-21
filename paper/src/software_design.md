# Software Design
<!-- 
1. Einlesen in einheitliches Format
    1. verschiedenen Reader unterschiedliche Formate (in Klassen sodass die möglichkeiten von der IDE vorgeschlagen werden)
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
    2. Ausgabe als ein einheitliches Pandas Dataframe 
      - Pandas Dataframe format wurde genutzt, weil es ein einfaches viel verwendetes tool ist und innerhlab des PyData universums liegt. Dadurch ist eine gute anbindung und kompatibilität innerhalb des PyData-Universums gegeben. und viele Nutzer*innen sind mit funktionen von Pandas bereits betraut. 
2. Mehrere Tests einer Batteriezelle in ein Dataframe zusammenführen (Merge). Um verhalten über die Alterung gut nachvollziehen zu können und eineinheitliche verarbbeitung zu vereinfachen 
3. Optional: Einteilen der Tests in ein  Sequenzen, wie Laden, Entladen und Pulse für vereinfachte und gleichmäßige weitere Auswertung.
4. Analysieren der Datein und berechnen von zum Beispiel State of Charge (SOH), Kapazitäten und Innenwiderstände und mit ihnen den State of Health des Innenwiderstandes und der Kapazität (SOH-C, SOH-R), Extrahieren von OCVs
  - Die Analyse Funktionen werden unterteilt in welche, die neue Spalten hinzufügen (add_XYZ), und informationen Extrahieren (extract_xyz). Durch das einfache hinzufügen, von neuen Spalten, ist die weitere Auswertung, plotting und exportieren sehr einfach. 
5. Exportieren
  - Bevorzugt als parquet für einen schnellen und einfachen workflow, alternativ auch in den vom Nutzer vorgegeben vormaten durch Pandas export funtkionen. 

um Wissenschaftliche funktionen anderer Authoren implemntieren zu können und stets eine honorierung ihrer arbeit sicherstellen zu können, wurde eine Zitationsfunktion implemntiert, die sicherstellt, die am Ende eine Skript genutzt werden kann um alle zu Zitierenden Arbeiten auszugeben. 

-->


![Overview over the Structure and functionalities of the Python Package PyDPEET](PyDPEET_Overview.svg)