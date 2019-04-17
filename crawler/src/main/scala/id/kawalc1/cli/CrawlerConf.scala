package id.kawalc1.cli

import org.rogach.scallop.{ ScallopConf, Subcommand }

class CrawlerConf(toolArgs: Seq[String]) extends ScallopConf(toolArgs) {
  import CrawlerConf._

  val Process = new Subcommand("process") {
    val phase = choice(Phases :+ "fetch")
    val offset = opt[Int](required = false)
    val batch = opt[Int](required = false)
  }

  val CreateDb = new Subcommand("create-db") {
    val name = choice(Phases)
    val drop = opt[Boolean](required = false)
  }

  addSubcommand(Process)
  addSubcommand(CreateDb)
  verify()
}

object CrawlerConf {
  val Phases: Seq[String] = Seq("fetch", "align", "extract", "presidential")

}
