package id.kawalc1
import id.kawalc1.cli.CrawlerConf
import org.scalatest.{Matchers, WordSpec}

class CommandLiRneSpecs extends WordSpec with Matchers {
  "CommandLine" should {
    "parse" in {
      val toolConf = new CrawlerConf(Seq("process", "-p", "align"))
      toolConf.printHelp()
      toolConf.Process.phase() shouldBe "align"
    }
  }
}
