Gatling's SBT plugin
=========================

A simple project showing how to configure and use Gatling's SBT plugin to run Gatling simulations. 

This project uses SBT 1, which is available [here](https://www.scala-sbt.org/download.html).

Start SBT
---------
```bash
$ sbt
```

Run all simulations
-------------------

```bash
> gatling:test
```

Run a single simulation
-----------------------

```bash
> gatling:testOnly kawalc1.KawalPemiluSimulation
```

List all tasks
--------------------

```bash
> tasks gatling -v
```
