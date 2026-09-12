# Informatika Terem Ültetésgenerátor

Egy egyszerű, Pythonban írt grafikus felületű (Tkinter) alkalmazás, amely segít az informatika termi ülésrend gyors és véletlenszerű kiosztásában, figyelembe véve a meghibásodott számítógépeket.

## Főbb funkciók

- **Terem elrendezés megjelenítése:** A terem asztalai grafikusan jelennek meg (bal oldalon 4x4, jobb oldalon 3x4 + 2 gépes blokk).
- **Rossz gépek kizárása:** Egyetlen kattintással bármelyik gép megjelölhető hibásként (`OUT OF ORDER`), így oda a rendszer nem sorsol tanulót.
- **e-Kréta névsor beolvasása:** Közvetlenül beolvasható az e-Krétából kimásolt vagy formázott `.txt` fájl. A program automatikusan felismeri a neveket és kihagyja a felesleges sorokat a `-` elválasztóig.
- **Véletlenszerű sorsolás:** A diákokat véletlenszerűen elosztja a működőképes gépek között.
- **Nyomtatás / PDF export:** A generált ülésrendet böngészőn keresztül azonnal ki lehet nyomtatni vagy PDF formátumban lementeni.

## Követelmények

- Python 3.x
- Nincs szükség külön csomagtelepítésre (`pip`), az alkalmazás csak a beépített standard könyvtárakat használja (`tkinter`, `random`, `webbrowser`, `os`, `tempfile`).

## Használat

1. Indítsd el a programot:
   ```bash
   python main.py
2. Kattints a 📁 Nevek betöltése (.txt) gombra, és válaszd ki a diákok névsorát tartalmazó fájlt.

3. Kattints azokra a gépekre, amelyek nem működnek (pirosra váltanak).

4. Kattints a Ülésrend generálás gombra a véletlenszerű ülésrend kiosztásához.

5. A 🖨️ Nyomtatás / PDF gombbal megjelenítheted a nyomtatóbarát nézetet.

## Bemeneti fájl formátuma (.txt)
A program a következő struktúrájú szöveges fájlokat dolgozza fel:

Plaintext
1
Jhone Doe
1
2
3
4
5
-
2
Kis Pista
1
2
3
4
5
-