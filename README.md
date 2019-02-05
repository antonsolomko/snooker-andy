# Andy Rating System

The Andy rating system was designed for the [AndyScorer](http://snooker.andyscorer.org) web service to evaluate players skills in the game of [snooker](en.wikipedia.org/wiki/Snooker). It is based on [Glicko](http://www.glicko.net/glicko.html) rating system with minor modifications and assesses players strength as their ability to win frames.

As glicko, the introduced rating system considers each player's strength being a [normally distributed random variable](en.wikipedia.org/wiki/Normal_distribution). Parameters of the distributions (mean and variance) are adjusted periodically based on games outcomes.

#### Assumptions:
* players try to win every frame,
* frames outcomes are independent of each other.

Ratings are updated daily. Ratings on a given day are based on all finished ranked games played before that day between members of one academy (excluding "guest" players, who are not ranked).

#### Types of games

There are three types of games, according to their importance and effect on ratings.

* **Major ranking**. These games have "full" impact. It is assumed that the result is important for both opponents and they do their best to win. Most tournaments are major ranking.

* **Minor ranking**. Minor ranking games have twice smaller effect than major ranking ones. Rating changes after playing a minor ranking game are "discounted" by a factor 0.5 compared to those observed after a major ranking game. In other words, winning two *minor* frames have the same effect on ratings than winning one *major* frame.
Friendly matches as well as some nonimportant tournaments are minor ranking events. Under normal circumstances it is recommended to give preference to this type of games as long as players try to win.

* **Non ranking**. These games do not have any affect on ratings at all. This type should be only used if players do not try to win or play not as they would normally do so that the outcome does not adequately represent their real abilities.

Too frequent minor ranking matches between the same two players (more then one in two weeks) have smaller impact on ratings (inversely proportional to the number of games).

Ratings are computed in the following way:
Default rating for a new player is 1500.
For every day the system considers all ranked games played that day, estimates an expected outcome of each game and then simultaniously adjusts players ratings according to the difference between actual results and the expectations. Victory over a strong player (whose rating is high) costs more then victory over a weak player. Winning a match 3-2 and 3-0 makes a difference.
In general, rating changes for two opponents are not symmetric. The system has a hidden parameter that represents its confidence in a player's rating. The confidence increases after every game, and decreases from the passage of time when not playing. For players who play often, their rating is considered to be more reliable and vary less then ratings of new players or those who play infrequently and whose rating is less precise.
A weak player may gain rating points winning few frames against a strong opponent, even loosing a match, and vise versa, a match winner may still lose some points if he/she defeats a weaker opponent with a close score.

Example 1. 1 September 2017. Besenval is a new player. His initial rating is 1500 and the system knows nothing about his real strenghs yet. He wins a minor ranking match against Minuto 4-1, whose rating 1745 is more trustworthy. Besenval gains +247 rating points, while Minuto looses only -46. Defeating a player with a fairly precise rating of 1743 is reasonable evidence that Basenval's strength is probably much higher than 1500. Minuto's rating should decrease by a smaller amount, because his rating is already precisely measured to be near 1745, and he lost to a player whose rating cannot be trusted, therefore little information about Minuto's playing strength has been learned from that match. New ratings appear on the following day, 2 September 2017.

Example 2. 8 November 2017. Solomko's rating is 1788, Di Marco's rating is 1652 and more reliable. Solomko wins a major ranking match 3-2. Solomko's new rating is 1774 (-14), Di Marco's new rating is 1660 (+8). Even though Solomko has won, the system thinks that the result 3-2 was closer then 1788 vs 1652 and increases Di Marco's rating by +8 points, decreasing Solomko's one by -14 points. If it was not a major but minor ranking game, the players would get twice less, +4 and -7, respectively.


The system has weak memory: current ratings depend strongly on recent games and very weakly on games played long time ago. As a result, players cannot rely on their past achievments only, but have to confirm their level constantly.

The model under consideration is probabilistic by its nature. Knowing the ratings of two players it allows to estimate the probability for each of them to win a single frame and a match. For example, in a match (best of 5) between players whose ratings are 1700 and 1650 (provided they are equally reliable) the stronger player would win with probability 62% and the distribution of possible match outcomes would be: 3-0 18%, 3-1 24%, 3-2 20%, 2-3 16%, 1-3 14%, 0-3 8%.


## Web interface

AndyScorer website provides and detailed reports on various statistics.


## F.A.Q.

**I have won the match. Why has my rating dropped?**

Changes in ratings depend not on a match outcome, but on the score (3-0 and 3-2 will cause different changes), as well as on the players ratings prior to the game. If both opponents had equal ratings before the game, the indeed winning with any score would mean getting rating points and vise versa. If however undervalued player looses a match but wins more frames than "expected" against a strong opponent, than he will still get rating points, and te winner will loose some.
Imagine your rating is 100, and Ronnie O'Sullivan's rating is 3000, and you loose 10-9. Then the system will conclude that maybe you are not so bad and he is not so good, and adjust your ratings accordingly.

Seriously speaking, the system does not see such thing as a match at all, it only cares about frames. So playing two matches 2-1 or one 4-2 will have exactly the same effect, as long as these matches are of the same type (minor or major).
