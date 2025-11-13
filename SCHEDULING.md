# Kanal- und Zeitplanung für die Controller A, B und C

Um Kollisionen bei Ranging-Intervallen von 100 ms zu vermeiden, werden die drei
Controller zeitlich gestaffelt und auf unterschiedliche UWB-Kanäle verteilt.

| Controller | UCI-Port | MAC-Adresse | Kanal | Startverzögerung | Ranging-Intervall |
|------------|----------|-------------|-------|------------------|-------------------|
| A          | COM4     | 0x10        | 5     | 0 ms             | 100 ms            |
| B          | COM5     | 0x11        | 9     | 33 ms            | 100 ms            |
| C          | COM6     | 0x12        | 13    | 66 ms            | 100 ms            |

## Umsetzung in den Skripten

* Die Konfiguration wird für jeden Controller im jeweiligen Skript (`controllerA.py`,
  `controllerB.py`, `controllerC.py`) gesetzt. Alle Skripte nutzen weiterhin
  `ScheduleMode = 1` und `MultiNodeMode = 0`, sodass der Zeitplan vollständig auf
  der definierten Startzeit und dem Intervall basiert.
* Die Startverzögerungen werden direkt vor dem Aufruf `ranging_start` realisiert.
  Damit verschieben sich die 100 ms-Ranging-Runden dauerhaft zueinander, sobald
  alle drei Controller laufen.
* Durch die Nutzung unterschiedlicher Kanäle werden etwaige Restüberlappungen der
  Funk-Slots zusätzlich vermieden.

## Startreihenfolge

Die Controller können in beliebiger Reihenfolge gestartet werden. Die absolute
Zeitverschiebung wird in jedem Skript umgesetzt. Wird ein Controller später
neu gestartet, orientiert er sich erneut an seiner internen Verzögerung und
fügt sich damit wieder in den oben beschriebenen Zeitplan ein.
