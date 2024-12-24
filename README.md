# VST Prepper

## What is this?

This app will take in audio file(s) assumed to contain notes of varying pitches from a piano. (I
have only tested with my piano, and certain things are specific for piano, though you could really
modify this to be any instrument)

It will then search for a transient, determine the note, normalize, and output that as
a single file. This will be continued for all transients.

It will output a directory "outputs" which will match the input file structure if you provide it
such a structure, otherwise just the output.

## Why is this?

This is just a tool I created along with ChatGPT to automate a large portion of sampling session processing for my piano.
I sampled my piano at 4 different mic positions and all 88 keys, and it would've take far too long
to cut this myself in a meanful way. Logic pro can slice at transients, but I wanted an easy batch
way to do so on commandline, and in a more organized fashion.

## Disclaimer

This project comes with no warranty, I may updated it, and change functionality at any point.
