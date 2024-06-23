# Changing the background on a replay
I'm not entirely sure whether or not this will be integrated in the final log converter, but I've figured out a method of changing the background of a Showdown, and it's predicated on changing the `<input>` value for the HTML of the replay file.

### What am I looking for?

Each replay file will have a line like so:
```html
<input name="replayid" value="">
```

By changing the value of `value` (specifically, by changing the number), you can have the replay file give different backgrounds.

Though gens 1 and 2 only have 1 background (making them irrelevant for this), for gens 3 through 5, this will let you customize the backgrounds they will have.

All the images of the backgrounds are available [here](https://play.pokemonshowdown.com/fx/).

### Gen 3

| Value   | Background             |
|-------- | ---------------------- |
| 1       | bg-gen3-cave.png       |
| 2       | bg-gen3-ocean.png      |
| 3       | bg-gen3-sand.png       |
| 4       | bg-gen3-forest.png     |
| 5       | bg-gen3-arena.png      |
| 6       | bg-gen3.png            |

### Gen 4

| Value   | Background             |
|-------- | ---------------------- |
| 1       | bg-gen4-cave.png       |
| 2       | bg-gen4-snow.png       |
| 3       | bg-gen4-indoors.png    |
| 4       | bg-gen4-water.png      |
| 5       | bg-gen4.png            |

### Gen 5

| Value   | Background             |
|-------- | ---------------------- |
| 1       | bg-beachshore.png      |
| 2       | bg-desert.png          |
| 3       | bg-meadow.png          |
| 4       | bg-thunderplains.png   |
| 5       | bg-city.png            |
| 6       | bg-earthycave.png      |
| 7       | bg-mountain.png        |
| 8       | bg-volcanocave.png     |
| 9       | bg-dampcave.png        |
| 10      | bg-forest.png          |
| 11      | bg-river.png           |
| 12      | bg-deepsea.png         |
| 13      | bg-icecave.png         |
| 14      | bg-route.png           |
| 15      | bg-beach.png           |

### Smogon Premier League Backgrounds

Ordinarily, the log will insert the following line into the log:

```
|rule|Unrated|
```

If you replace this line with the following line:
```
|rated|Smogon Premier League
```
then the replay will use SPL backgrounds (which look absolutely sick) and will put a message in the replay chat that indicates that the replay is for Smogon Premier League. You may also include additional text after "Smogon Premier League", so for example:
```
|rated|Smogon Premier League IV
```
will still give the SPL background and will have a message in the chat saying "Smogon Premier League IV".

##### Extra notes

- Changing the `replayid` will also change the background music that plays. I turn music off regardless when watching replays.
- Because none of the lists use the background `bg-space.jpg`, we cannot use the space background for any replay.
