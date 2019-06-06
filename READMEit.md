# Sistema di valutazione Andy

## Panoramica

Il sistema di valutazione Andy è stato progettato per [AndyScorer](http://snooker.andyscorer.org) per valutare le abilità di un giocatore nel gioco dello [snooker](https://it.wikipedia.org/wiki/Snooker). Questo sistema è basato sul sistema di valutazione [Glicko](http://www.glicko.net/glicko.html) con una serie di modifiche minori e mostra la forza dei giocatori come l'abilità di vincere individualmente i frames.

Nel nostro modello, come in Glicko, le abilità dei giocatori si presume che siano [variabili casuali normalmente distribuite](https://it.wikipedia.org/wiki/Distribuzione_normale). I parametri di distribuzione (media e varianza) sono nuovamente valutate periodicamente, in base ai risultati di gioco.

Il modello si basa sui seguenti presupposti:
* i giocatori cercano di vincere ogni frame,
* i frames siano indipendenti uno dall'altro.

Il solo *conteggio dei frames* (vinti o persi) determina il punteggio di valutazione.
Ogni altro fattore, come per esempio il risultato del match, i punti totalizzati, i breaks raggiunti, le fasi del torneo, non sono presi in considerazione.

## Descrizione

Per ogni giocatore sono assegnati due numeri:

* **Punteggio**.
Rappresenta la forza del giocatore (abilità di vincere frames). 
Il valore iniziale di forza del giocatore è di 1500 punti.

* **Affidabilità** del punteggio di valutazione del giocatore (versione rigraduata della varianza). 
Un parametro ausiliario che rappresenta la confidenza del sistema con il punteggio del giocatore stabilito. 
L'affidabilità varia da -1 (Standard per i nuovi giocatori) a 1. 
Maggiore è l'affidabilità, maggiore è il punteggio. 
(Affidabilità 1 significa che il sistema è sicuro al 100% della forza del giocatore, sebbene questo livello di confidenza non potrà mai esser raggiunto.) 
L'affidabilità serve come indicatore per lo [stato ufficiale](#official) del giocatore.

Entrambi i numeri (punteggio ed affidabilità) sono aggiornati *giornalmente* in base alla totalità delle [partite classificate](#games) giocate nelle giornate precedenti. 
Il sistema stima un risultato previsto per ogni partita e poi, simultaneamente, corregge il punteggio in base alla differenza tra il risultato ottenuto e la previsione. 
I risultati aggiornati vengono mostrati il *giorno seguente*, dopo che le partite sono state giocate. 
Se il giocatore non gioca partite classificate, il suo punteggio rimane invariato.

L'affidabilità cambia ogni giorno (indipendentemente dall'attività del giocatore) in due modi differenti:
* Ogni volta che una partita classificata viene giocata, l'affidabilità *cresce*; il che significa che più giochi, più credibile è il tuo punteggio. L'incremento dipende da vari fattori.
* Quando non si gioca, l'affidabilità *diminuisce* col passare del tempo (di 0.008(3) ogni giorno). Nei fatti ogni periodo di inattività determina una maggiore incertezza sulle abilità di un giocatore. 
Se un giocatore smette completamente di giocare, l'affidabilità cala fino a raggiungere il punteggio minimo (-1) in circa 2 anni.

Per ogni frame in una partita classificata, il giocatore ottiene o perde dei punti.
Il numero di punti dipende da due fattori:
1. *Differenza tra le valutazioni degli avversari* precedenti alla partita.
Questo è il fattore chiave: più il risultato ottenuto è inaspettato dal sistema, più il punteggio varia:

| Punteggio giocatore A | Punteggio giocatore B | Vincitore frame       | Variazione del punteggio                |
| :-------------: | :-------------: | :----------------: | :------------------------------------: |
| Alto            | Basso             | **A** (previsto)   | A riceve pochi punti, B perde pochi punti  |
| Alto            | Basso             | **B** (non previsto) | A perde molti punti, B riceve molti punti |

2. *Affidabilità*.
Se l'affidabilità è elevata, il cambiamento nel punteggio sarà di poco conto (dato che il sistema è già confidente nelle abilità del giocatore, un frame non fornirà una dimostrazione abbastanza valida per modificare fortemente il punteggio). 
Al contrario, una bassa affidabilità comporterà una possibilità di variazione del punteggio elevata (Le informazioni ottenute da ogni frame saranno percepibili rispetto a quelle che il sistema già conosce, quindi proverà ad una regolazione più audace del punteggio). 
La differenza nell'affidabilità tra i vari giocatori ha la sua importanza.

### Caratteristiche chiave

* Il cambiamento del punteggio deriva dai *punti di gioco*, non dal risultato della partita. 
Vincere un incontro 3-0 o 3-2 è assolutamente ininfluente.

* Vincere contro un giocatore con un punteggio elevato permette di ottenere molti più punti, inversamente, vincere contro un giocatore con un punteggio basso vi farà ottenere pochi punti.

* Un giocatore con basso punteggio potrebbe *ottenere* dei punti persino quando perde un incontro contro un giocatore più forte se riesce a vincere qualche frame (il vincitore perderà qualche punto, in questo caso). 
Per esempio, giocando contro uno sfidante forte, un giocatore potrebbe perdere -5 punti per ogni frame perso e guadagnarne +23 per un frame vinto; quindi una partita persa 1-3 darà al giocatore sconfitto 23 – 3*5 = +8 punti.

* I cambiamenti di punteggio dei giocatori *non sono simmetrici* in genere (ma sempre opposte). Dipendono dall'affidabilità degli sfidanti: i punteggi con affidabilità bassa variano di più.

* Gli incrementi dei punteggi *non sono aggiuntivi*: i punti ottenuti nei vari frames in una serie di partite giocata lo stesso giorno è leggermente inferiore al numero di punti ottenuti per un frame singolo. 
Inoltre, quando si gioca contro vari giocatori nello stesso giorno, la variazione di punteggio è composta dai singoli frames, ma non ridotta alla loro somma aritmetica.

* Il sistema ha la *memoria corta*. Sebbene tutte le partite passate abbiano una certa influenza sul sistema di punteggio, il punteggio attuale dipende fortemente dalle partite più recenti e solo in parte dalle partite giocate tempo prima. 
(Dando per scontato che i giocatori giochino regolarmente, naturalmente. I giocatori che hanno smesso di giocare vengono congelati.)


### <a name="games"></a>Tipologie di gioco

Ci sono tre tipi di gioco, catalogati in base alla loro importanza ed influenza sul sistema di calcolo del punteggio:

* **Major (principale) ranking** hanno un impatto pieno sul sistema di calcolo del punteggio. 
Si da per scontato che questa tipologia di partite sia considerata importante per entrambi gli sfidanti che faranno del loro meglio per vincere ogni frame. La maggior parte dei tornei sono partite classificate principali.

* **Minor (secondario) ranking**: hanno un impatto parziale messe a confronto con le partite classificate principali. 
Qualsiasi variazione causata da una partita classificata secondaria è “ammortizzata” o “scontata” di metà del suo valore.
In altre parole vincere due frames *secondario* è come vincere un frame *principale*. 
Le sfide amichevoli come anche i piccoli tornei sono classificate come eventi secondari. 
Sotto normali circostanze è consigliato giocare questa tipologia di partite fino a quando i giocatori cercheranno di vincere.

* **Non (nessun) ranking**: non variano il punteggio in alcun modo. 
Questa tipologia di partite dovrebbe esser giocata quando i giocatori non giocano per vincere oppure quando i giocatori non giocano come farebbero normalmente e quindi non ottengano il risultato che avrebbe rappresentato le loro abilità reali di gioco.


### Ospiti

I giocatori che non sono affiliati ad un'accademia (“ospiti”) non sono classificati. Ogni incontro che vede tra gli sfidanti un ospite è ignorato dal sistema.


### Restrizione di frequenza

Se due giocatori si incontrano troppo spesso (più di una volta in 2 settimane), le loro partite classificate secondarie (minor ranking) hanno un impatto minore sulla variazione del punteggio. In pratica a queste partite è attribuito un ulteriore "ammortamento" uguale al numero inverso di giorni in cui hanno giocato insieme negli ultimi 14 giorni.

Ad esempio, se due amici si sfidano per 3 giorni di fila, le sfide del primo giorno verranno contate come partite classificate secondarie normali. Le partite giocate il secondo giorno subiranno un impatto che equivale alla metà dell’impatto normale sui punteggi (coefficiente 1/2 o 1/4 rispetto a una partita classificata principale). Qualsiasi partita giocata tra questi due durante il terzo giorno verrà conteggiata con il coefficiente 1/3 e così via. Se si incontrano di nuovo tra due settimane o più tardi, non verrà più imposta alcuna penalità di frequenza e il gioco classificato verrà conteggiato come al solito.

Tutti i frame giocati in partite principali (major ranking) non subiscono questo ammortamento e hanno un impatto completo sui rating, indipendentemente dalla frequenza con i quali vengono giocati.


### <a name="official"></a>Stato ufficiale

La valutazione del giocatore è **ufficiale** se l'affidabilità è positiva e **non ufficiale** altrimenti.

Ciò significa che i nuovi giocatori ottengono inizialmente valutazioni non ufficiali (l'affidabilità predefinita è -1) e ottengono lo status ufficiale solo dopo aver completato un certo numero di partite classificate (in genere circa 20 frames giocati contro 5 avversari diversi, sufficienti perché il punteggio si stabilizzi vicino al valore reale).

Poiché l'affidabilità dei giocatori inattivi diminuisce costantemente con il passare del tempo, i punteggi di quei giocatori, che non giocano per un po', prima o poi (ma non più di 120 giorni) diventano *non ufficiali*. 
Se ciò accade, devono giocare un certo numero di partite per confermare il loro livello, prima che ritornino al loro stato ufficiale.

### Classifica del club

La classifica ufficiale del club viene aggiornata una volta alla settimana e si basa sulle valutazioni del lunedì. 
I giocatori la cui valutazione non è ufficiale rimangono non classificati.


## Interpretazione probabilistica

Il nostro modello è stocastico: dai risultati delle varie partite cerca di stimare entità e varianze delle abilità dei giocatori distribuite normalmente. In secondo luogo consente di prevedere i risultati delle sfide future. 
Conoscendo le valutazioni di due avversari, si può stimare la *probabilità* per ognuno di loro di vincere un singolo frame, e di conseguenza una partita. Ad esempio, per due giocatori con punteggi 1700 e 1650 (a condizione che siano ugualmente affidabili), il più forte vincerebbe un frame con probabilità 62% e la distribuzione dei possibili risultati di una partita "al meglio dei 5 frame" sarebbe:

Punteggio | Probabilità
:----:|:-----------:
 3-0  | 18%
 3-1  | 24%
 3-2  | 20%
 2-3  | 16%
 1-3  | 14%
 0-3  | 8%


## Esempi

#### Example 1.
**A.B.** is a new player playing his first ever game. 
His initial rating is 1500 and the system knows nothing about his real strengths yet (reliability -1). 
He wins a friendly (minor ranking) match 4-1 against **D.M.**, whose rating 1759 is more trustworthy (reliability 0.35). 
As the next day report reveals, **A.B.** gains +413 rating points, while **D.M.** only looses -61. 
Defeating a player with a fairly precise rating of 1759 is a reasonable evidence that **A.B.**'s strength is probably much higher than 1500. **D.M.**'s rating should decrease by a smaller amount, because his rating is already precisely measured to be near 1759, and he lost to a player whose rating cannot be trusted, therefore little information about **D.M.**'s playing strength has been learned from that match.
New reliabilities of the two players are -0.3 (unofficial) and 0.4, respectively.

![](img/Example1.jpg)

#### Example 2.
**A.S.**'s rating is 1858 (reliability 0.48), **P.DM.**'s rating is 1684 and more reliable (0.7).
**A.S.** wins a major ranking match 3-2 (the only game both players had that day).
**A.S.**'s new rating is 1830 (-28), while **P.DM.**'s one is 1701 (+17).
Even though **A.S.** has won the match, the system thinks that the result 3-2 was closer then 1858 vs 1684, thus adds +17 points to **P.DM.** and subtracts 28 points from **A.S.** (notice that the less reliable rating changes more).
If it was a *minor* ranking game instead, the players would get twice less, +9 and -14 points, respectively.

![](img/Example2.jpg)


## Web reports

[AndyScorer](http://snooker.andyscorer.org) website provides various rating reports.
Chronological data are typically ordered from recent to past.


### Ratings
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/snk_rating_1549395708.jpg?79537)\
This table shows ratings for a selected day (today by default) with the following columns:
* *Position*. Please note that one position is never shared by two players, even if rounded ratings sometimes coincide. The real (not rounded) values are almost surely different from each other.
* *Player name*.
* *Rating* for a given day (based on all games played before that day).
* Latest rating *change* for each player.
* *Day* when the last ranking game was played.
* Rating *reliability*.

Only official ratings are shown by default.
Set the corresponding flag to see all ratings including unofficial ones:
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/snk_rating_1549395796.jpg?38962)


### Official ranking
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/official_rating.jpg?4929)\
Official club ranking table (based on Monday ratings of the selected week, current week by default) contains the columns:
* *Position* (rank).
* *Position change* since the last week.
* *Player*.
* *Rating*.

Players whose rating is not official and who therefore are not ranked are listed in a separate table:
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/official_rating_off.jpg?81410)


### Leaders
This block contains two tables:
* the list of players who took the first line of the rankings by week,
* overall leaders by number of weeks they hold the first plase.


### Rating/ranking history
Complete record of all rating and ranking changes for a selected player:
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/player_rating_history_1549399068.jpg?13961)\
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/player_ranking_history_1549399068.jpg?98891)


## F.A.Q.

#### I have won the match. Why has my rating dropped?

Rating changes depend on the score (3-0 and 3-2 will have different effects), as well as on the players ratings prior to the game. 

Imagine your rating is 100, and Ronnie O'Sullivan's rating is 3000, and you lose 9-10. Even though you lost the match, the system will conclude that probably you are not so bad and he is not so good, and adjust the ratings accordingly.

You are only guaranteed to get rating points if you:
* whitewash your opponent, or
* win (with any score) against a stronger opponent.

Otherwise make sure that you don't lose too many frames to losers.

#### When will I get an official rating?

When reliability of your rating becomes positive.
It usually takes about 20 frames to play with 5 different opponents, but precise number depends on the "quality" of you opponents, as well as some other factors.
Keep playing and you get your official status soon.

#### What happens to my rating if I don't play for some time?

Rating value itself will not change, but reliability will go down until eventually it hits 0 and then your rating becomes *unofficial*.
In that case you will need to play some number of games to return your official status.

#### Will I get additional rating points for winning a match / a deciding frame / a tournament?

No, the system only cares about frames on a scoreboard and treats them all equally (apart from major/minor type).
It does not distinguish deciding frames, tournament finals etc.
This is because we believe that, no matter how important game you win, the outcome depends on your skills very much like any other frame, rather that your will to win (unfortunately, we cannot measure players psychological state yet).
The only way to tell that one game is more important than another is to nominate it *major ranking*, not *minor ranking*, in which case rating changes will be simply twice bigger.

#### I regularly make big breaks and recently won a big tournament. Doesn't it mean I should be number one in ranking?

No, it doesn't. No matter how big breaks you make or what other achievements you have, as long as you don't win consistently your rating may be low.

## Credits
The rating system was inspired by *Gerardo Calzerano*, designed by *Anton Solomko* and implemented by *Anton Solomko* and *Luca Gherardi*.
