---
title: Python Types
service: FastAPI
source_urls: ["/tmp/tmp2aqkafzm/repo/docs/de/docs/python-types.md"]
scraped_at: 2026-02-17T00:28:19.425540
content_hash: 460b36fe1000f0de48965357da301b3df72b4d0c0a9fc7f1f203f4fc0cfaa223
size_kb: 12.62
---

# Einführung in Python-Typen { #python-types-intro }

Python hat Unterstützung für optionale „Typhinweise“ (auch „Typannotationen“ genannt).

Diese **„Typhinweise“** oder -Annotationen sind eine spezielle Syntax, die es erlaubt, den <dfn title="zum Beispiel: str, int, float, bool">Typ</dfn> einer Variablen zu deklarieren.

Durch das Deklarieren von Typen für Ihre Variablen können Editoren und Tools bessere Unterstützung bieten.

Dies ist lediglich eine **schnelle Anleitung / Auffrischung** über Pythons Typhinweise. Sie deckt nur das Minimum ab, das nötig ist, um diese mit **FastAPI** zu verwenden ... was tatsächlich sehr wenig ist.

**FastAPI** basiert vollständig auf diesen Typhinweisen, sie geben der Anwendung viele Vorteile und Möglichkeiten.

Aber selbst wenn Sie **FastAPI** nie verwenden, wird es für Sie nützlich sein, ein wenig darüber zu lernen.

/// note | Hinweis

Wenn Sie ein Python-Experte sind und bereits alles über Typhinweise wissen, überspringen Sie dieses Kapitel und fahren Sie mit dem nächsten fort.

///

## Motivation { #motivation }

Fangen wir mit einem einfachen Beispiel an:

{* ../../docs_src/python_types/tutorial001_py310.py *}

Dieses Programm gibt aus:

```
John Doe
```

Die Funktion macht Folgendes:

* Nimmt einen `first_name` und `last_name`.
* Schreibt den ersten Buchstaben eines jeden Wortes groß, mithilfe von `title()`.
* <dfn title="Fügt sie zu einer Einheit zusammen. Mit dem Inhalt des einen nach dem anderen.">Verkettet</dfn> sie mit einem Leerzeichen in der Mitte.

{* ../../docs_src/python_types/tutorial001_py310.py hl[2] *}

### Es bearbeiten { #edit-it }

Es ist ein sehr einfaches Programm.

Aber nun stellen Sie sich vor, Sie würden es selbst schreiben.

Irgendwann sind die Funktions-Parameter fertig, Sie starten mit der Definition des Körpers ...

Aber dann müssen Sie „diese Methode aufrufen, die den ersten Buchstaben in Großbuchstaben umwandelt“.

War es `upper`? War es `uppercase`? `first_uppercase`? `capitalize`?

Dann versuchen Sie es mit dem langjährigen Freund des Programmierers, der Editor-Autovervollständigung.

Sie geben den ersten Parameter der Funktion ein, `first_name`, dann einen Punkt (`.`) und drücken `Strg+Leertaste`, um die Vervollständigung auszulösen.

Aber leider erhalten Sie nichts Nützliches:

<img src="/img/python-types/image01.png">

### Typen hinzufügen { #add-types }

Lassen Sie uns eine einzelne Zeile aus der vorherigen Version ändern.

Wir ändern den folgenden Teil, die Parameter der Funktion, von:

```Python
    first_name, last_name
```

zu:

```Python
    first_name: str, last_name: str
```

Das war's.

Das sind die „Typhinweise“:

{* ../../docs_src/python_types/tutorial002_py310.py hl[1] *}

Das ist nicht das gleiche wie das Deklarieren von Defaultwerten, wie es hier der Fall ist:

```Python
    first_name="john", last_name="doe"
```

Das ist eine andere Sache.

Wir verwenden Doppelpunkte (`:`), nicht Gleichheitszeichen (`=`).

Und das Hinzufügen von Typhinweisen ändert normalerweise nichts an dem, was ohne sie passieren würde.

Aber jetzt stellen Sie sich vor, Sie sind wieder mitten in der Erstellung dieser Funktion, aber mit Typhinweisen.

An derselben Stelle versuchen Sie, die Autovervollständigung mit „Strg+Leertaste“ auszulösen, und Sie sehen:

<img src="/img/python-types/image02.png">

Hier können Sie durch die Optionen blättern, bis Sie diejenige finden, bei der es „Klick“ macht:

<img src="/img/python-types/image03.png">

## Mehr Motivation { #more-motivation }

Sehen Sie sich diese Funktion an, sie hat bereits Typhinweise:

{* ../../docs_src/python_types/tutorial003_py310.py hl[1] *}

Da der Editor die Typen der Variablen kennt, erhalten Sie nicht nur Code-Vervollständigung, sondern auch eine Fehlerprüfung:

<img src="/img/python-types/image04.png">

Jetzt, da Sie wissen, dass Sie das reparieren müssen, konvertieren Sie `age` mittels `str(age)` in einen String:

{* ../../docs_src/python_types/tutorial004_py310.py hl[2] *}

## Deklarieren von Typen { #declaring-types }

Sie haben gerade den Haupt-Einsatzort für die Deklaration von Typhinweisen gesehen. Als Funktionsparameter.

Das ist auch meistens, wie sie in **FastAPI** verwendet werden.

### Einfache Typen { #simple-types }

Sie können alle Standard-Python-Typen deklarieren, nicht nur `str`.

Zum Beispiel diese:

* `int`
* `float`
* `bool`
* `bytes`

{* ../../docs_src/python_types/tutorial005_py310.py hl[1] *}

### `typing`-Modul { #typing-module }

Für einige zusätzliche Anwendungsfälle müssen Sie möglicherweise Dinge aus dem Standardmodul `typing` importieren. Zum Beispiel, wenn Sie deklarieren möchten, dass etwas „jeden Typ“ haben kann, können Sie `Any` aus `typing` verwenden:

```python
from typing import Any


def some_function(data: Any):
    print(data)
```

### Generische Typen { #generic-types }

Einige Typen können „Typ-Parameter“ in eckigen Klammern annehmen, um ihre inneren Typen zu definieren, z. B. eine „Liste von Strings“ würde als `list[str]` deklariert.

Diese Typen, die Typ-Parameter annehmen können, werden **generische Typen** oder **Generics** genannt.

Sie können dieselben eingebauten Typen als Generics verwenden (mit eckigen Klammern und Typen darin):

* `list`
* `tuple`
* `set`
* `dict`

#### Liste { #list }

Definieren wir zum Beispiel eine Variable, die eine `list` von `str` – eine Liste von Strings – sein soll.

Deklarieren Sie die Variable mit der gleichen Doppelpunkt-Syntax (`:`).

Als Typ nehmen Sie `list`.

Da die Liste ein Typ ist, welcher innere Typen enthält, werden diese von eckigen Klammern umfasst:

{* ../../docs_src/python_types/tutorial006_py310.py hl[1] *}

/// info | Info

Die inneren Typen in den eckigen Klammern werden als „Typ-Parameter“ bezeichnet.

In diesem Fall ist `str` der Typ-Parameter, der an `list` übergeben wird.

///

Das bedeutet: Die Variable `items` ist eine Liste – `list` – und jedes der Elemente in dieser Liste ist ein String – `str`.

Auf diese Weise kann Ihr Editor Sie auch bei der Bearbeitung von Einträgen aus der Liste unterstützen:

<img src="/img/python-types/image05.png">

Ohne Typen ist das fast unmöglich zu erreichen.

Beachten Sie, dass die Variable `item` eines der Elemente in der Liste `items` ist.

Und trotzdem weiß der Editor, dass es sich um ein `str` handelt, und bietet entsprechende Unterstützung.

#### Tupel und Menge { #tuple-and-set }

Das Gleiche gilt für die Deklaration eines Tupels – `tuple` – und einer Menge – `set`:

{* ../../docs_src/python_types/tutorial007_py310.py hl[1] *}

Das bedeutet:

* Die Variable `items_t` ist ein `tuple` mit 3 Elementen, einem `int`, einem weiteren `int` und einem `str`.
* Die Variable `items_s` ist ein `set`, und jedes seiner Elemente ist vom Typ `bytes`.

#### Dict { #dict }

Um ein `dict` zu definieren, übergeben Sie zwei Typ-Parameter, getrennt durch Kommas.

Der erste Typ-Parameter ist für die Schlüssel des `dict`.

Der zweite Typ-Parameter ist für die Werte des `dict`:

{* ../../docs_src/python_types/tutorial008_py310.py hl[1] *}

Das bedeutet:

* Die Variable `prices` ist ein `dict`:
    * Die Schlüssel dieses `dict` sind vom Typ `str` (z. B. die Namen der einzelnen Artikel).
    * Die Werte dieses `dict` sind vom Typ `float` (z. B. der Preis jedes Artikels).

#### Union { #union }

Sie können deklarieren, dass eine Variable einer von **verschiedenen Typen** sein kann, zum Beispiel ein `int` oder ein `str`.

Um das zu definieren, verwenden Sie den <dfn title="auch „bitweiser Oder-Operator“ genannt, aber diese Bedeutung ist hier nicht relevant">vertikalen Balken (`|`)</dfn>, um beide Typen zu trennen.

Das wird „Union“ genannt, weil die Variable etwas aus der Vereinigung dieser beiden Typmengen sein kann.

```Python hl_lines="1"
{!> ../../docs_src/python_types/tutorial008b_py310.py!}
```

Das bedeutet, dass `item` ein `int` oder ein `str` sein könnte.

#### Vielleicht `None` { #possibly-none }

Sie können deklarieren, dass ein Wert einen Typ haben könnte, wie `str`, dass er aber auch `None` sein könnte.

//// tab | Python 3.10+

```Python hl_lines="1"
{!> ../../docs_src/python_types/tutorial009_py310.py!}
```

////

Wenn Sie `str | None` anstelle von nur `str` verwenden, wird Ihr Editor Ihnen dabei helfen, Fehler zu erkennen, bei denen Sie annehmen könnten, dass ein Wert immer ein `str` ist, obwohl er auch `None` sein könnte.

### Klassen als Typen { #classes-as-types }

Sie können auch eine Klasse als Typ einer Variablen deklarieren.

Nehmen wir an, Sie haben eine Klasse `Person`, mit einem Namen:

{* ../../docs_src/python_types/tutorial010_py310.py hl[1:3] *}

Dann können Sie eine Variable vom Typ `Person` deklarieren:

{* ../../docs_src/python_types/tutorial010_py310.py hl[6] *}

Und wiederum bekommen Sie die volle Editor-Unterstützung:

<img src="/img/python-types/image06.png">

Beachten Sie, das bedeutet: „`one_person` ist eine **Instanz** der Klasse `Person`“.

Es bedeutet nicht: „`one_person` ist die **Klasse** genannt `Person`“.

## Pydantic-Modelle { #pydantic-models }

<a href="https://docs.pydantic.dev/" class="external-link" target="_blank">Pydantic</a> ist eine Python-Bibliothek für die Validierung von Daten.

Sie deklarieren die „Form“ der Daten als Klassen mit Attributen.

Und jedes Attribut hat einen Typ.

Dann erzeugen Sie eine Instanz dieser Klasse mit einigen Werten, und Pydantic validiert die Werte, konvertiert sie in den passenden Typ (falls notwendig) und gibt Ihnen ein Objekt mit allen Daten.

Und Sie erhalten volle Editor-Unterstützung für dieses Objekt.

Ein Beispiel aus der offiziellen Pydantic Dokumentation:

{* ../../docs_src/python_types/tutorial011_py310.py *}

/// info | Info

Um mehr über <a href="https://docs.pydantic.dev/" class="external-link" target="_blank">Pydantic zu erfahren, schauen Sie sich dessen Dokumentation an</a>.

///

**FastAPI** basiert vollständig auf Pydantic.

Viel mehr von all dem werden Sie in praktischer Anwendung im [Tutorial – Benutzerhandbuch](tutorial/index.md){.internal-link target=_blank} sehen.

## Typhinweise mit Metadaten-Annotationen { #type-hints-with-metadata-annotations }

Python bietet auch die Möglichkeit, **zusätzliche <dfn title="Daten über die Daten, in diesem Fall Informationen über den Typ, z. B. eine Beschreibung.">Metadaten</dfn>** in Typhinweisen unterzubringen, mittels `Annotated`.

Sie können `Annotated` von `typing` importieren.

{* ../../docs_src/python_types/tutorial013_py310.py hl[1,4] *}

Python selbst macht nichts mit `Annotated`. Für Editoren und andere Tools ist der Typ immer noch `str`.

Aber Sie können `Annotated` nutzen, um **FastAPI** mit Metadaten zu versorgen, die ihm sagen, wie sich Ihre Anwendung verhalten soll.

Wichtig ist, dass **der erste *Typ-Parameter***, den Sie `Annotated` übergeben, der **tatsächliche Typ** ist. Der Rest sind Metadaten für andere Tools.

Im Moment müssen Sie nur wissen, dass `Annotated` existiert, und dass es Standard-Python ist. 😎

Später werden Sie sehen, wie **mächtig** es sein kann.

/// tip | Tipp

Der Umstand, dass es **Standard-Python** ist, bedeutet, dass Sie immer noch die **bestmögliche Entwickler-Erfahrung** in Ihrem Editor haben, sowie mit den Tools, die Sie nutzen, um Ihren Code zu analysieren, zu refaktorisieren, usw. ✨

Und ebenfalls, dass Ihr Code sehr kompatibel mit vielen anderen Python-Tools und -Bibliotheken sein wird. 🚀

///

## Typhinweise in **FastAPI** { #type-hints-in-fastapi }

**FastAPI** macht sich diese Typhinweise zunutze, um mehrere Dinge zu tun.

Mit **FastAPI** deklarieren Sie Parameter mit Typhinweisen, und Sie erhalten:

* **Editorunterstützung**.
* **Typ-Prüfungen**.

... und **FastAPI** verwendet dieselben Deklarationen, um:

* **Anforderungen** zu definieren: aus <abbr title="Request – Anfrage: Daten, die der Client zum Server sendet">Request</abbr>-Pfadparametern, Query-Parametern, Header-Feldern, Bodys, Abhängigkeiten, usw.
* **Daten umzuwandeln**: aus dem Request in den erforderlichen Typ.
* **Daten zu validieren**: aus jedem Request:
    * **Automatische Fehler** generieren, die an den Client zurückgegeben werden, wenn die Daten ungültig sind.
* Die API mit OpenAPI zu **dokumentieren**:
    * Die dann von den Benutzeroberflächen der automatisch generierten interaktiven Dokumentation verwendet wird.

Das mag alles abstrakt klingen. Machen Sie sich keine Sorgen. Sie werden all das in Aktion sehen im [Tutorial – Benutzerhandbuch](tutorial/index.md){.internal-link target=_blank}.

Das Wichtigste ist, dass **FastAPI** durch die Verwendung von Standard-Python-Typen an einer einzigen Stelle (anstatt weitere Klassen, Dekoratoren usw. hinzuzufügen) einen Großteil der Arbeit für Sie erledigt.

/// info | Info

Wenn Sie bereits das ganze Tutorial durchgearbeitet haben und mehr über Typen erfahren wollen, dann ist eine gute Ressource <a href="https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html" class="external-link" target="_blank">der „Cheat Sheet“ von `mypy`</a>.

///
