package id.kawalc1.cli

import org.rogach.scallop.{ ScallopConf, Subcommand }

class CrawlerConf(toolArgs: Seq[String]) extends ScallopConf(toolArgs) {
  import CrawlerConf._

  val Process = new Subcommand("process") {
    val phase = choice(Phases)
    val offset = opt[Int](required = false)
    val limit = opt[Int](required = false)
    val batch = opt[Int](required = false)
    val threads = opt[Int](required = false)
  }

  val Stats = new Subcommand("stats") {
    val on = choice(Seq("duplicates"))
  }

  val CreateDb = new Subcommand("create-db") {
    val name = choice(Phases)
    val drop = opt[Boolean](required = false)
  }

  addSubcommand(Process)
  addSubcommand(CreateDb)
  addSubcommand(Stats)
  verify()
}

object CrawlerConf {
  val Phases: Seq[String] = Seq("test", "fetch", "align", "extract", "presidential", "detect")

}
