### De Code
Deze folder bevat alle code die gebruikt is voor het maken van de tool.
Veel van deze code en data zijn niet nodig om de tool te gebruiken maar zijn wel gebruikt tijdens het project.


### Inladen
Deze folder bevat alle data die nodig is om de algoritmes te starten, het is dus NIET nodig om data nog in te laden.

Als de csv's van de steden wel ontbreken dan kunnen deze ingeladen worden met het volgende command line argumenten:
(In volgorde):
1. python main.py -l ; laad de data in.
2. python main.py -c krommenie -csv ; maakt complete csv voor krommenie
3. python main.py -c leiden -csv ; maakt complete csv voor leiden
4. python main.py -c eindhoven -csv ; maakt complete csv voor eindhoven
5. python main.py -c amsterdam -csv ; maakt complete csv voor amsterdam


### Opstarten
Om de tool op te starten kan de file tool.py gestart worden met de terminal command: python tool.py

Het is ook mogelijk om de main.py file direct te starten met command line argumenten:
- c geeft aan welke stad geselecteerd wordt
- a1 is het routerings algoritme
- a2 is het lokaliserings algoritme
- v maakt in visualisatie van de geselecteerde stad in plaats van het algoritme uit te voeren

Voorbeeld:
python main.py -c krommenie -a1 prim -a2 greedy ; voert het greedy-prim algoritme uit voor de stad krommenie
python main.py -v -c amsterdam ; maakt een visualisatie van de stad amsterdam


### Functionaliteit
visualisaties die gemaakt worden van de oplossingen worden opgeslagen in de map: tool_images.
Deze afbeeldingen worden overschreven wanneer er een nieuwe afbeeldinging wordt gemaakt.
Daarom is het handig om visualisaties die bewaart moeten blijven naar de visualisations map te Kopiëren.

De andere output is een file met de coordinaten van de geplaatste stations.
Deze bevinden zich in de map: data/solutions.

### benodigdheden
De volgende python packages moeten geinstalleerd zijn zodat dat de code het doet:
- matplotlib
- pandas
- numpy
- argparse
- functools
- shapely
