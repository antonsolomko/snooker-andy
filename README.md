# Andy Rating System

## Overview

The Andy rating system was designed for the [AndyScorer](http://snooker.andyscorer.org) web service to evaluate players skills in the game of [snooker](en.wikipedia.org/wiki/Snooker). 
It is based on [Glicko](http://www.glicko.net/glicko.html) rating system with minor modifications and treats players strength as their ability to win individual frames.

In our model, like in glicko, player strength is assumed to be a [normally distributed random variable](https://en.wikipedia.org/wiki/Normal_distribution). 
Parameters of the distributions (mean and variance) are reestimated periodically based on games outcomes.

The model relies on the following assumptions:
* players try to win every frame,
* frames outcomes are independent of each other.

Only *count of frames* won or lost in every pair of opponents determines the resulting ratings.
Any other factors, such as match outcome, points scored, breaks made, tournament stage etc, are not taken into account.

## Description

To each player two numbers are associated:

* **Rating**.
Represents player's strength (ability to win frames).
Initial rating for a new player is 1500.

* **Reliability** (rescaled version of variance).
This is an auxiliary parameter that represents the system's confidence in player skills estimate.
Reliability varies from -1 (default for new players) to 1. 
The higher the reliability, the more accurate the rating is considered to be. 
(Reliability 1 would mean that the system is 100% sure in player's strength, although this level of confidence can never be achieved.)

Both numbers (rating and reliability) are updated *daily* based on all ranking games played the day before.
The system estimates an expected outcome of each game and then simultaniously adjusts players ratings according to the difference between actual results and the expectations.
That is, a new rating for a given player is displayed in the system the *next day* after ranking games played by the player.
Otherwise, in case of player's inactivity, the rating value remains unchanged.

Reliability changes every day in two ways:
* Whenever ranked games are played, reliability grows (with an increment depending on many factors).
* When not playing, reliability decreases with the passage of time (by 0.008(3) every day).

The more you play, the more trustworthy your rating is.
And vise versa, long absence results in more uncertanty.

For every frame won/lost a player obtains/looses rating points.
The number of points depends on:
* *The difference between opponents ratings prior to the game*. 
This is the main factor: more "unexpected" outcomes lead to bigger rating changes. 
Player with high rating will not get much from winning on weak opponent, but if loosing to one will lose a lot. 
Similarly, low rated player gets many points from beating a stronger opponent, but looses only few points when looses a frame.
* *Players raliabilities*. 
If raliability is high (meaning that the system is quite confident in player skills), rating changes will be small.
On the contrary, the systems "knows little" about players with low reliability, and therefore any frame will result in bigger changes in ratings (the system will try to find a correct value based on little information it has about the player).
Difference in players reliabilities also matters.

#### Types of games

There are three types of games, depending on their importance and effect on ratings.

* **Major ranking**. 
These games have "full" impact on ratings. 
It is assumed that the result matters for both opponents and thus they do their best to win every frame. 
Most tournaments are major ranking.

* **Minor ranking**. 
Minor ranking games have twice smaller effect on ratings than major ranking ones. 
Rating changes for minor ranking games are "discounted" by the factor 0.5 compared to those observed after a major ranking game. 
In other words, winning two *minor* frames have the same effect on ratings than winning one *major* frame.
Friendly matches as well as some nonimportant tournaments are minor ranking events. 
Under normal circumstances it is recommended to give preference to this type of games as long as players try to win.

* **Non ranking**. 
These games do not affect ratings at all. 
This type should be only used if players do not try to win or play not as they would normally do so that the outcome does not adequately represent their real abilities.

#### Guest players

Players that are not members of an academy ("guest" players) are not ranked.
Games where unranked players take part do not affect ratings.

#### Frequecy restriction

If two players play with each other too often (more than once in two weeks), their minor ranking games impact gets additional "discount factor" inversely proportional to the number of games played within the past 14 days.

#### Official ratings

Player's rating is considered to be *official* if the reliability is positive, and *unofficial* otherwise.
This means that newcomers' ratings are initially not official and become official only after they play certain number of games (typically aroung 20).
Similarly, since reliability goes down with the passage of time, ratings of players who do not play for a long period of time or play too seldom sooner or later becomes unofficial until they renew.

#### Official rankings

Club official ranking is updated weekly based on Monday ratings.

#### Remarks

* Rating changes depend on the score. Winning a match 3-2 or 3-0 makes a (big) difference.

* Victory over a strong player (whose rating is high) "costs" more than victory over a weak player.
Similarly, loosing to a lower rated player will cause heavier rating drop than loosing to a stronger one.

* A weak player may still get rating points if he looses a match to a strong opponent but manages to win few frames (the winner will lose rating points in that case).

* Rating changes for two opponents are not symmetric in general (but are always opposite).
They depend on players reliabilities.
Low reliability results in high rating volatility, because in that case the rating is considered to be less precise and the system tries more adjustment, while high reliability means that the system is confident in the rating accuracy and only makes little changes.

* The system has weak memory: current ratings depend strongly on recent games and very weakly on games played long time ago.

### Examples

#### Example 1. 
**A** is a new player playing his first ever game. 
His initial rating is 1500 and the system knows nothing about his real strenghs yet. 
He wins a minor ranking match 4-1 against **B**, whose rating 1745 is more trustworthy. 
**A** gains +247 rating points, while **B** only looses -46. 
Defeating a player with a fairly precise rating of 1743 is reasonable evidence that **A**'s strength is probably much higher than 1500. **B**'s rating should decrease by a smaller amount, because his rating is already precisely measured to be near 1745, and he lost to a player whose rating cannot be trusted, therefore little information about **B**'s playing strength has been learned from that match.
New ratings appear on the following day.

#### Example 2. 
**A**'s rating is 1788, **B**'s rating is 1652 and more reliable.
**A** wins a major ranking match 3-2.
**A**'s new rating is 1774 (-14), while **B**'s new rating is 1660 (+8).
Even though **A** has won, the system thinks that the result 3-2 was closer then 1788 vs 1652 and increases **B**'s rating by +8 points, decreasing **A**'s one by -14 points.
If it was not a major but minor ranking game, the players would get twice less, +4 and -7, respectively.


## Probabilistic interpretation

The model under consideration is probabilistic by its nature. Knowing the ratings of two players it allows to estimate the probability for each of them to win a single frame and a match. For example, in a match (best of 5) between players whose ratings are 1700 and 1650 (provided they are equally reliable) the stronger player would win with probability 62% and the distribution of possible match outcomes would be: 3-0 18%, 3-1 24%, 3-2 20%, 2-3 16%, 1-3 14%, 0-3 8%.


## Web interface

AndyScorer website provides various detailed rating reports.

### Ratings
Ratings for a selected day (today by default)
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/snk_rating_1549395708.jpg?79537)\
with the following columns:
* *Position*. Please note that even though rounded rating values may sometimes coincide, the reaal values are almost surely different from each other, thus one position is never shared by more than one player (this is different from the previous version).
* *Player name*.
* *Rating* for a given day (based on all games played before that day).
* Last rating *change* for each player.
* *Day* when the last ranking game was played. Notice that this date is always strictly before the day for which the ratings were generated, so games played on 11/12/2017 will only appear in the next day report for 12/12/2017 with the corresponding rating changes.
* Rating *reliability*.

Only official ratings are shown by default.
Set the corresponding flag to see all ratings including unofficial ones:
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/snk_rating_1549395796.jpg?38962)

### Official ranking
Official club ranking (based on Monday ratings of the selected week, current week by default):
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/official_rating.jpg?62134)\
contains columns:
* *Position* (rank).
* *Position change* since the last week.
* *Player*.
* *Rating*.

Players whose rating is not official and who therefore are not ranked are listed in a separate table:
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/official_rating_off.jpg?86926)

### Leaders
List of official ranking leaders for every week
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/number_ones_1549398666.jpg?77396)\
and overall leaders by number of weeks holding the first plase
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/number_ones_total_1549398667.jpg?34188)

### Rating/ranking history
Record of all rating and ranking changes for a selected player:
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/player_rating_history_1549399068.jpg?13961)\
![alt text](http://snooker.andyscorer.org/snooker/tuscany/__cfg/output/generic_table/player_ranking_history_1549399068.jpg?98891)

## F.A.Q.

#### I have won the match. Why has my rating dropped?**

Changes in ratings depend on the score (3-0 and 3-2 will result in different changes), as well as on the players ratings prior to the game. 
Imagine your rating is 100, and Ronnie O'Sullivan's rating is 3000, and you loose 10-9. Then the system will conclude that probably you are not so bad and he is not so good, and adjust the ratings accordingly.
You are guaranteed to get raning points only if you:
* whitewash your opponent, or
* win (with any score) against a stronger opponent.
Otherwice make sure that you don't loose too many frames.

#### Will I get rating points for winning a match?

No, the system does not see such a thing as match at all, it only cares about frames.
The number of rating points you get depends on the frames scored, not a match result.
Basically, playing two matches 2-1 or one 4-2 will have exactly the same effect, as long as these matches are of the same type (minor or major).

#### When will I get an official rating?

When reliability of your rating becomes positive.
It usually takes about 20 frames to play with 5 different opponents, but precise number depents on the "quality" of you opponents, as well as some other factors.
Keep playing and you get your official status soon.

#### What happens to my rating if I don't play for some time?

Rating value itself will not change, but reliability will go down until eventually it hits 0 and your rating becomes *unofficial*.
In that case you will need to play some number of games before appearing at the official ranking again.

## Credits
The rating system was inspired by *Gerardo Calzerano*, designed by *Anton Solomko* and implemented by *Anton Solomko* and *Luca Gherardi*.
