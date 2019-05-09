package id.kawalc1.clients
import akka.http.scaladsl.testkit.ScalatestRouteTest
import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1
import id.kawalc1.Report
import id.kawalc1.database.ResultsTables
import id.kawalc1.services.BlockingSupport
import org.json4s.native.Serialization
import org.scalatest.{Matchers, WordSpec}
import slick.jdbc.PostgresProfile.api._

import scala.concurrent.Future
import scala.concurrent.duration.FiniteDuration
import scala.io.Source
import scala.concurrent.duration._

class ReportsSpecs extends WordSpec with Matchers with ScalatestRouteTest with JsonSupport with BlockingSupport {
  override def duration: FiniteDuration = 1.hour

  "report" should {
    "parse" in {
      val response                               = Source.fromURL(getClass.getResource("/reports.json")).mkString
      val kelurahan                              = Serialization.read[Seq[Report]](response)
      val problems: Seq[kawalc1.ProblemReported] = kelurahan.map(Report.toProblemReported)

      val resultsDatabase = Database.forConfig("verificationResults")

      val inserts                         = problems.map(ResultsTables.problemsReportedQuery.insertOrUpdate)
      val insertSuccess: Future[Seq[Int]] = resultsDatabase.run(DBIO.sequence(inserts))
      insertSuccess.futureValue.length shouldBe 1

    }
  }

}
