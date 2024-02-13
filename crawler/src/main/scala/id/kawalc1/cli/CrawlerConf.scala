package id.kawalc1.cli

import org.rogach.scallop.{ ScallopConf, Subcommand }

class CrawlerConf(toolArgs: Seq[String]) extends ScallopConf(toolArgs) {
  import CrawlerConf._

  val Process = new Subcommand("process") {
    val phase = choice(Phases)
    val refreshToken = opt[String](required = false)
    val offset = opt[Int](required = false)
    val service = opt[String](required = false)
    val limit = opt[Int](required = false)
    val batch = opt[Int](required = false)
    val threads = opt[Int](required = false)
  }

  val Stats = new Subcommand("stats") {
    val on = choice(Seq("duplicates", "det-duplicated"))
  }

  val Submit = new Subcommand("submit") {
    val name = choice(Seq("problems", "switch", "submit"), required = true)
    val token = opt[String](required = true)
    val force = opt[Boolean](default = Some(false))
  }

  val CreateDb = new Subcommand("create-db") {
    val name = choice(Phases)
    val drop = opt[Boolean](required = false)
  }

  addSubcommand(Process)
  addSubcommand(CreateDb)
  addSubcommand(Stats)
  addSubcommand(Submit)
  verify()
}

object CrawlerConf {
  val Phases: Seq[String] =
    Seq(
      "terbalik",
      "roi",
      "problems",
      "problems-reported",
      "forms-processed",
      "test",
      "fetch",
      "align",
      "extract",
      "presidential",
      "detect",
      "submit",
      "tps-unprocessed")
}
