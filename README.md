# Andy Rating System

The [Andy](http://snooker.andyscorer.org) rating system is based on [Glicko](http://www.glicko.net/glicko.html) rating system with minor modifications. It assesses a player's strength as ability to win frames.

Rigorously speaking, the introduced rating system considers each player's strength being a [normally distributed random variable](en.wikipedia.org/wiki/Normal_distribution). Parameters of the distributions (mean and variance) are adjusted periodically based on the games played recently to reflect the outcomes.

#### Assumptions:
* players try to win every frame,
* frames outcomes are independent of each other.

Ratings are updated daily. Ratings on a given day are based on all finished ranked games played before that day between members of one academy (excluding "guest" players, who are not ranked).

#### Types of games

There are three different types of games depending on their effect on players ratings.

* **Major ranking**: These games have "full" impact.

* **Minor ranking**: Minor ranking games have twice smaller effect than major ranking ones, namely winning two minor frames have the very same effect on ratings than winning one major frame. Under normal circumstances it is recommended to give preference to this type of games

* **Non ranking**: These games do not have any affect on ratings at all. 

There are three types of games: "major ranking", "minor ranking" and "non-ranking", that have impacts 1, 1/2 and 0, respectively. Minor ranking games have twice smaller weight then major ranking games, i.e. one major ranking frame is equivalent to two minor ranking frames. Non-ranking games do not affect ratings at all.
Most tournaments are major ranking. Friendly matches (Amichevole), as well as some nonimportant tournaments, are minor ranking events. As a consequence, all past friendly games have some impact on current ratings. For future purposes, a non-ranking category called "Practice" was created. However, it is recommended to give preference to ranking games when possible.
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
