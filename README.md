# Andy Rating System

## Overview

The Andy rating system was designed for the [AndyScorer](http://snooker.andyscorer.org) web service to evaluate players skills in the game of [snooker](en.wikipedia.org/wiki/Snooker). 
It is based on [Glicko](http://www.glicko.net/glicko.html) rating system with minor modifications and treats players strength as their ability to win individual frames.

Like glicko, the introduced rating system considers each player strength being a [normally distributed random variable](en.wikipedia.org/wiki/Normal_distribution). 
Parameters of the distributions (mean and variance) are adjusted periodically based on games outcomes.

The model relies on the following assumptions:
* players try to win every frame,
* frames outcomes are independent of each other.

Any factors other than the *count of frames* won or lost between two opponents, such as match outcome, points scored, breaks made, tournament stage etc, are not taken into account.

## Description

To each player two numbers are associated:

* **Rating**.
Represents player's strength (ability to win frames).
Default rating for a new player is 1500.

* **Reliability** (rescaled version of variance or deviation).
Represents the system's confidence it its estimate of player's skills. 
Varies from -1 (default for a new players) to 1. 
The higher the reliability, the more accurate the rating is considered to be. 
Reliability 1 would mean that the system is 100% sure in player's strength, although this level of confidence can never be achieved.

Both values (rating and reliability) are updated daily based on all finished ranked games played the day before and between members of a club (excluding "guest" players, who are not ranked).
The system looks at all ranked games played at a given day, estimates an expected outcome of each frame and then simultaniously adjusts players ratings according to the difference between actual results and the expectations.

Reliability for a given player grows whenever he plays ranked games (the value by which it is increased is not fixed and depends on many factors, firstly opponent's rating and reliability), and decreases with the passage of time (by approximately -0.0083 every day) if he does not play.
The more you play, the more confident the system becomes that your rating is measured accurately.
And vise versa, long absence results in an uncertanty.

### Remarks

* Rating changes depend on the score. Winning a match 3-2 or 3-0 makes a (big) difference.

* Victory over a strong player (whose rating is high) "costs" more than victory over a weak player.
Similarly, loosing to a lower rated player will cause heavier rating drop than loosing to a stronger one.

* A weak player may still get rating points if he looses a match to a strong opponent but manages to win few frames.
And vise versa, a match winner may still lose some points if he defeats a weaker opponent with a close score.

* Rating changes for two opponents are not symmetric in general.
They depend on both players reliabilities.
Low reliability results in high rating volatility (because in that case the rating is considered to be less precise and the system tries more adjustment), while high reliability means that the system is confident in the rating accuracy and only makes little changes.


#### Types of games

There are three types of games, according to their importance and effect on ratings.

* **Major ranking**. 
These games have "full" impact. 
It is assumed that the result matters for both opponents and thus they do their best to win every frame. 
Most tournaments are major ranking.

* **Minor ranking**. 
Minor ranking games have twice smaller effect than major ranking ones. 
Rating changes after playing a minor ranking game are "discounted" by a factor 0.5 compared to those observed after a major ranking game. 
In other words, winning two *minor* frames have the same effect on ratings than winning one *major* frame.
Friendly matches as well as some nonimportant tournaments are minor ranking events. 
Under normal circumstances it is recommended to give preference to this type of games as long as players try to win.

* **Non ranking**. 
These games do not have any affect on ratings at all. 
This type should be only used if players do not try to win or play not as they would normally do so that the outcome does not adequately represent their real abilities.

Too frequent minor ranking matches between the same two players (more then one in two weeks) have smaller impact on ratings (inversely proportional to the number of games).

Example 1. 1 September 2017. Besenval is a new player. His initial rating is 1500 and the system knows nothing about his real strenghs yet. He wins a minor ranking match against Minuto 4-1, whose rating 1745 is more trustworthy. Besenval gains +247 rating points, while Minuto looses only -46. Defeating a player with a fairly precise rating of 1743 is reasonable evidence that Basenval's strength is probably much higher than 1500. Minuto's rating should decrease by a smaller amount, because his rating is already precisely measured to be near 1745, and he lost to a player whose rating cannot be trusted, therefore little information about Minuto's playing strength has been learned from that match. New ratings appear on the following day, 2 September 2017.

Example 2. 8 November 2017. Solomko's rating is 1788, Di Marco's rating is 1652 and more reliable. Solomko wins a major ranking match 3-2. Solomko's new rating is 1774 (-14), Di Marco's new rating is 1660 (+8). Even though Solomko has won, the system thinks that the result 3-2 was closer then 1788 vs 1652 and increases Di Marco's rating by +8 points, decreasing Solomko's one by -14 points. If it was not a major but minor ranking game, the players would get twice less, +4 and -7, respectively.


The system has weak memory: current ratings depend strongly on recent games and very weakly on games played long time ago. As a result, players cannot rely on their past achievments only, but have to confirm their level constantly.

The model under consideration is probabilistic by its nature. Knowing the ratings of two players it allows to estimate the probability for each of them to win a single frame and a match. For example, in a match (best of 5) between players whose ratings are 1700 and 1650 (provided they are equally reliable) the stronger player would win with probability 62% and the distribution of possible match outcomes would be: 3-0 18%, 3-1 24%, 3-2 20%, 2-3 16%, 1-3 14%, 0-3 8%.


## Web interface

AndyScorer website provides and detailed reports on various statistics.


## F.A.Q.

#### I have won the match. Why has my rating dropped?**

Changes in ratings depend not on a match outcome, but on the score (3-0 and 3-2 will result in different changes), as well as on the players ratings prior to the game. If both opponents had equal ratings before the game, then indeed winning with any score would mean gaining some rating points and vise versa. However, if a player with lover rating wins more frames than "expected" against a strong opponent, than he will still get rating points, while the winner will loose some.
Imagine your rating is 100, and Ronnie O'Sullivan's rating is 3000, and you loose 10-9. Then the system will conclude that maybe you are not so bad and he is not so good, and adjust your ratings accordingly.

Seriously speaking, the system does not see such thing as a match at all, it only cares about frames. So playing two matches 2-1 or one 4-2 will have exactly the same effect, as long as these matches are of the same type (minor or major).

**When will I get an official rating?




## Credits
The rating system was inspired by Gerardo Calzerano, designed by Anton Solomko and implemented by Anton Solomko and Luca Gherardi.
